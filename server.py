import subprocess
from time import sleep


def cmd(command: str):
    return subprocess.check_output(command.split(" "))


while True:
    sleep(1)
    t = cmd("adb connect localhost:5555")
    devices = cmd("adb devices")
    print(t)
    if b'already connected' in t and b'offline' not in devices and b'error: device' not in t and b'unable' not in t:
        forwardResult = cmd("adb -s localhost:5555 forward tcp:4200 tcp:4200")
        print(forwardResult)
    if b'empty host name' in t:
        cmd("adb kill-server")
        cmd("adb start-server")
