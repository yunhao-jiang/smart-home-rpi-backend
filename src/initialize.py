from menu import Menu
from menu_options import MenuOptions
import time
import subprocess


def initialize_menu(lcd):
    ########## VARS ##########

    ########## CUSTOMIZE FUNCTIONS ##########
    def about_page():
        lcd.text("Made by".center(16), 1)
        lcd.text("Yunhao & Robin".center(16), 2)
        time.sleep(3)
        lcd.text("Thank You!".center(16), 1)
        lcd.text("(c)2025".center(16), 2)
        time.sleep(3) # return nothing to stay at the current node

    #  add more function such as receiving IR signals and etc. Do NOT implement this part yet.

    def ir_send(file, repetition):
        # Send the IR signal
        subprocess.run(["ir-ctl", "-d", "/dev/lirc0"]+ [f"--send=data/{file}"] * repetition + ["--gap=50000"])
        lcd.text("Sent: " + file, 1)
        lcd.text("", 2)
        time.sleep(1)
        # lcd.text(output,1)
    
    def ir_receive():
        name = menu.input_queue.pop(0)
        repetition = int(menu.input_queue.pop(0))
        filename = f"{name}-{repetition}.ir"
        print(f"Receiving IR: {filename}")
        try:
            lcd.text("Receiving IR...".center(16), 1)
            lcd.text("Timeout in 10sec".center(16), 2)
            result = subprocess.run(
                ["ir-ctl", "-d", "/dev/lirc1", f"--receive=data/{filename}", "-1"],
                timeout=10
            )
            new_option = MenuOptions(name=f"root-ir-list-{name}", line1="IR List", line1_marker=False, line2=f"{name}", line2_marker=True, 
                                     action=ir_send, 
                                     action_args={"file": f"{filename}", "repetition": repetition}, 
                                     parent=root_ir_list)
            return root_ir_add_success
        except subprocess.TimeoutExpired:
            return root_ir_add_timeout
        
    def ir_all_input():
        menu.input_mode = 'all'
        return root_ir_add_filename
    
    def ir_digit_input():
        menu.input_mode = 'digits'
        return root_ir_add_repetition

    
    
    ########## MENU OPTIONS ##########
    root = MenuOptions(name="dummy", line1="Root", line1_marker=False, line2="", line2_marker=False, action=None, parent=None) # This is a dummy root that won't be shown
    
    # First level
    root_stat = MenuOptions(name="root-stat", line1="STAT", line1_marker=True, line2="", line2_marker=False, action=None, parent=root)
    root_ir = MenuOptions(name="root-ir", line1="IR", line1_marker=True, line2="", line2_marker=False, action=None, parent=root)
    root_sensors = MenuOptions(name="root-sensors", line1="SENSORS", line1_marker=True, line2="", line2_marker=False, action=None, parent=root)
    root_about = MenuOptions(name="root-about", line1="ABOUT", line1_marker=True, line2="", line2_marker=False, action=about_page, parent=root) # the actioin is a callable function definied above that will display the about page, since it's not going to return anything BUT a workflow (has actioni), it will stay at the current node

    # Second level - IR
    root_ir_list = MenuOptions(name="root-ir-list", line1="IR", line1_marker=False, line2="List", line2_marker=True, action=None, parent=root_ir)
    root_ir_add = MenuOptions(name="root-ir-add", line1="IR", line1_marker=False, line2="Add", line2_marker=True, action=ir_all_input, parent=root_ir)
    root_ir_back = MenuOptions(name="root-ir-back", line1="IR", line1_marker=False, line2="Back", line2_marker=True, action=lambda: root_ir_back.parent, parent=root_ir) # this lambda function allow it to serve as a BACK button (i.e., go to parent node)
    
    # TODO: More menu options can be added here
    # Third level - IR List
    root_ir_list_back = MenuOptions(name="root-ir-list-back", line1="IR List", line1_marker=False, line2="Back", line2_marker=True, action=lambda: root_ir_list_back.parent, parent=root_ir_list) 

    # Third level - IR Add
    root_ir_add_filename = MenuOptions(name="root-ir-add-input", line1="Enter File Name", line1_marker=False, line2="turn the knob...", line2_marker=False, action=ir_digit_input, parent=root_ir_add)
    root_ir_add_repetition = MenuOptions(name="root-ir-add-repetition", line1="Enter Repetition", line1_marker=False, line2="turn the knob...", line2_marker=False, action=ir_receive, parent=root_ir_add_filename)
    
    root_ir_add_success = MenuOptions(name="root-ir-add-success", line1="IR", line1_marker=False, line2="Add Success", line2_marker=False, action=lambda: root_ir, parent=root_ir_add_repetition)
    root_ir_add_timeout = MenuOptions(name="root-ir-add-timeout", line1="IR", line1_marker=False, line2="Add Timeout", line2_marker=False, action=lambda: root_ir, parent=root_ir_add_repetition)

    menu = Menu(root, lcd)
    return menu