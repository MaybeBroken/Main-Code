import subprocess
import keyboard
import time
import ctypes
import sys

if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 0
        )

        sys.exit()
    keyboard.add_hotkey("ctrl + win + k", subprocess.Popen, args=["pythonw main.pyw"])
    subprocess.Popen(["taskmgr"])
    subprocess.Popen(["pythonw", "tkWindow/main.pyw"])
    while True:
        time.sleep(1)
