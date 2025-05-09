import os
import sys
from time import sleep

is_python_installed = os.system("python3 --version") == 0

if is_python_installed:
    print("Python is installed, proceeding with runtime.")
else:
    if sys.platform == "win32":
        print("Python is not installed, taking you to the microsoft store.")
        os.startfile("ms-windows-store://pdp/?ProductId=9PJPW5LDXLZ2")
    elif sys.platform == "linux":
        print("Python is not installed, taking you to the python website.")
        os.system("xdg-open https://www.python.org/downloads/source/")
    elif sys.platform == "darwin":
        print("Python is not installed, taking you to the apple store.")
        os.system("open https://apps.apple.com/us/app/python-3/id1477388418")
    else:
        print("Python is not installed, please install it manually.")
        sys.exit(1)

while not is_python_installed:
    print("Waiting for Python to be installed...")
    is_python_installed = os.system("python3 --version") == 0
    sleep(5)

# execute the Main.py script in the current directory
os.system("python3 ./Main.py")
