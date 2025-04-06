import serial
import re
import time
import keyboard
import numpy as np

ESP32_PORT = "COM8"
BAUD_RATE = 115200
SEND_INTERVAL = 0.012  # ~83Hz

ENABLE_LEAPHAND = False

SERVO_TESTING = False

if ENABLE_LEAPHAND:
    from LeapHandAPI import LeapNode as BaseLeapNode
    from leap_hand_utils.dynamixel_client import *
    import leap_hand_utils.leap_hand_utils as lhu

    class LeapNode(BaseLeapNode):
        def __init__(self):
            super().__init__()  # COM5 fallback

# Allegro-style mapping: 0.0 (open) → ~4.0 (closed)
def glove_to_allegro(glove_data):
    pose = np.zeros(16)

    finger_map = {
        "Index (P)": [1, 2, 3],
        "Middle (C)": [5, 6, 7],
        "Ring (D)": [9, 10, 11],
        "Thumb (A)": [13, 14, 15]
    }

    for finger, joints in finger_map.items():
        bend = np.clip(glove_data[finger] / 100.0, 0.0, 1.0)
        # Original
        # pose[joints[0]] = bend * 1.6  # MCP
        # pose[joints[1]] = bend * 1.4  # PIP
        # pose[joints[2]] = bend * 1.0  # DIP

        # Original 2 (tighter grip)
        pose[joints[0]] = bend * 1.8  # MCP
        pose[joints[1]] = bend * 1.4  # PIP
        pose[joints[2]] = bend * 1.4  # DIP

    return pose

# Calibration globals
calibration_ranges = {
    "Thumb (A)": [float('inf'), float('-inf')],
    "Index (P)": [float('inf'), float('-inf')],
    "Middle (C)": [float('inf'), float('-inf')],
    "Ring (D)": [float('inf'), float('-inf')],
    "Pinky (E)": [float('inf'), float('-inf')],
}
calibrated = False

def calibrate(serial_conn, duration=5):
    global calibration_ranges, calibrated
    print("\n🛠️ Starting calibration... Move fingers through full range.")
    start_time = time.time()
    while time.time() - start_time < duration:
        if serial_conn.in_waiting > 0:
            raw_data = serial_conn.readline().decode('utf-8').strip()
            data = parse_raw_data(raw_data)
            if data:
                for key in calibration_ranges:
                    value = data[key]
                    if value < 10000:  # sanity
                        calibration_ranges[key][0] = min(calibration_ranges[key][0], value)
                        calibration_ranges[key][1] = max(calibration_ranges[key][1], value)
    calibrated = True
    print("\n✅ Calibration complete:")
    for key, (min_val, max_val) in calibration_ranges.items():
        print(f"  {key}: Min={min_val}, Max={max_val}, Range={max_val - min_val:.1f}")

def parse_raw_data(raw_data):
    pattern = r"A(\d+)B(\d+)C(\d+)D(\d+)E(\d+)F(\d+)G(\d+)P(\d+)(.*)"
    match = re.match(pattern, raw_data)
    if match:
        return {
            "Thumb (A)": int(match.group(1)),
            "Index (P)": int(match.group(8)),
            "Middle (C)": int(match.group(3)),
            "Ring (D)": int(match.group(4)),
            "Pinky (E)": int(match.group(5)),
        }
    return None

def parse_and_print_data(raw_data):
    global calibration_ranges, calibrated
    data = parse_raw_data(raw_data)
    if data:
        if calibrated:
            output = {}
            for key, value in data.items():
                min_val, max_val = calibration_ranges[key]
                if max_val - min_val >= 5:
                    percentage = ((value - min_val) / (max_val - min_val)) * 100
                    output[key] = max(0, min(100, percentage))
                else:
                    output[key] = 0
                print(f"{key}: {output[key]:.1f}%", end="  ")
            print(end="\r", flush=True)
            return output
        else:
            print(f"\rCalibration not done. Raw data: {raw_data}       ", end='', flush=True)
    return None

try:
    esp32_serial = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Connected to {ESP32_PORT}")

    leap_node = None
    if ENABLE_LEAPHAND:
        leap_node = LeapNode()
        print("🤖 LEAP Hand initialized")

    last_send_time = time.time()
    latest_glove_data = None

    while True:
        if keyboard.is_pressed('shift+c'):
            calibrate(esp32_serial)
            time.sleep(0.5)

        if esp32_serial.in_waiting > 0:
            raw_data = esp32_serial.readline().decode('utf-8').strip()
            latest_glove_data = parse_and_print_data(raw_data)

        now = time.time()
        if ENABLE_LEAPHAND and calibrated and latest_glove_data and (now - last_send_time) >= SEND_INTERVAL:
            pose = glove_to_allegro(latest_glove_data)
            #print(f"\n🎯 Allegro pose: {np.round(pose, 2)}")
            leap_node.set_allegro(pose)
            last_send_time = now

except serial.SerialException as e:
    print(f"Serial Error: {e}")

except KeyboardInterrupt:
    print("\n🛑 Exiting...")

finally:
    if 'esp32_serial' in locals() and esp32_serial.is_open:
        esp32_serial.close()
