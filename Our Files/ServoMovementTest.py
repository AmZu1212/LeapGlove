import serial
import time

BT_SERIAL_PORT = "COM8"   # Replace with your actual port
BAUD_RATE = 115200
SEND_INTERVAL = 0.1      # Seconds between each phase, don’t go below 1

"""
Corrected letter-to-finger mapping based on servo behavior:
A = Pinky
B = Thumb
C = Index
D = Middle
E = Ring
"""

try:
    bt_serial = serial.Serial(BT_SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Connected to {BT_SERIAL_PORT}")

    commands = [
        'A0B0C0D0E0',
      #  'A500B0C0D0E0',
       # 'A500B500C0D0E0',
       # 'A500B500C500D0E0',
       # 'A500B500C500D500E0',
        'A1000B1000C1000D1000E1000',
       # 'A500B500C500D500E0',
       # 'A500B500C500D0E0',
        #'A500B500C0D0E0',
       #'A500B0C0D0E0',
        'A0B0C0D0E0'
    ]

    for command in commands:
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
