from menu import Menu
from menu_options import MenuOptions
import time
import subprocess
import os


def initialize_menu(lcd, dht_sensor):
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
        fn_no_ext_rep = file[:file.rfind("-")]
        lcd.text("SENT: ", 1)
        lcd.text(fn_no_ext_rep.center(16), 2)
        time.sleep(1)
    
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
            lcd.text("IR".center(16), 1)
            lcd.text("Add Success".center(16), 2)
            time.sleep(2)
            return root_ir_add
        except subprocess.TimeoutExpired:
            lcd.text("IR".center(16), 1)
            lcd.text("Add Timeout".center(16), 2)
            os.remove(f"./data/{filename}")
            time.sleep(2)
            return root_ir_add
        
    def ir_all_input():
        menu.input_mode = 'all'
        return root_ir_add_filename
    
    def ir_digit_input():
        menu.input_mode = 'digits'
        return root_ir_add_repetition
    
    def ir_delete(node, filename):
        os.remove(f"./data/{filename}")
        for n in node:
            n.parent = None
            del(n)
            
        lcd.text("Deleted".center(16), 1)
        lcd.text(filename[:filename.rfind("-")].center(16), 2)
        time.sleep(1)
        return root_ir_delete

    def add_existing_irs(dir="./data"):
        ir_files = [f for f in os.listdir(dir) if f.endswith(".ir")]
        for filename in ir_files: 
            # filename = f"{name}-{repetition}.ir"
            extension_idx = filename.rfind(".")
            fn_no_extension = filename[:extension_idx]

            split_idx = fn_no_extension.rfind("-")
            name = fn_no_extension[:split_idx]
            repetition = int(fn_no_extension[split_idx+1:])
            new_option = MenuOptions(name=f"root-ir-list-{name}", line1="IR List", line1_marker=False, line2=f"{name}", line2_marker=True, 
                                     action=ir_send, 
                                     action_args={"file": f"{filename}", "repetition": repetition}, 
                                     parent=root_ir_list)
            
            delete_option = MenuOptions(name=f"root-ir-list-{name}-delete", line1="IR Delete", line1_marker=False, line2=f"{name}", line2_marker=True,
                         action=ir_delete, parent=root_ir_delete)
            delete_option.action_args = {"node": [new_option, delete_option], "filename" : filename}


    def update_root_stats(refresh_only=False):
        root.line2 = f"T:{dht_sensor.temperature}C H:{dht_sensor.humidity}%".center(16)
        if not refresh_only:
            return root.children[0] # go to the first child of the root node (work like a normal menu without action)
        else: 
            return None # if this is refresh only, return None to stay at the current node
    
    ########## MENU OPTIONS ##########
    root = MenuOptions(name="dummy", line1="SMART HOME HUB", line1_marker=False, line2="T:XXC H:XX%", line2_marker=False, action=update_root_stats, parent=None) 
    
    # First level
    root_stat = MenuOptions(name="root-stat", line1="STAT", line1_marker=True, line2="", line2_marker=False, action=None, parent=root)
    root_ir = MenuOptions(name="root-ir", line1="IR", line1_marker=True, line2="", line2_marker=False, action=None, parent=root)
    root_sensors = MenuOptions(name="root-sensors", line1="SENSORS", line1_marker=True, line2="", line2_marker=False, action=None, parent=root)
    root_about = MenuOptions(name="root-about", line1="ABOUT", line1_marker=True, line2="", line2_marker=False, action=about_page, parent=root) # the actioin is a callable function definied above that will display the about page, since it's not going to return anything BUT a workflow (has actioni), it will stay at the current node
    root_back = MenuOptions(name="root-back", line1="BACK", line1_marker=True, line2="", line2_marker=False, action=lambda: root_back.parent, parent=root) # this lambda function allow it to serve as a BACK button (i.e., go to parent node)

    # Second level - IR
    root_ir_list = MenuOptions(name="root-ir-list", line1="IR", line1_marker=False, line2="List", line2_marker=True, action=None, parent=root_ir)
    root_ir_add = MenuOptions(name="root-ir-add", line1="IR", line1_marker=False, line2="Add", line2_marker=True, action=ir_all_input, parent=root_ir)
    root_ir_delete = MenuOptions(name="root-ir-delete", line1="IR", line1_marker=False, line2="Delete", line2_marker=True, action=None, parent=root_ir)
    root_ir_back = MenuOptions(name="root-ir-back", line1="IR", line1_marker=False, line2="Back", line2_marker=True, action=lambda: root_ir_back.parent, parent=root_ir) # this lambda function allow it to serve as a BACK button (i.e., go to parent node)
    
    # Third level - IR List
    add_existing_irs()  # add existing IR files to the list
    root_ir_list_back = MenuOptions(name="root-ir-list-back", line1="IR List", line1_marker=False, line2="Back", line2_marker=True, action=lambda: root_ir_list_back.parent, parent=root_ir_list) 
    root_ir_delete_back = MenuOptions(name="root-ir-delete-back", line1="IR Delete", line1_marker=False, line2="Back", line2_marker=True, action=lambda: root_ir_delete_back.parent, parent=root_ir_delete)

    # Third level - IR Add
    root_ir_add_filename = MenuOptions(name="root-ir-add-input", line1="Enter File Name", line1_marker=False, line2="turn the knob...", line2_marker=False, action=ir_digit_input, parent=root_ir_add)
    root_ir_add_repetition = MenuOptions(name="root-ir-add-repetition", line1="Enter Repetition", line1_marker=False, line2="turn the knob...", line2_marker=False, action=ir_receive, parent=root_ir_add_filename)

    menu = Menu(root, lcd)
    return menu