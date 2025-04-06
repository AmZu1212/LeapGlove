import serial
import time

BT_SERIAL_PORT = "COM8"   # Replace with your port
BAUD_RATE = 115200
SEND_INTERVAL = 0.2       # Send every 200ms to keep it active

try:
    bt_serial = serial.Serial(BT_SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Connected to {BT_SERIAL_PORT} for BTSerial")

    haptic_command = "A1023B0C0D0E0\n"

    while True:
        bt_serial.write(haptic_command.encode())
        print(f"Sent: {haptic_command.strip()}")
        time.sleep(SEND_INTERVAL)

except serial.SerialException as e:
    print(f"Serial error: {e}")

except KeyboardInterrupt:
    print("🛑 Exiting...")

finally:
    if 'bt_serial' in locals() and bt_serial.is_open:
        bt_serial.close()
