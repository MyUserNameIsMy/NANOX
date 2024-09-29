from gpiozero import OutputDevice
from time import sleep

# Initialize GPIO pin 17 as the motor control pin
motor = OutputDevice(17)  # Adjust the GPIO pin as needed


motor.on()

sleep(2)
