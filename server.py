import socket
import subprocess
from time import sleep
import requests
import sys
import time
import datetime
import asyncio

def is_proxy_working(proxy_ip, proxy_port, timeout=1):
    try:
        # First check if port is open
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((proxy_ip, proxy_port))
        
        if result == 0:
            # If port is open, try to send a simple HTTP request to check if server is listening
            try:
                # Send a simple HTTP HEAD request
                sock.send(b"HEAD / HTTP/1.1\r\nHost: localhost\r\n\r\n")
                # Wait for response
                response = sock.recv(1024)
                if response:
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{current_time}] [+] Port {proxy_port} is open and server is responding")
                    sock.close()
                    return True
                else:
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{current_time}] [-] Port {proxy_port} is open but server is not responding")
                    sock.close()
                    return False
            except:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{current_time}] [-] Port {proxy_port} is open but server is not responding properly")
                sock.close()
                return False
        else:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] [-] Proxy connection check failed - Port {proxy_port} is not accessible (Error code: {result})")
            sock.close()
            return False
            
    except Exception as e:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] [-] Proxy connection error: {str(e)}")
        return False

def cmd(command: str):
    while True:
        try:
            return subprocess.check_output(command.split(), timeout=10)
        except subprocess.TimeoutExpired:
            print("Command timed out after 10s")
            break
        except subprocess.CalledProcessError:
            sleep(1)

async def reset_adb_connection():
    try:
        print("-> Resetting ADB connection...")
        cmd("adb kill-server")
        await asyncio.sleep(2)
        cmd("adb start-server")
        await asyncio.sleep(2)
        print("[+] ADB server reset complete")
        return True
    except:
        return False

async def check_proxy_connection(proxy_ip, proxy_port):
    while True:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] -> Checking proxy connection...")
        if is_proxy_working(proxy_ip, proxy_port):
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [+] Port {proxy_port} is working")
            return True
        else:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [-] Proxy connection lost!")
            return False
        await asyncio.sleep(1)

async def forward_ports():
    while True:
        try:
            print("=============ADB-CONNECTOR=================")
            # First reset ADB
            await reset_adb_connection()
            
            print("-> trying to connect to localhost:5555")
            resultConnectLocalhost = cmd("adb connect localhost:5555")

            if b'connected' in resultConnectLocalhost:
                print("[+] connected to localhost:5555")
                devices = cmd("adb devices")
                if (b'localhost:5555' in devices) or (b'emulator-5554' in devices):
                    try:
                        print("-> trying to forward traffic from windows to bluestack with port 63254 for HTTP")
                        forwardResult = cmd("adb -s localhost:5555 forward tcp:63254 tcp:63254")
                        print("[+] traffic forwarded with port 63254 from windows to bluestack")
                        print("-> trying to forward traffic from windows to bluestack with port 63255 for SOCKS")
                        forwardResult = cmd("adb -s localhost:5555 forward tcp:63255 tcp:63255")
                        print("[+] traffic forwarded with port 63255 from windows to bluestack")
                        print("[+] status: all ready done.")
                        return True
                    except subprocess.CalledProcessError as e:
                        print("[-] could not forward traffic!")
                        await asyncio.sleep(1)
                        return False
            else:
                print("after 1s trying again connect to localhost:5555")
                await asyncio.sleep(1)
                continue
        except subprocess.CalledProcessError as e:
            await reset_adb_connection()
            continue

async def main():
    proxy_ip = "localhost"
    proxy_port = 63254
    need_to_forward = True
    failure_count = 0
    FAILURE_THRESHOLD = 3  # Number of consecutive failures before resetting

    while True:
        # Check proxy connection
        proxy_working = await check_proxy_connection(proxy_ip, proxy_port)
        
        if not proxy_working:
            failure_count += 1
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failure count: {failure_count}")
            if failure_count >= FAILURE_THRESHOLD:
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] -> Too many failures, resetting ADB and forwarding ports...")
                await reset_adb_connection()
                await forward_ports()
                failure_count = 0  # Reset the counter after attempting recovery
            await asyncio.sleep(1)
        else:
            failure_count = 0  # Reset on success
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())