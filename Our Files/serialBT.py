import serial

# Replace 'COM5' with your ESP32's serial port
ESP32_PORT = "COM5"
BAUD_RATE = 115200

try:
    # Open serial connection
    esp32_serial = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {ESP32_PORT}")
    
    while True:
        # Read data from the ESP32
        if esp32_serial.in_waiting > 0:
            data = esp32_serial.readline().decode('utf-8').strip()
            print(f"Received: {data}")

except serial.SerialException as e:
    print(f"Error: {e}")

except KeyboardInterrupt:
    print("Exiting...")

finally:
    if 'esp32_serial' in locals() and esp32_serial.is_open:
        esp32_serial.close()
