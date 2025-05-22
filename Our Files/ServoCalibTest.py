import serial
import time

BT_SERIAL_PORT = "COM8"   # Replace with your actual port
BAUD_RATE = 115200
SEND_INTERVAL = 2  # Time to wait between sending commands

"""
currently the mapping is:
A = thumb
B = Pinky finger
C = Ring finger
D = Middle finger
E = Index finger

This script sends all fingers to position 1000, waits, then sends them to 0.
"""

try:
    bt_serial = serial.Serial(BT_SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Connected to {BT_SERIAL_PORT}")

    # Step 1: Extend all servos (CCW)
    extend_command = 'A300B300C300D300E300\n'
    bt_serial.write(extend_command.encode())
    print(f"🔧 Sent: {extend_command.strip()}")
    time.sleep(SEND_INTERVAL)

    # Step 2: Retract all servos (CW)
    retract_command = 'A0B0C0D0E0\n'
    bt_serial.write(retract_command.encode())
    print(f"🔁 Sent: {retract_command.strip()}")
    time.sleep(SEND_INTERVAL)

    print("\n✅ Calibration sequence complete.")

except serial.SerialException as e:
    print(f"Serial error: {e}")

except KeyboardInterrupt:
    print("🛑 Exiting...")

finally:
    if 'bt_serial' in locals() and bt_serial.is_open:
        bt_serial.close()
