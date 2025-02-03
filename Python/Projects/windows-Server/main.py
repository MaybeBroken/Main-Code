# A simple program to launch an xampp-based apache server and notify the user of access logs, as well as run terminal commands from socket connections
# This script is intended to run on Windows only, as it uses the xampp server software

import os
import subprocess
import time
import logging
import sys
import threading
import websockets
import asyncio
import json
import ctypes

# Check if the script is running on Windows
if not sys.platform.startswith("win"):
    raise EnvironmentError("This script is intended to run on Windows only.")

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Define the path to the Apache server executable
APACHE_PATH = r"C:\\xampp\\apache_start.bat"

# Define the path to the XAMPP installation directory
XAMPP_PATH = r"C:\\xampp"

# Define the path to the access log file
ACCESS_LOG_PATH = os.path.join(XAMPP_PATH, "apache", "logs", "access.log")

# Define the path to the error log file
ERROR_LOG_PATH = os.path.join(XAMPP_PATH, "apache", "logs", "error.log")

# Define the path to the httpd.pid file
HTTPD_PID_PATH = os.path.join(XAMPP_PATH, "apache", "logs", "httpd.pid")

# Define the IP address to bind the WebSocket server to
IPADDR_PATH = os.path.join(XAMPP_PATH, "apache", "logs", "ip.txt")

# Confirm the paths exist, if not, create them
if not os.path.exists(XAMPP_PATH):
    raise FileNotFoundError(f"XAMPP installation directory not found: {XAMPP_PATH}")
if not os.path.exists(ACCESS_LOG_PATH):
    open(ACCESS_LOG_PATH, "w").close()
if not os.path.exists(ERROR_LOG_PATH):
    open(ERROR_LOG_PATH, "w").close()
if not os.path.exists(HTTPD_PID_PATH):
    open(HTTPD_PID_PATH, "w").close()

print("XAMPP installation directory found.")


# Launch the Apache server
def launch_apache():
    logging.info("Launching Apache server...")
    process = subprocess.Popen(APACHE_PATH, shell=True)
    time.sleep(1)
    with open(HTTPD_PID_PATH, "w") as f:
        f.write(str(process.pid))
    logging.info("Apache server launched.")
    logging.info("Reading access log...")
    with open(ACCESS_LOG_PATH, "r") as f:
        f.seek(0, os.SEEK_END)  # Move the cursor to the end of the file
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)  # Wait for new entries
                continue
            else:
                logging.info(f"{line.strip()}")


# Function to read the error log file and notify the user of new entries
def read_error_log():
    logging.info("Reading error log...")
    with open(ERROR_LOG_PATH, "r") as f:
        f.seek(0, os.SEEK_END)  # Move the cursor to the end of the file
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)  # Wait for new entries
                continue
            else:
                logging.error(f"{line.strip()}")


# Function to run a command in the terminal and return the output
def run_command(command: str):
    def _th():
        result = os.system(command)
        return result

    threading.Thread(target=_th).start()


# Function to handle incoming WebSocket connections
async def handle_connection(websocket):
    logging.info("New connection established.")
    try:
        await websocket.send(
            "Connection to server established\nReady to receive commands, type 'exit' to shutdown the server\n"
        )
        while True:
            try:
                message = await websocket.recv()
                if message == "exit":
                    await websocket.send(
                        "Are you sure you want to exit? This is irreversible\nType 'yes' to confirm\n"
                    )
                    logging.info("Waiting for confirmation to exit...")
                    logging.disable(logging.CRITICAL)
                    confirmation = await websocket.recv()
                    if confirmation == "yes":
                        await websocket.send("Exiting...")
                        break
                    else:
                        logging.disable(logging.NOTSET)
                        logging.info("Resuming normal operations...")
                        await websocket.send("Resuming normal operations...")
                else:
                    await websocket.send(str(run_command(message)))
            except Exception as e:
                logging.error(f"Error: {e}")
                await websocket.send(f"Error: {e}")
    except websockets.ConnectionClosed:
        logging.info("Connection closed.")
    except Exception as e:
        logging.error(f"Error: {e}")


# Function to start the WebSocket server
async def start_websocket_server():
    print("Starting WebSocket server on port 8765...")
    async with websockets.serve(handle_connection, IPADDR, 8765):
        await asyncio.Future()  # Run forever


# Function to check if the Apache server is running
def is_apache_running():
    return os.path.exists(open(HTTPD_PID_PATH).read().strip())


# Exit function
def exit_program():
    logging.info("Exiting program...")
    os.kill(open(HTTPD_PID_PATH).read().strip(), 9)
    sys.exit(0)


# Function to make the console window fullscreen and remove the scroll bar
def make_fullscreen():
    user32 = ctypes.WinDLL("user32")
    hWnd = user32.GetForegroundWindow()
    user32.keybd_event(0x7A, 0, 0, 0)  # Press F11 key
    user32.keybd_event(0x7A, 0, 2, 0)  # Release F11 key
    os.system(
        "mode con: cols=197 lines=55"
    )  # Adjust console window size to remove scroll bar


# Main function
def main():
    global IPADDR
    if len(IPADDR) == 0 and os.path.exists(IPADDR_PATH):
        with open(IPADDR_PATH, "r") as f:
            IPADDR = f.read().strip()
    elif len(IPADDR) == 0:
        print("No IP address provided and none found in ip.txt.")
        IPADDR = input("Local IP Address: ")
        main()
        return
    else:
        with open(IPADDR_PATH, "w") as f:
            f.write(IPADDR)
    if not is_apache_running():
        threading.Thread(target=launch_apache, daemon=True).start()
    else:
        logging.info("Apache server is already running.")
    threading.Thread(target=read_error_log, daemon=True).start()
    asyncio.run(start_websocket_server())


if __name__ == "__main__":
    try:
        make_fullscreen()  # Make the console window fullscreen
        if not os.path.exists(IPADDR_PATH):
            open(IPADDR_PATH, "w").close()
            IPADDR = input(f"Local IP Address: {open(IPADDR_PATH).read().strip()}")
        else:
            IPADDR = open(IPADDR_PATH).read().strip()
            if len(IPADDR) == 0:
                IPADDR = input(f"Local IP Address: {open(IPADDR_PATH).read().strip()}")
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"line: {sys.exc_info()[-1].tb_lineno}")

input("Press Enter to exit...")  # Wait for user input before exiting
