from initialize import initialize_menu
from flask import Flask, request, jsonify
import time
import gpiozero
import gpiozero.pins.lgpio
import lgpio
# import threading

def __patched_init(self, chip=None):
    gpiozero.pins.lgpio.LGPIOFactory.__bases__[0].__init__(self)
    chip = 0
    self._handle = lgpio.gpiochip_open(chip)
    self._chip = chip
    self.pin_class = gpiozero.pins.lgpio.LGPIOPin

gpiozero.pins.lgpio.LGPIOFactory.__init__ = __patched_init

menu = initialize_menu() # initialize the LCD menu sturcture

# Rotary Encoder Pins
PIN_SW = 22 # BCM Pin numbers - WiringPi 3
PIN_DT = 27 # WPi 2
PIN_CLK = 17 # WPi 0

# TODO: This should be replaced by a function that checks the rotary encoder, use WiringPi Pin 3 for SW (button press), Pin 2 for DT and Pin 0 for CLK
# TODO: You may need to use threading to handle the rotary encoder (so it won't block the main thread)
# GPIOZero handles events in the background automatically
encoder = gpiozero.RotaryEncoder(PIN_CLK, PIN_DT, bounce_time=0.01, max_steps=0, wrap=False, )
button = gpiozero.Button(PIN_SW, bounce_time=0.01, pull_up=True)

def on_rotate_clockwise():
    menu.next()
    print("Rotated clockwise: next menu")
def on_rotate_counter_clockwise():
    menu.prev()
    print("Rotated counter-clockwise: previous menu")

encoder.when_rotated_clockwise = on_rotate_clockwise
encoder.when_rotated_counter_clockwise = on_rotate_counter_clockwise

def on_button_pressed():
    menu.select()
    print("Button pressed: select menu")

button.when_pressed = on_button_pressed

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    menu.clear()
    print("Clearing the screen and exiting program.")

# Do not implement code to communicate with IR here. Put it as a customize function in initialize.py










# Start the flask app and handle API requests, Do not implement yet
# app = Flask(__name__)