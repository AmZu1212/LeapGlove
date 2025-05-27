# --- Dependencies ---
# Install these with pip if not already present:
#   pip install pyserial keyboard numpy
# The 're' and 'time' modules are built-in with Python and require no installation.

import serial    # pip install pyserial
import re        # built-in, no install needed
import time      # built-in, no install needed
import keyboard  # pip install keyboard
import numpy as np  # pip install numpy



# ============== LeapGlove.py ===============
# === Written by Amir Zuabi & Liz Dushkin ===


# === Serial/Bluetooth and timing config ===
ESP32_PORT = "COM8"          # The Bluetooth port the LucidGlove ESP32 is enumerated to, change as needed (check your device manager)
BAUD_RATE = 115200           # Serial communication speed
SEND_INTERVAL = 0.012        # How often to send hand pose updates (to LeapHand), ~83Hz
SERVO_UPDATE_INTERVAL = 2.0  # How often to read current/load from LeapHand servos (dont go below 1 sec, unstable)

ENABLE_LEAPHAND = True       # Toggle LeapHand (robotic hand) integration

# === HAPTICS: Preset commands for the glove (for haptic feedback, i.e., servo braking) ===
servo_zero_command = "A0B0C0D0E0\n"   # Command to release all servos (no haptic resistance)
# Predefined brake strengths (0-1000) for each finger in "ball_hold" grip mode
haptic_presets = {
    "ball_hold": {
        "Thumb (A)": 700,
        "Index (P)": 700,
        "Middle (C)": 700,
        "Ring (D)": 700,
        "Pinky (E)": 700
    }
}

# --- LEAPHAND API setup (if enabled) ---
if ENABLE_LEAPHAND:
    from LeapHandAPI import LeapNode as BaseLeapNode
    from leap_hand_utils.dynamixel_client import *
    import leap_hand_utils.leap_hand_utils as lhu

    class LeapNode(BaseLeapNode):
        # Subclass for future extension; currently just calls parent constructor
        def __init__(self):
            super().__init__()  # Uses default serial port for LeapHand

# === Utility: Convert glove finger data to Allegro pose format (for LeapHand) ===
def glove_to_allegro(glove_data):
    pose = np.zeros(16)  # Allegro expects a 16-joint vector (4 fingers × 4 joints)
    # Mapping glove finger keys to Allegro joint indices
    finger_map = {
        "Index (P)": [1, 2, 3],
        "Middle (C)": [5, 6, 7],
        "Ring (D)": [9, 10, 11],
        "Thumb (A)": [13, 14, 15]
    }
    for finger, joints in finger_map.items():
        bend = np.clip(glove_data[finger] / 100.0, 0.0, 1.0)  # Convert percent to 0-1
        # Scale joint angles (empirically tuned for Allegro/LeapHand)
        pose[joints[0]] = bend * 1.8
        pose[joints[1]] = bend * 1.4
        pose[joints[2]] = bend * 1.4
    return pose

# === Utility: Read and process servo currents from LeapHand ===
def get_finger_currents(leap_node, idle_current=0.05, contact_threshold=1.3):
    try:
        # Read raw current sensor values
        raw_vals = leap_node.read_cur()
        # Convert to amperes using scaling factor
        current_vals = [val * 0.00269 for val in raw_vals]
        # Sometimes Thumb sensor is broken; patch value with Pinky if needed
        if current_vals[0] < 0.005:
            current_vals[0] = abs(current_vals[4])
        print(f"🔧 raw read_cur(): {raw_vals}")
        print(f"📏 type: {type(current_vals)}, length: {len(current_vals)}")
    except Exception as e:
        print(f"❌ Failed to read currents: {e}")
        # Return zeros for all fingers if reading failed
        return {k: 0 for k in ["Thumb (A)", "Index (P)", "Middle (C)", "Ring (D)", "Pinky (E)"]}

    # Convert currents to a 0-1000 brake/load value, ignoring idle noise
    def scale(val):
        excess = max(0.0, abs(val) - idle_current)
        range_current = contact_threshold - idle_current
        return min(int((excess / range_current) * 1000), 1000)

    # Print currents for debugging
    print("🔎 Raw Currents:")
    print(f"  Thumb={current_vals[0]:.2f} A, Index={current_vals[1]:.2f} A, Middle={current_vals[2]:.2f} A, Ring={current_vals[3]:.2f} A")

    # Map current values to finger names and scale
    currents = {
        "Thumb (A)": scale(current_vals[0]),
        "Index (P)": scale(current_vals[1]),
        "Middle (C)": scale(current_vals[2]),
        "Ring (D)": scale(current_vals[3]),
        "Pinky (E)": scale(current_vals[3])  # Pinky uses same sensor as Ring (for 4-finger hand)
    }
    return currents

# === Calibration state: min/max analog values for each finger ===
calibration_ranges = {
    "Thumb (A)": [float('inf'), float('-inf')],
    "Index (P)": [float('inf'), float('-inf')],
    "Middle (C)": [float('inf'), float('-inf')],
    "Ring (D)": [float('inf'), float('-inf')],
    "Pinky (E)": [float('inf'), float('-inf')],
}
calibrated = False  # Flag for calibration

# === Calibrate glove sensor ranges ===
def calibrate(serial_conn, duration=5):
    """
    Runs a 5s loop to find min/max for each finger. User should move all fingers
    through their full range during calibration.
    """
    global calibration_ranges, calibrated
    print("\n🛠️ Starting calibration... Move fingers through full range.")
    start_time = time.time()
    while time.time() - start_time < duration:
        if serial_conn.in_waiting > 0:
            raw_data = serial_conn.readline().decode('utf-8').strip()
            data = parse_raw_data(raw_data)
            if data:
                # Update min/max per finger if sample is valid
                for key in calibration_ranges:
                    value = data[key]
                    if value < 10000:  # Ignore outliers/glitches
                        calibration_ranges[key][0] = min(calibration_ranges[key][0], value)
                        calibration_ranges[key][1] = max(calibration_ranges[key][1], value)
    calibrated = True
    print("\n✅ Calibration complete:")
    for key, (min_val, max_val) in calibration_ranges.items():
        print(f"  {key}: Min={min_val}, Max={max_val}, Range={max_val - min_val:.1f}")

# === Parse raw serial glove data into a dict of finger values ===
def parse_raw_data(raw_data):
    """
    Expects string like: 'A0000B0000C0000D0000E0000F0000G0000P0000'
    The group mapping depends on hardware wiring.
    Returns a mapping of logical finger names to integer values.
    """
    pattern = r"A(\d+)B(\d+)C(\d+)D(\d+)E(\d+)F(\d+)G(\d+)P(\d+)(.*)"
    match = re.match(pattern, raw_data)
    if match:
        # Parse fields by index
        raw = {
            "Thumb (A)": int(match.group(1)),
            "Index (P)": int(match.group(8)),
            "Middle (C)": int(match.group(3)),
            "Ring (D)": int(match.group(4)),
            "Pinky (E)": int(match.group(5)),
        }
        # Remap values for correct logical finger order (hardware mapping quirk)
        return {
            "Thumb (A)": raw["Pinky (E)"],
            "Index (P)": raw["Ring (D)"],
            "Middle (C)": raw["Middle (C)"],
            "Ring (D)": raw["Index (P)"],
            "Pinky (E)": raw["Thumb (A)"],
        }
    return None

# === Use calibration to convert raw finger values to 0–100% and print ===
def parse_and_print_data(raw_data):
    """
    Reads and prints glove data as percentages if calibrated.
    Returns dictionary of {finger: percent} if data is valid.
    """
    global calibration_ranges, calibrated
    data = parse_raw_data(raw_data)
    if data:
        if calibrated:
            output = {}
            for key, value in data.items():
                min_val, max_val = calibration_ranges[key]
                if max_val - min_val >= 5:  # Ignore bad calibration
                    percentage = ((value - min_val) / (max_val - min_val)) * 100
                    output[key] = max(0, min(100, percentage))  # Clamp to 0-100
                else:
                    output[key] = 0
                print(f"{key}: {output[key]:.1f}%", end="  ")
            print(end="\r", flush=True)
            return output
        else:
            print(f"\rCalibration not done. Raw data: {raw_data}       ", end='', flush=True)
    return None

# === Main loop: Glove-robot integration ===
try:
    # Open serial connection to glove
    esp32_serial = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Connected to {ESP32_PORT}")

    # Initialize LeapHand if enabled
    leap_node = None
    if ENABLE_LEAPHAND:
        leap_node = LeapNode()
        print("🤖 LEAP Hand initialized")

        # Test current sensor connection on LeapHand
        print("🔍 Testing leap_node.read_cur()...")
        try:
            current_vals = leap_node.read_cur()
            print(f"✅ read_cur() success: {current_vals}")
        except Exception as e:
            print(f"❌ read_cur() failed: {e}")

    # --- Main loop state ---
    last_send_time = time.time()
    last_servo_update_time = time.time()
    latest_glove_data = None  # Latest glove values (percentages, post-calibration)

    while True:
        # === Keyboard Controls ===
        if keyboard.is_pressed('shift+c'):
            calibrate(esp32_serial)
            time.sleep(0.5)  # Debounce

        if keyboard.is_pressed('shift+z'):
            print("\n🔧 Zeroing all servos...")
            esp32_serial.write(servo_zero_command.encode())
            time.sleep(0.5)

        # Apply ball-hold preset on 'b' press
        if keyboard.is_pressed('b'):
            print("\n🖐️ Activating ball-hold preset...")
            preset = haptic_presets["ball_hold"]
            # Map logical finger values to correct servo letter order
            command = (
                f"A{preset['Pinky (E)']}"
                f"B{preset['Thumb (A)']}"
                f"C{preset['Index (P)']}"
                f"D{preset['Middle (C)']}"
                f"E{preset['Ring (D)']}\n"
            )
            esp32_serial.write(command.encode())
            print(f"→ Sent: {command.strip()}")
            time.sleep(0.5)
        # Manual preset strengths 0–9: send same value to all servos
        for i in range(10):
            if keyboard.is_pressed(str(i)):
                strength = i * 100  # 0–900
                print(f"\n🖐️ Activating haptic preset {i} ({strength} brake)...")
                command = f"A{strength}B{strength}C{strength}D{strength}E{strength}\n"
                esp32_serial.write(command.encode())
                print(f"→ Sent: {command.strip()}")
                time.sleep(0.5)
                break

        # === Read glove data and print finger bend ===
        if esp32_serial.in_waiting > 0:
            raw_data = esp32_serial.readline().decode('utf-8').strip()
            latest_glove_data = parse_and_print_data(raw_data)

        now = time.time()
        # === Send hand pose to LeapHand, and read servo load, at specified intervals ===
        if ENABLE_LEAPHAND and calibrated and latest_glove_data:
            if (now - last_send_time) >= SEND_INTERVAL:
                pose = glove_to_allegro(latest_glove_data)
                leap_node.set_allegro(pose)
                last_send_time = now

            if (now - last_servo_update_time) >= SERVO_UPDATE_INTERVAL:
                brake_values = get_finger_currents(leap_node)
                print(f"\n🔧 LOAD: Thumb={brake_values['Thumb (A)']}  Index={brake_values['Index (P)']}  Middle={brake_values['Middle (C)']}  Ring={brake_values['Ring (D)']}  Pinky={brake_values['Pinky (E)']}")
                last_servo_update_time = now

except serial.SerialException as e:
    print(f"Serial Error: {e}")

except KeyboardInterrupt:
    print("\n🛑 Exiting...")

finally:
    if 'esp32_serial' in locals() and esp32_serial.is_open:
        esp32_serial.close()
