# Import necessary modules
import time
from dynamixel_sdk import *  # Uses Dynamixel SDK library
from flask import Flask, render_template, jsonify, request
from waitress import serve
import logging

# Dynamixel Control Table addresses and protocol settings
ADDR_PRO_TORQUE_ENABLE = 64
ADDR_PRO_OPERATING_MODE = 11
ADDR_PRO_GOAL_POSITION = 116
ADDR_PRO_PRESENT_POSITION = 132
ADDR_PRO_VELOCITY_LIMIT = 44

PROTOCOL_VERSION = 2.0  # Protocol version used by the Dynamixel
BAUDRATE = 57600  # Default baudrate
DEVICENAME = '/dev/ttyUSB0'  # Port to which the Dynamixels are connected

TORQUE_ENABLE = 1
TORQUE_DISABLE = 0
EXTENDED_POSITION_MODE = 4
VELOCITY_LIMIT = 1023

# Initialize PortHandler and PacketHandler instances
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port and set baudrate
if not portHandler.openPort():
    print("Failed to open the port")
    quit()

if not portHandler.setBaudRate(BAUDRATE):
    print("Failed to change the baudrate")
    quit()

# Flask application setup
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("app.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Motor IDs and initial setup
motor_ids = [0, 1, 2]
for motor_id in motor_ids:
    packetHandler.write4ByteTxRx(portHandler, motor_id, ADDR_PRO_VELOCITY_LIMIT, VELOCITY_LIMIT)
    packetHandler.write1ByteTxRx(portHandler, motor_id, ADDR_PRO_OPERATING_MODE, EXTENDED_POSITION_MODE)
    packetHandler.write1ByteTxRx(portHandler, motor_id, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)

# Flask routes
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/hydrogel', methods=["POST"])
def make_hydrogel():
    data = request.get_json()
    logger.info(f"Form submitted with data: {data}")

    # Move each motor based on the data received
    for item in data:
        motor_id = int(item.get('motor'))-1
        grams = int(item.get('amount', 0))
        if motor_id in motor_ids:
            move_motor_by_grams(motor_id, grams)
        else:
            logger.error(f"Invalid motor ID {motor_id}")

    return jsonify({"message": "Data received", "data": data}), 200

# Function to map grams to degrees and move motor
def move_motor_by_grams(motor_id, grams):
    # Simple mapping example: 1 gram = 2 degrees (adjust this mapping based on actual calibration)
    degrees = grams_to_degrees(grams)
    current_position = get_current_position(motor_id)
    new_position = current_position + degrees_to_position(degrees)

    logger.info(f"Moving motor {motor_id} to {new_position} (adding {degrees} degrees) for {grams} grams")
    write_goal_position(motor_id, new_position)

# Function to convert grams to degrees
def grams_to_degrees(grams):
    # Adjust the conversion factor based on your calibration (e.g., 1 gram = 2 degrees)
    conversion_factor =1500
    return grams * conversion_factor

# Function to convert degrees to position value for Dynamixel
def degrees_to_position(degrees):
    # Assuming a full rotation (360 degrees) corresponds to the full range of Dynamixel's position values (0-4095)
    position_value = int((degrees / 360) * 4095)
    return position_value

# Function to get the current position of the motor
def get_current_position(dxl_id):
    dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, dxl_id, ADDR_PRO_PRESENT_POSITION)
    if dxl_comm_result != COMM_SUCCESS:
        logger.error("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        return 0
    elif dxl_error != 0:
        logger.error("%s" % packetHandler.getRxPacketError(dxl_error))
        return 0
    else:
        return dxl_present_position

# Function to write goal position to a motor
def write_goal_position(dxl_id, position):
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_PRO_GOAL_POSITION, position)
    if dxl_comm_result != COMM_SUCCESS:
        logger.error("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        logger.error("%s" % packetHandler.getRxPacketError(dxl_error))

# Start the server
if __name__ == "__main__":
    try:
        serve(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        for motor_id in motor_ids:
            packetHandler.write1ByteTxRx(portHandler, motor_id, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
        portHandler.closePort()
        print("Exiting program")

