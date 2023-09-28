import subprocess
from time import sleep


def cmd(command: str):
    return subprocess.check_output(command.split(" "))


while True:
    sleep(1)
    t = cmd("adb connect localhost:5555")
    devices = cmd("adb devices")
    print(t)
    if b'already connected' in t and b'offline' not in devices:
        x = subprocess.check_output(
            ['adb', '-s', 'localhost:5555', 'forward', 'tcp:4200', 'tcp:4200'])
        print(x)
