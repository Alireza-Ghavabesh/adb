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
STATUS_BOX_DRAWN = False # New state to control static box drawing

# --- Visual Assets ---
# MODIFIED: Changed spinner frames to use /|\- instead of Unicode characters
SPINNER_FRAMES = ["/", "-", "\\", "|"] 
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

# --- The Renderer ---

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
██       ██    ██ ██          ██    ██    ████  ████
███████   ██  ██  ███████      ██    █████  ██ ████ ██
      ██     ████      ██      ██    ██    ██  ██  ██
███████      ██  ███████      ██    ███████ ██      ██

 ██████ ███████  █████ ██████ ██    ██     ██
 ██ ██ ██     ██ ██  ██ ██  ██  ██    ██
 ██████ █████ ███████ ██  ██   ████     ██
 ██ ██ ██     ██  ██ ██  ██    ██
 ██ ██ ███████ ██  ██ ██████    ██     ██
    """
    
    # Print it in Bright Green
    print(Fore.GREEN + Style.BRIGHT + ascii_art + Style.RESET_ALL)
    print() # Extra spacing

def draw_static_status_box(status_color):
    """
    Draws the static border block only once and positions the cursor 
    for dynamic content to prevent flickering.
    """
    global STATUS_BOX_DRAWN
    
    if not STATUS_BOX_DRAWN:
        # Clear screen and draw static frame
        print('\033[H\033[J', end='', flush=True) # Clear the entire terminal
        
        block_width = 80
        color_start = status_color + Style.BRIGHT
        color_end = Style.RESET_ALL
        empty_line = color_start + "|" + " " * (block_width - 2) + "|" + color_end
        
        # Draw the 7 lines of the box structure
        print(color_start + "=" * block_width + color_end) # Line 1: Top Border
        print(empty_line) # Line 2
        print(empty_line) # Line 3

        # Line 4: The Dynamic Content Target. Print a placeholder of spaces.
        print(color_start + "|" + " " * (block_width - 2) + "|" + color_end) 

        print(empty_line) # Line 5
        print(empty_line) # Line 6
        print(color_start + "=" * block_width + color_end) # Line 7: Bottom Border

        # The cursor is now on Line 8. We need to move it up 4 lines to Line 4.
        # \033[A is the standard ANSI escape code to move the cursor UP one line.
        print('\033[A' * 4, end='', flush=True) 
        
        STATUS_BOX_DRAWN = True

def update_dynamic_status_line(message, status_color):
    """Updates only the content line within the already drawn static border."""
    block_width = 80
    
    # The inner content area between the vertical bars is 78 characters (block_width - 2).
    INNER_WIDTH = block_width - 2  # 78

    # Handle truncation
    if len(message) > INNER_WIDTH:
        # Truncate if message exceeds 78 characters
        display_message = message[:INNER_WIDTH - 3] + "..."
    else:
        display_message = message

    # Calculate padding for centering within 78 characters
    padding_needed = INNER_WIDTH - len(display_message)
    padding_left = padding_needed // 2
    padding_right = padding_needed - padding_left
    
    # Construct the inner content string (exactly 78 chars wide)
    inner_content = " " * padding_left + display_message + " " * padding_right
    
    # The full line to print (80 characters: | + 78 content + |)
    full_line = status_color + Style.BRIGHT + "|" + inner_content + "|" + Style.RESET_ALL
    
    # Print the line, overwriting the placeholder line 4.
    # We use '\r' to ensure the cursor starts at the beginning of the line before printing.
    print(f"\r{full_line}", end='', flush=True)
    
    # Keep the cursor at column 0 for the next overwrite
    print('\r', end='', flush=True) 


async def animation_loop():
    """
    Handles ALL visual output in EASY_MODE.
    """
    global STATUS_BOX_DRAWN
    spinner_idx = 0
    pulse_idx = 0
    
    while True:
        if EASY_MODE == "OFF":
            await asyncio.sleep(1)
            continue

        # 1. LOADING STATE (e.g., deep recovery)
        if APP_STATE == "LOADING":
            spinner_idx += 1
            spinner_char = SPINNER_FRAMES[spinner_idx % len(SPINNER_FRAMES)]
            
            # 1a. Draw static box only if needed (prevents flicker)
            draw_static_status_box(Fore.CYAN)
            
            # 1b. Update content line (only this part animates)
            update_dynamic_status_line(f"{spinner_char} {STATUS_TEXT}", Fore.CYAN)
            await asyncio.sleep(0.1) 

        # 2. READY STATE
        elif APP_STATE == "READY":
            # Clear status box drawn flag when transitioning away from the box format
            STATUS_BOX_DRAWN = False
            
            pulse = PULSE_FRAMES[pulse_idx % len(PULSE_FRAMES)]
            line = f"{Fore.GREEN}[ {pulse} {Fore.GREEN}] {Fore.WHITE}Monitoring Proxy Connection {Fore.GREEN}:: {Fore.WHITE}{PROXY_PORT_HTTP} {Fore.GREEN}:: {Fore.WHITE}Active"
            # Keep this compact line using \r for continuous monitoring to avoid flicker
            print(f"\r{' '*100}\r{line}", end="", flush=True)
            pulse_idx += 1
            await asyncio.sleep(0.25) 

        # 3. ERROR STATE (transient failure before deep recovery)
        elif APP_STATE == "ERROR":
            # 3a. Draw static box only if needed (prevents flicker)
            draw_static_status_box(Fore.RED)
            
            # 3b. Update content line (only this part animates)
            update_dynamic_status_line(f"🚨 CONNECTION LOST | {STATUS_TEXT}", Fore.RED)
            await asyncio.sleep(0.5) 
        
        else:
            await asyncio.sleep(0.1)

# --- Main Logic Loop ---

async def logic_loop():
    global APP_STATE, STATUS_TEXT, LAST_ERROR, STATUS_BOX_DRAWN
    
    failure_count = 0
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
            ready_box_drawn = False 
            
            # Also clear the STATUS_BOX_DRAWN flag so the status box is redrawn cleanly
            if APP_STATE == "READY":
                STATUS_BOX_DRAWN = False
            
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