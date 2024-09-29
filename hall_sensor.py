from gpiozero import InputDevice
from time import sleep

# Initialize the Hall sensor connected to GPIO 8
sensor = InputDevice(4)

# Counter variable to keep track of activations
activation_count = 0

# Variable to track the previous state of the sensor
previous_state = False

while True:
    current_state = sensor.is_active
    
    # Check for a change from inactive to active state
    if current_state and not previous_state:
        activation_count += 1
        print(f"Magnet Detected! Count: {activation_count}")
    
    # Update the previous state
    previous_state = current_state
    
    sleep(0.1)  # Adjust the sleep time as needed for your application

