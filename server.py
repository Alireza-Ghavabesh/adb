import socket
import subprocess
from time import sleep
import datetime
import asyncio
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# --- Configuration ---
PROXY_IP = "localhost"
PROXY_PORT_HTTP = 63254
PROXY_PORT_SOCKS = 63255
FAILURE_THRESHOLD = 3
EASY_MODE = "ON" 

# --- Global Animation State ---
# Start in LOADING to prevent freeze
APP_STATE = "LOADING"  
STATUS_TEXT = "Initializing..."
LAST_ERROR = ""

# --- Visual Assets ---
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
PULSE_FRAMES = [
    f"{Fore.GREEN}●{Style.RESET_ALL}", 
    f"{Fore.GREEN}●{Style.RESET_ALL}", 
    f"{Fore.WHITE}●{Style.RESET_ALL}", 
    f"{Fore.GREEN}●{Style.RESET_ALL}"
]

# --- Core Logic Functions ---

def cmd_sync(command: str):
    """Blocking command execution."""
    try:
        return subprocess.check_output(
            command.split(), 
            timeout=10, 
            stderr=subprocess.STDOUT
        )
    except Exception:
        return b''

async def cmd(command: str):
    """Async wrapper."""
    return await asyncio.to_thread(cmd_sync, command)

async def is_proxy_working(proxy_ip, proxy_port, timeout=1):
    """Checks if the proxy port is open and attempts a basic HTTP handshake."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = await asyncio.to_thread(sock.connect_ex, (proxy_ip, proxy_port))
        if result == 0:
            try:
                # Attempt a simple request to confirm it's actually serving
                await asyncio.to_thread(sock.send, b"HEAD / HTTP/1.1\r\nHost: localhost\r\n\r\n")
                response = await asyncio.to_thread(sock.recv, 1024)
                sock.close()
                return True if response else False
            except:
                sock.close()
                return False
        sock.close()
        return False
    except:
        return False

async def reset_adb_connection():
    """Kills and restarts the ADB server."""
    global STATUS_TEXT
    if EASY_MODE == "ON": STATUS_TEXT = "Resetting ADB Server..."
    else: print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {Fore.YELLOW}🔄 Resetting ADB...")
    
    await cmd("adb kill-server")
    await asyncio.sleep(1)
    await cmd("adb start-server")
    await asyncio.sleep(1)
    return True

async def forward_ports(initial_run=False):
    """Connects to the emulator and forwards the required ports."""
    global STATUS_TEXT
    
    await reset_adb_connection()

    if EASY_MODE == "ON": STATUS_TEXT = "Connecting to Emulator..."
    elif initial_run: print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {Fore.YELLOW}🔗 Connecting to localhost...")

    result_connect = await cmd("adb connect localhost:5555")
    
    if b'connected' in result_connect:
        devices = await cmd("adb devices")
        # Check for emulator-5554 or localhost:5555
        if (b'localhost:5555' in devices) or (b'emulator-5554' in devices):
            try:
                if EASY_MODE == "ON": STATUS_TEXT = "Forwarding Traffic Ports..."
                elif initial_run: print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {Fore.YELLOW}➡️ Forwarding Ports...")
                
                await cmd(f"adb -s localhost:5555 forward tcp:{PROXY_PORT_HTTP} tcp:{PROXY_PORT_HTTP}")
                await cmd(f"adb -s localhost:5555 forward tcp:{PROXY_PORT_SOCKS} tcp:{PROXY_PORT_SOCKS}")
                return True
            except:
                return False
        return False
    return False

# --- The Renderer (Updated for BIG TEXT) ---

def draw_ready_box():
    """
    Draws the Massive ASCII Art Success Message.
    Clears the entire terminal screen first to prevent output overlap.
    """
    # Use ANSI escape codes to clear the screen: 
    # \033[H (Move cursor to home position, top-left)
    # \033[J (Clear screen from cursor down)
    print('\033[H\033[J', end='', flush=True) 
    
    # Raw string for ASCII Art
    ascii_art = r"""
  ██████  ██    ██ ███████ ████████ ███████ ███    ███
 ██       ██    ██ ██          ██    ██     ████  ████
 ███████   ██  ██  ███████     ██    █████  ██ ████ ██
      ██     ████      ██     ██    ██     ██  ██  ██
 ███████      ██    ███████     ██    ███████ ██      ██

 ██████  ███████  █████  ██████  ██    ██     ██
 ██  ██ ██      ██  ██ ██  ██  ██  ██     ██
 ██████  █████  ███████ ██  ██   ████      ██
 ██  ██ ██      ██  ██ ██  ██    ██
 ██  ██ ███████ ██  ██ ██████    ██      ██
    """
    
    # Print it in Bright Green
    print(Fore.GREEN + Style.BRIGHT + ascii_art + Style.RESET_ALL)
    print() # Extra spacing

async def animation_loop():
    """
    Handles ALL visual output in EASY_MODE.
    """
    spinner_idx = 0
    pulse_idx = 0
    
    while True:
        if EASY_MODE == "OFF":
            await asyncio.sleep(1)
            continue

        # 1. LOADING STATE (e.g., deep recovery)
        if APP_STATE == "LOADING":
            frame = SPINNER_FRAMES[spinner_idx % len(SPINNER_FRAMES)]
            line = f"{Fore.CYAN}{frame} {Fore.WHITE}{STATUS_TEXT}"
            # Use \r to return to the start of the line and overwrite previous status
            print(f"\r{' '*100}\r{line}", end="", flush=True)
            spinner_idx += 1
            await asyncio.sleep(0.1) 

        # 2. READY STATE
        elif APP_STATE == "READY":
            pulse = PULSE_FRAMES[pulse_idx % len(PULSE_FRAMES)]
            line = f"{Fore.GREEN}[ {pulse} {Fore.GREEN}] {Fore.WHITE}Monitoring Proxy Connection {Fore.GREEN}:: {Fore.WHITE}{PROXY_PORT_HTTP} {Fore.GREEN}:: {Fore.WHITE}Active"
            # Use \r to return to the start of the line and overwrite previous status
            print(f"\r{' '*100}\r{line}", end="", flush=True)
            pulse_idx += 1
            await asyncio.sleep(0.25) 

        # 3. ERROR STATE (transient failure before deep recovery)
        elif APP_STATE == "ERROR":
            line = f"{Fore.RED}🚨 CONNECTION LOST {Fore.WHITE}| {STATUS_TEXT}"
            # Use \r to return to the start of the line and overwrite previous status
            print(f"\r{' '*100}\r{line}", end="", flush=True)
            await asyncio.sleep(0.5) 
        
        else:
            await asyncio.sleep(0.1)

# --- Main Logic Loop ---

async def logic_loop():
    global APP_STATE, STATUS_TEXT, LAST_ERROR
    
    failure_count = 0
    # Flag to control drawing of the big ASCII box. Reset on failure.
    ready_box_drawn = False 
    
    # Initial Start
    APP_STATE = "LOADING"
    STATUS_TEXT = "Initializing core services..."
    await asyncio.sleep(1) 
    
    success = await forward_ports(initial_run=True)
    
    if not success:
        # If initial setup fails, start in error state so the loop retries immediately
        APP_STATE = "ERROR"
        STATUS_TEXT = "Initial setup failed. Starting Watchdog..."
        await asyncio.sleep(2)
    
    while True:
        working = await is_proxy_working(PROXY_IP, PROXY_PORT_HTTP)
        
        if working:
            failure_count = 0
            
            # Transition from LOADING/ERROR back to READY
            if APP_STATE != "READY":
                APP_STATE = "READY"
                STATUS_TEXT = "Active"
                
                # Draw the big banner if we haven't since the last failure
                if not ready_box_drawn:
                    if EASY_MODE == "ON":
                        draw_ready_box()
                    ready_box_drawn = True # Mark as drawn
            
            await asyncio.sleep(2) 
            
        else:
            # Connection failed
            failure_count += 1
            
            # Clear the ready_box_drawn flag so the banner shows on successful recovery
            if ready_box_drawn:
                # Optional: Clear the console immediately upon first failure for a clean transition
                print('\033[H\033[J', end='', flush=True)
                
            ready_box_drawn = False 
            
            if failure_count == 1:
                # Transition to ERROR state on first failure
                APP_STATE = "ERROR" 
                
            STATUS_TEXT = f"Retrying connection ({failure_count}/{FAILURE_THRESHOLD})..."
            
            if failure_count >= FAILURE_THRESHOLD:
                # Initiate deep recovery attempt
                APP_STATE = "LOADING"
                STATUS_TEXT = "Deep recovery initiated..."
                await forward_ports(initial_run=False)
                failure_count = 0 # Reset failure count after attempting fix
            
            await asyncio.sleep(1)

async def main():
    if EASY_MODE == "OFF":
        print(f"{Fore.MAGENTA}🚀 ADB Proxy Watchdog started (Advanced Mode).")
    
    await asyncio.gather(
        animation_loop(),
        logic_loop()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Ensure a clean line break when terminated
        print(f"\r{' '*100}\r{Fore.YELLOW}👋 Terminated by user.")