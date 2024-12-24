import subprocess
import time
import ctypes
import sys
import keyboard

if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 0
        )

        sys.exit()
    subprocess.Popen(["taskmgr"])
    subprocess.Popen(["pythonw", "tkWindow/main.pyw"])
    keyboard.add_hotkey(
        "ctrl + win + t", lambda: subprocess.Popen(["pythonw", "tkWindow/main.pyw"])
    )
    while True:
        time.sleep(1)
