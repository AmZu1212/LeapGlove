
"""
Corrected letter-to-finger mapping based on servo behavior:
A = Pinky
B = Thumb
C = Index
D = Middle
E = Ring
"""
import serial
import time
import random

BT_SERIAL_PORT = "COM8"
BAUD_RATE = 115200
SEND_INTERVAL = 1  # 100 ms

fingers = ['A', 'B', 'C', 'D', 'E']  # A = Pinky, B = Thumb, etc.

try:
    bt_serial = serial.Serial(BT_SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Connected to {BT_SERIAL_PORT}")

    while True:
        value = random.choice(range(0, 1100, 100))  # 0 to 1000
        command = ''.join(f"{finger}{value}" for finger in fingers)
        bt_serial.write((command + '\n').encode())
        print(f"Sent: {command}")
        time.sleep(SEND_INTERVAL)

except serial.SerialException as e:
    print(f"Serial error: {e}")

except KeyboardInterrupt:
    print("🛑 Exiting...")

finally:
    if 'bt_serial' in locals() and bt_serial.is_open:
        bt_serial.close()
