import ctypes
import numpy as np
import cv2
import time
import sys
cap = ctypes.cdll.LoadLibrary(r"./ScreenCaptureDLL.dll")

user32 = ctypes.windll.user32


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not is_admin():
    # Relaunch the script with admin rights and hide the terminal window
    script = sys.argv[0]
    params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
    SW_HIDE = 0  # 0 = hidden, 1 = normal, 2 = minimized, 3 = maximized
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{script}" {params}', None, SW_HIDE
    )
    sys.exit()

# define signatures
cap.start_capture.argtypes = [ctypes.c_wchar_p]
cap.start_capture.restype = ctypes.c_bool
cap.get_frame.restype = ctypes.c_bool
cap.get_frame.argtypes = [
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
]
cap.stop_capture.restype = None

# pick your window title exactly
window_title = "Task Manager"

if not cap.start_capture(window_title):
    print("Failed to start capture")
    exit(1)

# assuming max 1920x1080
BUF_SIZE = 1920 * 1080 * 4
buf = (ctypes.c_uint8 * BUF_SIZE)()
w = ctypes.c_int()
h = ctypes.c_int()

try:
    while True:
        ok = cap.get_frame(buf, ctypes.byref(w), ctypes.byref(h))
        if ok:
            frame = np.frombuffer(buf, dtype=np.uint8, count=w.value * h.value * 4)
            frame = frame.reshape((h.value, w.value, 4))
            cv2.imshow("Window Capture", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            time.sleep(0.01)
finally:
    cap.stop_capture()
    cv2.destroyAllWindows()
