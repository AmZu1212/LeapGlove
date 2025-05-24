from dynamixel_sdk import PortHandler, PacketHandler
import time

PORT_NAME = "COM5"
BAUDRATE = 4000000
PROTOCOL_VERSION = 2.0

# Degrees to Dynamixel units (assuming XL430 or similar)
def angle_to_position(angle_deg):
    return int((angle_deg / 360.0) * 4096)

# Test angles
OPEN_POS = angle_to_position(180)
CLOSE_POS = angle_to_position(270)

# Create handlers
portHandler = PortHandler(PORT_NAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

if not portHandler.openPort():
    print("❌ Failed to open port")
    exit()
if not portHandler.setBaudRate(BAUDRATE):
    print("❌ Failed to set baudrate")
    portHandler.closePort()
    exit()

# Enable torque
def enable_torque(motor_id):
    packetHandler.write1ByteTxRx(portHandler, motor_id, 64, 1)

# Write goal position
def move_motor(motor_id, position):
    packetHandler.write4ByteTxRx(portHandler, motor_id, 116, position)

# Test loop
for motor_id in range(1, 12):
    print(f"\n▶ Motor {motor_id}: enabling torque")
    enable_torque(motor_id)

    print(f"  Moving to 180° (open)")
    move_motor(motor_id, OPEN_POS)
    time.sleep(1.5)

    print(f"  Moving to 270° (closed)")
    move_motor(motor_id, CLOSE_POS)
    time.sleep(1.5)

portHandler.closePort()
print("\n✅ Test complete")
