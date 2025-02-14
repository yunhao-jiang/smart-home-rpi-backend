import subprocess

# ir-ctl -d /dev/lirc0 --send=tvpower.txt
subprocess.run(["ir-ctl", "-d", "/dev/lirc0", "--send=tvpower.txt"])
