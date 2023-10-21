import subprocess
from time import sleep


def cmd(command: str):
    return subprocess.check_output(command.split(" "))


while True:
    try:
        print("=========================================")
        print(
            "-> trying to connect to localhost:5555")
        t = cmd("adb connect localhost:5555")
    except subprocess.CalledProcessError as e:
        try:
            print(
                "-> trying to: adb kill-server")
            cmd("adb kill-server")
        except subprocess.CalledProcessError as e:
            print("[-] could kill the server")
            continue
        try:
            print(
                "-> trying to: adb start-server")
            cmd("adb start-server")
        except subprocess.CalledProcessError as e:
            print("[-] could kill the server")
            continue
    itsFirstTimeConnect = True
    while True:
        try:
            devices = cmd("adb devices")
            if b'localhost:5555' in devices:
                if itsFirstTimeConnect:
                    print("[+] connected to localhost:5555 Bluestack")
                    while True:
                        try:
                            print(
                                "-> trying to forward traffic from windows to bluestack with port 63254 for HTTP")
                            print(
                                "-> trying to forward traffic from windows to bluestack with port 63255 for SOCKS")
                            forwardResult = cmd(
                                "adb -s localhost:5555 forward tcp:63254 tcp:63254")
                            forwardResult = cmd(
                                "adb -s localhost:5555 forward tcp:63255 tcp:63255")
                            print(
                                "[+] traffic forwarded with port 4200 from windows to bluestack")
                            itsFirstTimeConnect = False
                            print("[+] status: all ready done.")
                            break
                        except subprocess.CalledProcessError as e:
                            print("[-] could not forward traffic!")

                        sleep(1)
                else:
                    sleep(1)
            else:
                sleep(1)
                break
        except subprocess.CalledProcessError as e:
            sleep(1)
            continue
