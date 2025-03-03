###################### Imports ######################
from initialize import initialize_menu
from flask import Flask, request, jsonify
import time
import gpiozero
import gpiozero.pins.lgpio
import lgpio
from input_menu import InputMenu
from rpi_lcd import LCD
import threading
import board
import adafruit_dht

def __patched_init(self, chip=None):
    gpiozero.pins.lgpio.LGPIOFactory.__bases__[0].__init__(self)
    chip = 0
    self._handle = lgpio.gpiochip_open(chip)
    self._chip = chip
    self.pin_class = gpiozero.pins.lgpio.LGPIOPin

gpiozero.pins.lgpio.LGPIOFactory.__init__ = __patched_init

###################### GPIO Ports & Constants ######################
PIN_SW = 17 # BCM Pin numbers - WiringPi 3
PIN_DT = 27 # WPi 2
PIN_CLK = 22 # WPi 0
PIN_DHT = board.D26 # this is BCM 26
PIN_MOTION = 21 # WPi 29

TIMEOUT = 30

###################### Devices & Initilization ######################
# Hardware
lcd = LCD(width=16, rows=2)
encoder = gpiozero.RotaryEncoder(PIN_CLK, PIN_DT, bounce_time=0.01, max_steps=0, wrap=False, )
button = gpiozero.Button(PIN_SW, bounce_time=0.01, pull_up=True)
dht_sensor = adafruit_dht.DHT11(PIN_DHT)

temperature_c = dht_sensor.temperature
humidity = dht_sensor.humidity
print(f"Temp: {temperature_c}C, Humidity: {humidity}%")


motion_sensor = gpiozero.MotionSensor(PIN_MOTION) # motion sensor doesn't really work for some reason
motion_sensor.when_motion = lambda: print("Motion Detected")
motion_sensor.when_no_motion = lambda: print("No Motion Detected")

# Software
all_input_menu = InputMenu(options='all', lcd=lcd, max_input_length=14, min_input_length=1)
letters_input_menu = InputMenu(options='letters', lcd=lcd, max_input_length=14, min_input_length=1)
digit_input_menu = InputMenu(options='digits', lcd=lcd, max_input_length=1, min_input_length=1)
menu = initialize_menu(lcd=lcd, dht_sensor=dht_sensor) # initialize the LCD menu sturcture

###################### Helpers ######################
last_interaction = time.time()

def check_timeout():
    global last_interaction
    while True:
        if time.time() - last_interaction > TIMEOUT:
            menu.return_to_root_and_refresh()
            last_interaction = time.time()
            print("Timeout: Returning to root")
        time.sleep(1)

timeout_thread = threading.Thread(target=check_timeout)
timeout_thread.start()

###################### GPIOZero Event Handlers ######################
def handle_input_mode():
    if menu.input_mode == 'all':
        return all_input_menu
    elif menu.input_mode == 'digits':
        return digit_input_menu
    elif menu.input_mode == 'letters':
        return letters_input_menu

def on_rotate_clockwise():
    global last_interaction
    last_interaction = time.time()
    if menu.input_mode:
        input_menu = handle_input_mode()
        input_menu.next()
        print("Rotated clockwise: next input")
    else:
        menu.next()
        print("Rotated clockwise: next menu")
def on_rotate_counter_clockwise():
    global last_interaction
    last_interaction = time.time()
    if menu.input_mode:
        input_menu = handle_input_mode()
        input_menu.previous()
        print("Rotated counter clockwise: previous input")
    else:
        menu.prev()
        print("Rotated counter clockwise: previous menu")

encoder.when_rotated_clockwise = on_rotate_counter_clockwise
encoder.when_rotated_counter_clockwise = on_rotate_clockwise

def on_button_pressed():
    global last_interaction
    last_interaction = time.time()
    if menu.input_mode:
        input_menu = handle_input_mode()
        print("Button pressed: select input")
        value = input_menu.select()
        if value:
            menu.input_queue.append(value)
            menu.input_mode = None
            menu.select()
    else:
        print("Button pressed: select menu")
        menu.select()

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