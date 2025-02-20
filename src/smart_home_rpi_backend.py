from initialize import initialize_menu
from flask import Flask, request, jsonify


menu = initialize_menu() # initialize the LCD menu sturcture

# TODO: This should be replaced by a function that checks the rotary encoder, use WiringPi Pin 3 for SW (button press), Pin 2 for DT and Pin 0 for CLK
# TODO: You may need to use threading to handle the rotary encoder (so it won't block the main thread)
while True: 
    command = input("Next(n), Prev(p), Select(s)? ")
    if command == "n":  # TODO: when the rotary encoder is turned clockwise, switch to the next menu
        menu.next()
    elif command == "p": # TODO: when rotary encoder is turned counter-clockwise, switch to the previous menu
        menu.prev()
    elif command == "s": # TODO: when rotary encoder is pressed, select the current menu
        menu.select()
    else:
        print("Invalid command")


# Do not implement code to communicate with IR here. Put it as a customize function in initialize.py










# Start the flask app and handle API requests, Do not implement yet
# app = Flask(__name__)