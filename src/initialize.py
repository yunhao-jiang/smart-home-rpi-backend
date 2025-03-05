from menu import Menu
from menu_options import MenuOptions
import time
import subprocess
import os
import socket

TIMEOUT = 30

def initialize_menu(lcd, dht_sensor):
    ########## VARS ##########
    start_time = time.time()
    temp, humid = None, None
    avg_temp, avg_humid = None, None

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
        subprocess.run(["ir-ctl", "-d", "/dev/lirc1"]+ [f"--send=data/{file}"] * repetition + ["--gap=50000"])
        # subprocess.run(["ir-ctl", "-d", "/dev/lirc0"]+ [f"--send=data/{file}"] * repetition + ["--gap=50000"])
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
                # ["ir-ctl", "-d", "/dev/lirc1", f"--receive=data/{filename}", "-1"],
                ["ir-ctl", "-d", "/dev/lirc0", f"--receive=data/{filename}", "-1"],
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
            new_option = MenuOptions(name=f"root-ir-list-{name}", line1="Remote List", line1_marker=False, line2=f"{name}", line2_marker=True, 
                                     action=ir_send, 
                                     action_args={"file": f"{filename}", "repetition": repetition}, 
                                     parent=root_ir_list)
            
            delete_option = MenuOptions(name=f"root-ir-list-{name}-delete", line1="IR Delete", line1_marker=False, line2=f"{name}", line2_marker=True,
                         action=ir_delete, parent=root_ir_delete)
            delete_option.action_args = {"node": [new_option, delete_option], "filename" : filename}

    def update_root_stats(refresh_only=False):
        nonlocal temp, humid, avg_temp, avg_humid
        local_time = time.localtime()
        root.line1 = time.strftime("%m/%d/%Y %H:%M", local_time).center(16)
        try: 
            temp = dht_sensor.temperature
            humid = dht_sensor.humidity
            root.line2 = f"T:{temp}C H:{humid}%".center(16)
            # Update avg readings since uptime
            if avg_temp is None or avg_humid is None:
                avg_temp, avg_humid = temp, humid
            else:
                uptime_seconds = time.time() - start_time
                avg_temp = ((uptime_seconds - TIMEOUT) * avg_temp + TIMEOUT * temp) / uptime_seconds
                avg_humid = ((uptime_seconds - TIMEOUT) * avg_humid + TIMEOUT * humid) / uptime_seconds
            root_info_avgth_display.line2 = f"T:{avg_temp:.1f}C H:{avg_humid:.1f}%".center(16)
        except Exception as e:
            # handle the case where reading error happens on start up
            if temp is None or humid is None:
                root.line2 = f"T:..C H:..%".center(16)
                root_info_avgth_display.line2 = f"T:..C H:..%".center(16)
            print(e)
        if not refresh_only:
            return root.children[0] # go to the first child of the root node (work like a normal menu without action)
        else: 
            return None # if this is refresh only, return None to stay at the current node
    
    def update_info_ip():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # 连接到公网 DNS 服务器
            ip_address = s.getsockname()[0]
        root_info_ip_display.line2 = ip_address.center(16)
        return root_info_ip_display

    def update_info_uptime():
        # with open("/proc/uptime", "r") as f: # Linux system uptime
        #     uptime_seconds = round(float(f.readline().split()[0]))
        uptime_seconds = round(time.time() - start_time)
        hh = uptime_seconds // 3600
        uptime_seconds %= 3600
        mm = uptime_seconds // 60
        uptime_seconds %= 60
        ss = uptime_seconds % 3600
        root_info_uptime_display.line2 = f"{hh:02}:{mm:02}:{ss:02}".center(16)
        return root_info_uptime_display

    
    ########## MENU OPTIONS ##########
    root = MenuOptions(name="dummy", line1="HH:RR MM/DD/YYYY", line1_marker=False, line2="T:..C H:..%", line2_marker=False, action=update_root_stats, parent=None) 
    
    # First level
    root_ir = MenuOptions(name="root-ir", line1="Features", line1_marker=False, line2="IR Remote", line2_marker=True, action=None, parent=root)
    root_info = MenuOptions(name="root-info", line1="Features", line1_marker=False, line2="Info", line2_marker=True, action=None, parent=root)
    root_devices = MenuOptions(name="root-devices", line1="Features", line1_marker=False, line2="Devices", line2_marker=True, action=None, parent=root)
    root_about = MenuOptions(name="root-about", line1="Features", line1_marker=False, line2="About", line2_marker=True, action=about_page, parent=root) # the actioin is a callable function definied above that will display the about page, since it's not going to return anything BUT a workflow (has actioni), it will stay at the current node
    root_back = MenuOptions(name="root-back", line1="Features", line1_marker=False, line2="Back", line2_marker=True, action=lambda: root_back.parent, parent=root) # this lambda function allow it to serve as a BACK button (i.e., go to parent node)

    # Second level - Info
    root_info_ip = MenuOptions(name="root-info-ip", line1="Info", line1_marker=False, line2="IP Address", line2_marker=True, action=update_info_ip, parent=root_info)
    root_info_uptime = MenuOptions(name="root-info-uptime", line1="Info", line1_marker=False, line2="Uptime", line2_marker=True, action=update_info_uptime, parent=root_info)
    root_info_avgth = MenuOptions(name="root-info-avgth", line1="Info", line1_marker=False, line2="Avg Temp&Humi", line2_marker=True, action=None, parent=root_info)
    root_info_back = MenuOptions(name="root-info-back", line1="Info", line1_marker=False, line2="Back", line2_marker=True, action=lambda: root_info_back.parent, parent=root_info) # this lambda function allow it to serve as a BACK button (i.e., go to parent )

    # Third level - Info
    root_info_ip_display = MenuOptions(name="root-info-ip-display", line1="IP Address", line1_marker=False, line2="", line2_marker=False, action=lambda: root_info_ip_display.parent, parent=root_info_ip)
    root_info_uptime_display = MenuOptions(name="root-info-uptime-display", line1="Uptime", line1_marker=False, line2="", line2_marker=False, action=lambda: root_info_uptime_display.parent, parent=root_info_uptime)
    root_info_avgth_display = MenuOptions(name="root-info-avgth-display", line1="Avg Temp&Humid", line1_marker=False, line2="", line2_marker=False, action=lambda: root_info_avgth_display.parent, parent=root_info_avgth)


    # Second level - IR
    root_ir_list = MenuOptions(name="root-ir-list", line1="IR Remote", line1_marker=False, line2="List", line2_marker=True, action=None, parent=root_ir)
    root_ir_add = MenuOptions(name="root-ir-add", line1="IR Remote", line1_marker=False, line2="Add", line2_marker=True, action=ir_all_input, parent=root_ir)
    root_ir_delete = MenuOptions(name="root-ir-delete", line1="IR Remote", line1_marker=False, line2="Delete", line2_marker=True, action=None, parent=root_ir)
    root_ir_back = MenuOptions(name="root-ir-back", line1="IR Remote", line1_marker=False, line2="Back", line2_marker=True, action=lambda: root_ir_back.parent, parent=root_ir) # this lambda function allow it to serve as a BACK button (i.e., go to parent node)
    
    # Third level - IR List
    add_existing_irs()  # add existing IR files to the list
    root_ir_list_back = MenuOptions(name="root-ir-list-back", line1="Remote List", line1_marker=False, line2="Back", line2_marker=True, action=lambda: root_ir_list_back.parent, parent=root_ir_list) 
    root_ir_delete_back = MenuOptions(name="root-ir-delete-back", line1="Delete Remote", line1_marker=False, line2="Back", line2_marker=True, action=lambda: root_ir_delete_back.parent, parent=root_ir_delete)

    # Third level - IR Add
    root_ir_add_filename = MenuOptions(name="root-ir-add-input", line1="Enter File Name", line1_marker=False, line2="turn the knob...", line2_marker=False, action=ir_digit_input, parent=root_ir_add)
    root_ir_add_repetition = MenuOptions(name="root-ir-add-repetition", line1="Enter Repetition", line1_marker=False, line2="turn the knob...", line2_marker=False, action=ir_receive, parent=root_ir_add_filename)

    menu = Menu(root, lcd)
    return menu