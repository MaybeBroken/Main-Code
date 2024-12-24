import subprocess
import keyboard
import time

if __name__ == "__main__":
    keyboard.add_hotkey("ctrl + win + k", subprocess.Popen, args=["pythonw main.pyw"])
    keyboard.add_hotkey("ctrl + win + e", exit)
    while True:
        time.sleep(1)
