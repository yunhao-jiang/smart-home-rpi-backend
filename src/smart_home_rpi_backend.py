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
from anytree.search import findall
import ctypes

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
# PIN_DHT = board.D26 # this is BCM 26
PIN_DHT = board.D4 # BCM 4
# PIN_MOTION = 21 # WPi 29
PIN_MOTION = 10
PIN_LED = 21

TIMEOUT = 30

###################### Devices & Initilization ######################
# CPU
freq_lib = ctypes.CDLL("./src/libgovernor.so")
freq_lib.init_userspace_governor.restype = None
freq_lib.set_by_max_freq.restype = None
freq_lib.set_by_min_freq.restype = None
freq_lib.get_cur_freq.restype = ctypes.c_int
freq_lib.init_userspace_governor()
current_freq = freq_lib.get_cur_freq()
freq_lib.set_by_min_freq()
current_freq = freq_lib.get_cur_freq()

# Hardware
lcd = LCD(width=16, rows=2)
encoder = gpiozero.RotaryEncoder(PIN_CLK, PIN_DT, bounce_time=0.01, max_steps=0, wrap=False, )
button = gpiozero.Button(PIN_SW, bounce_time=0.01, pull_up=True)
dht_sensor = adafruit_dht.DHT11(PIN_DHT)
led = gpiozero.LED(PIN_LED)
led.on()

try: 
    temperature_c = dht_sensor.temperature
    humidity = dht_sensor.humidity
    print(f"Temp: {temperature_c}C, Humidity: {humidity}%")
except Exception as e:
    print(e)


motion_sensor = gpiozero.MotionSensor(PIN_MOTION) 
motion_sensor.when_motion = lambda: print("Motion Detected")
motion_sensor.when_no_motion = lambda: print("No Motion Detected")

# Software
all_input_menu = InputMenu(options='all', lcd=lcd, max_input_length=14, min_input_length=1)
letters_input_menu = InputMenu(options='letters', lcd=lcd, max_input_length=14, min_input_length=1)
digit_input_menu = InputMenu(options='digits', lcd=lcd, max_input_length=1, min_input_length=1)
menu = initialize_menu(lcd=lcd, dht_sensor=dht_sensor, led=led, motion_sensor=motion_sensor) # initialize the LCD menu sturcture

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

timeout_thread = threading.Thread(target=check_timeout, daemon=True)
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


class InteractableInfo(object):
    def __init__(self, id, displayName, type, readin, action=None, action_args=None):
        self.id = id
        self.displayName = displayName
        self.type = type
        self.readin = readin
        self.action = action
        self.action_args = action_args
    def base_to_dict(self):
        return {"id": self.id, "displayName": self.displayName, "type": self.type}

def find_menu_node(name):
    global menu
    node_list = findall(menu.root, filter_=lambda menu_node: menu_node.name==name)
    return node_list[0]

def read_humidity():
    try:
        humidity = dht_sensor.humidity
    except Exception as e:
        print(e)
        humidity = 0
    return {"humidity": humidity}

def read_temperature():
    try:
        temperature_c = dht_sensor.temperature
    except Exception as e:
        print(e)
        temperature_c = 0
    return {"temperature": temperature_c}

def read_motion_sensor():
    return {"motion": motion_sensor.motion_detected}

def toggle_led():
    led.toggle()
    return None
    

sensor_info = [
    InteractableInfo(0, displayName="Humidity Sensor", type="humid_sensor", readin=True, action=read_humidity, action_args=None),
    InteractableInfo(1, displayName="Temperature Sensor", type="temp_sensor", readin=True, action=read_temperature, action_args=None),
    InteractableInfo(2, displayName="Motion Sensor", type="motion_sensor", readin=True, action=read_motion_sensor, action_args=None),
    InteractableInfo(3, displayName="LED", type="bulb", readin=False, action=toggle_led, action_args=None),
]

ir_node = find_menu_node("root-ir-list")
def get_ir_list():
    global ir_node
    ir_list = []
    n = len(sensor_info)
    for j, child in enumerate(ir_node.children):
        if "Back" in child.line2:
            continue
        name = child.line2[1:15].strip()
        child_info = InteractableInfo(id=j+n, displayName=name, type="ir", readin=False,
                                      action=child.action, action_args=child.action_args)
        ir_list.append(child_info)
    return ir_list

app = Flask(__name__)
@app.get('/api_init')
def api_init():
    global sensor_info
    ir_list = get_ir_list()
    return jsonify([info.base_to_dict() for info in sensor_info + ir_list])

@app.route('/api_post', methods=['GET', 'POST'])
def api_post():
    global sensor_info
    ir_list = get_ir_list()
    id = int(request.args.get('id', None))
    if id < len(sensor_info):
        info = sensor_info[id]
    else:
        info = ir_list[id - len(sensor_info)]
        
    result = info.action(**info.action_args) if info.action_args else info.action()
    if result is not None:
        return jsonify(result)
    else:
        return jsonify("Done")

try:
    app.run("0.0.0.0")
except KeyboardInterrupt:
    menu.clear()
    print("Clearing the screen and exiting program.")







