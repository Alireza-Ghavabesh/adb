import subprocess
from time import sleep
import requests








def cmd(command: str):
    while True:
        try:
            # Set the timeout to 180 seconds (3 minutes)
            return subprocess.check_output(command.split(), timeout=10)
        except subprocess.TimeoutExpired:
            print("Command timed out after 3 minutes.")
            break
        except subprocess.CalledProcessError:
            sleep(1)

def is_http_connection(proxy_ip, proxy_port):
    url = f'http://{proxy_ip}:{proxy_port}'
    try:
        response = requests.get(url, timeout=2)
        # print("is http connection...")
        return True
    except requests.exceptions.RequestException as e:
        print("there is no http connection...")
        return False
    



def main():
    while True:
        try:
            print("=============ADB-CONNECTOR=================")
            print(
                "-> trying to connect to localhost:5555")
            resultConnectLocalhost = cmd("adb connect localhost:5555")
            if b'unable' in resultConnectLocalhost:
                sleep(1)
                continue
            print(
                "[+] connected to localhost:5555")
            itsFirstTimeConnect = True
            while True:
                try:
                    devices = cmd("adb devices")
                    if (b'localhost:5555' in devices) or (b'emulator-5554' in devices):
                        if itsFirstTimeConnect:
                            while True:
                                try:
                                    print(
                                        "-> trying to forward traffic from windows to bluestack with port 63254 for HTTP")
                                    forwardResult = cmd(
                                        "adb -s localhost:5555 forward tcp:63254 tcp:63254")
                                    print(
                                        "[+] traffic forwarded with port 63254 from windows to bluestack")
                                    print(
                                        "-> trying to forward traffic from windows to bluestack with port 63255 for SOCKS")
                                    forwardResult = cmd(
                                        "adb -s localhost:5555 forward tcp:63255 tcp:63255")
                                    print(
                                        "[+] traffic forwarded with port 63255 from windows to bluestack")
                                    itsFirstTimeConnect = False
                                    print("[+] status: all ready done.")
                                    break
                                except subprocess.CalledProcessError as e:
                                    print("[-] could not forward traffic!")
                                    sleep(1)
                                    break
                        else:
                            if is_http_connection("localhost", 63254):
                                sleep(1)
                            else:
                                print(
                                        "-> tring to kill adb server...")
                                cmd("adb kill-server")
                                print("[+] server killed")
                                print(
                                        "-> tring to start adb server...")
                                cmd("adb start-server")
                                print("[+] adb server started.")
                                break

                    else:
                        sleep(1)
                        break
                except subprocess.CalledProcessError as e:
                    sleep(1)
                    continue
        except subprocess.CalledProcessError as e:
            try:
                print(
                    "-> trying to: adb kill-server")
                cmd("adb kill-server")
            except subprocess.CalledProcessError as e:
                print("[-] could not kill the server")
                continue
            try:
                print(
                    "-> trying to: adb start-server")
                cmd("adb start-server")
                continue
            except subprocess.CalledProcessError as e:
                print("[-] could not start the server")
                continue

main()