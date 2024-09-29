import os
import time
import keyboard
from dynamixel_sdk import *  # Uses Dynamixel SDK library

# Control table address
ADDR_PRO_TORQUE_ENABLE = 64
ADDR_PRO_OPERATING_MODE = 11
ADDR_PRO_GOAL_VELOCITY = 104
ADDR_PRO_PRESENT_POSITION = 132
ADDR_PRO_VELOCITY_LIMIT = 44

# Protocol version
PROTOCOL_VERSION = 2.0  # See which protocol version is used in the Dynamixel

# Default setting
BAUDRATE = 57600  # Dynamixel default baudrate : 57600
DEVICENAME = '/dev/ttyUSB0'  # Check which port is being used on your controller

TORQUE_ENABLE = 1  # Value for enabling the torque
TORQUE_DISABLE = 0  # Value for disabling the torque
WHEEL_MODE = 1  # Value for wheel mode

DXL_MOVING_STATUS_THRESHOLD = 20  # Dynamixel moving status threshold

VELOCITY_LIMIT = 1023

# Initialize PortHandler instance
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    quit()

# Enable Dynamixel Torque
def enable_torque(dxl_id):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel ID %d has been successfully connected" % dxl_id)

# Disable Dynamixel Torque
def disable_torque(dxl_id):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

# Set Wheel Mode
def set_wheel_mode(dxl_id):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_PRO_OPERATING_MODE, WHEEL_MODE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel ID %d has been set to Wheel Mode" % dxl_id)

# Write Goal Velocity
def write_goal_velocity(dxl_id, velocity):
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_PRO_GOAL_VELOCITY, velocity)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

def set_velocity_limit(dxl_id, limit):
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_PRO_VELOCITY_LIMIT, limit)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print(f"Velocity limit set to {limit} for Dynamixel ID {dxl_id}")


# Initialize all motors
motor_ids = [0, 1, 2]
for motor_id in motor_ids:
    set_velocity_limit(motor_id, VELOCITY_LIMIT)
    set_wheel_mode(motor_id)
    enable_torque(motor_id)

selected_motor = None

def on_press_key(event):
    global selected_motor
    key = event.name
    if key == '0':
        selected_motor = 0
        print("Motor 0 selected")
    elif key == '1':
        selected_motor = 1
        print("Motor 1 selected")
    elif key == '2':
        selected_motor = 2
        print("Motor 2 selected")
    elif key == 'w' and selected_motor is not None:
        print(f"Moving motor {selected_motor} forward")
        write_goal_velocity(selected_motor, 1023)  # Adjust velocity as needed
    elif key == 's' and selected_motor is not None:
        print(f"Moving motor {selected_motor} backward")
        write_goal_velocity(selected_motor, -1023)  # Adjust velocity as needed
    elif key == 'space' and selected_motor is not None:
        print(f"Stopping motor {selected_motor}")
        write_goal_velocity(selected_motor, 0)

# Listen to key events
keyboard.on_press(on_press_key)

# Keep the program running to listen to keypresses
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    # Disable torque on all motors before exiting
    for motor_id in motor_ids:
        disable_torque(motor_id)
    portHandler.closePort()
    print("Exiting program")

