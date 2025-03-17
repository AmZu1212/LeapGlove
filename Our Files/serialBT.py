import serial
import re
import time
import keyboard  # Install with `pip install keyboard`

from LeapHandAPI import LeapNode  # Import LEAP Hand control class
from leap_hand_utils.dynamixel_client import *
import leap_hand_utils.leap_hand_utils as lhu
import numpy as np

# Replace 'COM8' with your ESP32's serial port
ESP32_PORT = "COM8"
BAUD_RATE = 115200

# Delay between updates, in seconds (~83 Hz, safely under 90 Hz)
UPDATE_DELAY = 0.012  

ENABLE_HAPTIC_FEEDBACK = False
ENABLE_LEAPHAND = False

# Converts finger 0-100% to leaphand joint angles
def glove_to_leap(glove_data):
    min_angle = 90   # Fully closed
    max_angle = 180  # Fully open

    # Default all joints to fully open (180°)
    leap_pose = np.full(16, 180)

    # Map glove values (0-100%) → LEAP Hand joints
    finger_map = {
        "Index (P)": [1, 2, 3],   # MCP Forward, PIP, DIP
        "Middle (C)": [5, 6, 7],  # MCP Forward, PIP, DIP
        "Ring (D)": [9, 10, 11],  # MCP Forward, PIP, DIP
        "Thumb (A)": [13, 14, 15] # MCP Forward, PIP, DIP
    }

    for finger, joints in finger_map.items():
        bend_value = glove_data[finger] / 100  # Normalize 0-1

        # Distribute bend values across joints
        leap_pose[joints[0]] = max_angle - (bend_value * (max_angle - min_angle) * 0.40)  # MCP (40%)
        leap_pose[joints[1]] = max_angle - (bend_value * (max_angle - min_angle) * 0.35)  # PIP (35%)
        leap_pose[joints[2]] = max_angle - (bend_value * (max_angle - min_angle) * 0.25)  # DIP (25%)

    return leap_pose


# Global variables for calibration
calibration_ranges = {
    "Thumb (A)": [float('inf'), float('-inf')],  # [min, max]
    "Index (P)": [float('inf'), float('-inf')],
    "Middle (C)": [float('inf'), float('-inf')],
    "Ring (D)": [float('inf'), float('-inf')],
    "Pinky (E)": [float('inf'), float('-inf')],
}
calibrated = False  # Flag to check if calibration is done

def calibrate(serial_conn, duration=5):
    
    # Calibrates the system by observing min and max values for each finger over `duration` seconds.
    
    global calibration_ranges, calibrated

    print("\nStarting calibration... Move fingers through full range.")
    start_time = time.time()

    while time.time() - start_time < duration:
        if serial_conn.in_waiting > 0:
            raw_data = serial_conn.readline().decode('utf-8').strip()
            data = parse_raw_data(raw_data)
            if data:
                for key in calibration_ranges.keys():
                    value = data[key]
                    calibration_ranges[key][0] = min(calibration_ranges[key][0], value)  # Update min
                    calibration_ranges[key][1] = max(calibration_ranges[key][1], value)  # Update max

    calibrated = True
    print("\nCalibration complete! Ranges:")
    for key, (min_val, max_val) in calibration_ranges.items():
        print(f"  {key}: Min={min_val}, Max={max_val}")

def parse_raw_data(raw_data):
    
    #Parses the raw data string and returns a dictionary with values for each finger.
    
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
    
    #Parses and prints percentage data based on calibrated ranges.
    
    global calibration_ranges, calibrated

    data = parse_raw_data(raw_data)
    if data:
        if calibrated:
            # Calculate percentages
            output = {}
            for key, value in data.items():
                min_val, max_val = calibration_ranges[key]
                if max_val > min_val:  # Avoid division by zero
                    percentage = ((value - min_val) / (max_val - min_val)) * 100
                    output[key] = max(0, min(100, percentage))  # Clamp between 0-100%
                else:
                    output[key] = 0  # Default to 0% if invalid range

            # Print percentages
            percentages = "  ".join([f"{key}: {output[key]:.1f}%" for key in output])
            print(f"\r{percentages}      ", end='', flush=True)
        else:
            # Print raw data with padding to overwrite leftovers
            print(f"\rCalibration not done. Raw data: {raw_data}          ", end='', flush=True)

try:
    # Open serial connection
    esp32_serial = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {ESP32_PORT}")

    # Initialize the robotic hand
    leap_node = LeapNode()  
    print(f"Initialized LeapHand")

    while True:
        # Check for Shift+C to trigger calibration
        if keyboard.is_pressed('shift+c'):
            calibrate(esp32_serial)
            time.sleep(0.5)  # Debounce to avoid multiple triggers

        # Read data from the ESP32 and print percentages
        if esp32_serial.in_waiting > 0:
            raw_data = esp32_serial.readline().decode('utf-8').strip()
            glove_data = parse_and_print_data(raw_data)  # Convert raw sensor data to percentages (0-100%)

            if glove_data and ENABLE_LEAPHAND:  # Only process if both conditions are True
                pose = glove_to_leap(glove_data)  # Convert glove values to LEAP Hand angles
                leap_node.set_leap(pose)  # Send movement command

            # figure out a update delay thingy ******* amzu
            #time.sleep(UPDATE_DELAY)  # Maintain ~83 Hz update rate

except serial.SerialException as e:
    print(f"Error: {e}")

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    if 'esp32_serial' in locals() and esp32_serial.is_open:
        esp32_serial.close()
