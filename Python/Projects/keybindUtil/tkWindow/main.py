import win32gui
import win32con
import win32api

# Register a window class
wc = win32gui.WNDCLASS()
wc.lpfnWndProc = win32gui.DefWindowProc
wc.lpszClassName = "MyWindowClass"
win32gui.RegisterClass(wc)

# Create a transparent window
hwnd = win32gui.CreateWindowEx(
    win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT,
    wc.lpszClassName,
    "",
    win32con.WS_POPUP | win32con.WS_VISIBLE,
    0,
    0,
    win32con.CW_USEDEFAULT,
    win32con.CW_USEDEFAULT,
    0,
    0,
    0,
    None,
)

# Set the window's background color to be completely transparent
win32gui.SetLayeredWindowAttributes(
    hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY
)

import tkinter as tk
from PIL import Image, ImageTk
import threading
import time

# Create a Tkinter window and set its background color to be completely transparent
root = tk.Tk()
root.overrideredirect(1)
root.attributes("-topmost", True)  # Ensure the Tkinter window is always on top
root.attributes("-transparentcolor", "white")  # Set transparency color
root.configure(bg="white")  # Set the background color to white


screen_width = win32api.GetSystemMetrics(0)
screen_height = win32api.GetSystemMetrics(1)
root.geometry(f"{screen_width}x{screen_height}")

# Create a tiny tab in the corner
tab = tk.Button(root, text="", bg="SystemButtonFace", width=1, height=2)
tab.pack(side=tk.LEFT, anchor="nw")

# Frame to hold the buttons
button_frame = tk.Frame(root, bg="white")
button_frame.pack(side=tk.LEFT, anchor="nw")
button_frame.pack_forget()  # Hide the button frame initially

# Dictionary to store the registered windows
registered_windows = {}


# Function to register or bring the window to the foreground
def handle_button_click(button_name, button):
    if button_name in registered_windows:
        win32gui.SetForegroundWindow(registered_windows[button_name])
    else:
        time.sleep(2)
        hwnd = win32gui.GetForegroundWindow()
        registered_windows[button_name] = hwnd
        window_text = win32gui.GetWindowText(hwnd)
        button.config(text=window_text)


window1Button = tk.Button(
    button_frame,
    text="Window 1",
    bg="SystemButtonFace",
    command=lambda: handle_button_click("Window 1", window1Button),
)
window1Button.pack(side=tk.LEFT)
window2Button = tk.Button(
    button_frame,
    text="Window 2",
    bg="SystemButtonFace",
    command=lambda: handle_button_click("Window 2", window2Button),
)
window2Button.pack(side=tk.LEFT)
window3Button = tk.Button(
    button_frame,
    text="Window 3",
    bg="SystemButtonFace",
    command=lambda: handle_button_click("Window 3", window3Button),
)
window3Button.pack(side=tk.LEFT)


# Function to show/hide the button frame
def toggle_buttons():
    if button_frame.winfo_ismapped():
        button_frame.pack_forget()
    else:
        button_frame.pack(side=tk.LEFT, anchor="nw")


tab.config(command=toggle_buttons)

# Position the overlay on top of the desktop
win32gui.SetWindowPos(
    hwnd,
    win32con.HWND_TOPMOST,
    0,
    0,
    win32api.GetSystemMetrics(0),
    win32api.GetSystemMetrics(1),
    win32con.SWP_SHOWWINDOW,
)

root.mainloop()
