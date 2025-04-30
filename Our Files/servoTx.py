import serial
import time

BT_SERIAL_PORT = "COM8"   # Replace with your actual port
BAUD_RATE = 115200
SEND_INTERVAL = 2       # 500ms between each action


"""
currently the mapping is:
A = thumb
B = Ring finger
C = Pinky finger
D = Middle finger
E = Index finger


The mapping is not correct, not sure why yet.


But regardless this serves as an example of how to send commands to the glove.
"""

try:
    bt_serial = serial.Serial(BT_SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Connected to {BT_SERIAL_PORT}")

    fingers = ['A', 'B', 'C', 'D', 'E']  # Thumb → Pinky
    brake_strength = 600                # 60% brake
    rest = 'A0B0C0D0E0'                 # All fingers at rest

    while True:
        for finger in fingers:
            # Step 1: Set current finger to active value
            parts = []
            for f in fingers:
                if f == finger:
                    parts.append(f + str(brake_strength))
                else:
                    parts.append(f + '0')
            command = ''.join(parts) + '\n'
            bt_serial.write(command.encode())
            print(f"Sent: {command.strip()}")
            time.sleep(SEND_INTERVAL)

            # Step 2: Return to rest
            command = rest + '\n'
            bt_serial.write(command.encode())
            print(f"Sent: {command.strip()}")
            time.sleep(SEND_INTERVAL)

except serial.SerialException as e:
    print(f"Serial error: {e}")

except KeyboardInterrupt:
    print("🛑 Exiting...")

finally:
    if 'bt_serial' in locals() and bt_serial.is_open:
        bt_serial.close()
