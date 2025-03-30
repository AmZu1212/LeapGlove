from dynamixel_sdk import PortHandler, PacketHandler

# Setup
PORT_NAME = "COM5"
BAUDRATE = 4000000  # Try other values if needed
PROTOCOL_VERSION = 2.0  # Most Dynamixel servos use 2.0

# Create handlers
portHandler = PortHandler(PORT_NAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if not portHandler.openPort():
    print("❌ Failed to open port")
    exit()
print("✅ Port opened")

# Set baudrate
if not portHandler.setBaudRate(BAUDRATE):
    print("❌ Failed to set baudrate")
    portHandler.closePort()
    exit()
print(f"✅ Baudrate set to {BAUDRATE}")

# Ping motor IDs (adjust range)
for motor_id in range(1, 12):
    dxl_model_number, dxl_comm_result, dxl_error = packetHandler.ping(portHandler, motor_id)
    if dxl_comm_result == 0:
        print(f"✅ Motor {motor_id} found! Model number: {dxl_model_number}")
    else:
        print(f"❌ No response from ID {motor_id}")

portHandler.closePort()
