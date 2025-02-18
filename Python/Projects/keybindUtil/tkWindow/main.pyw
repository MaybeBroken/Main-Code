import win32gui
import win32con
import win32api
import tkinter as tk
import threading
import time

# Register a window class
wc = win32gui.WNDCLASS()
wc.lpfnWndProc = win32gui.DefWindowProc
wc.lpszClassName = "MyWindowClass"
win32gui.RegisterClass(wc)

# Create a transparent window
root_hwnd = win32gui.CreateWindowEx(
    win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOOLWINDOW,
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
    root_hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY
)


# Create a Tkinter window and set its background color to be completely transparent
root = tk.Tk()
root.attributes("-topmost", True)  # Ensure the Tkinter window is always on top
root.attributes("-transparentcolor", "white")  # Set transparency color
root.configure(bg="white")  # Set the background color to white
root.wm_attributes("-toolwindow", True)  # Hide the window from the taskbar
root.wm_overrideredirect(True)

screen_width = win32api.GetSystemMetrics(0)
screen_height = win32api.GetSystemMetrics(1)
root.geometry(f"{screen_width}x{screen_height}-4-4")

# Create a tiny tab in the corner
tab = tk.Button(root, text="", bg="SystemButtonFace", width=1, height=2)
tab.pack(side=tk.LEFT, anchor="nw")
# Button to close the program
# Frame to hold the buttons
button_frame = tk.Frame(root, bg="white")
button_frame.pack(side=tk.LEFT, anchor="nw")
button_frame.pack_forget()  # Hide the button frame initially
close_button = tk.Button(
    button_frame, text="Quit", bg="SystemButtonFace", command=root.quit
)
close_button.pack(side=tk.RIGHT, fill=tk.X)

# Dictionary to store the registered windows
registered_windows = {}
button_count = 0


# Function to register or bring the window to the foreground
def handle_button_click(button_name, button):
    try:
        if button_name in registered_windows:
            win32gui.SetForegroundWindow(registered_windows[button_name])
            toggle_buttons()
        else:
            hwnd1 = win32gui.GetForegroundWindow()
            while True:
                hwnd = win32gui.GetForegroundWindow()
                if hwnd != hwnd1:
                    registered_windows[button_name] = hwnd
                    window_text = win32gui.GetWindowText(hwnd).split(" - ")[-1]
                    button.config(text=window_text)
                    break
                else:
                    pass
                time.sleep(0.1)
    except:
        pass


# Function to delete a button
def _delete_button(button_name, button_frame):
    button_frame.destroy()
    global button_count
    button_count -= 1
    if button_name in registered_windows:
        del registered_windows[button_name]


# Function to add a new button
def add_button():
    global button_count
    button_count += 1
    button_name = f"Window {button_count}"

    new_button_frame = tk.Frame(button_frame, bg="white")
    new_button_frame.pack(side=tk.LEFT, fill=tk.X)

    new_button = tk.Button(
        new_button_frame,
        text=button_name,
        bg="SystemButtonFace",
        command=lambda: threading.Thread(
            target=handle_button_click, args=(button_name, new_button)
        ).start(),
    )
    new_button.pack(side=tk.LEFT)

    delete_button = tk.Button(
        new_button_frame,
        text="X",
        bg="#FF9999",  # Slightly redder color
        command=lambda: _delete_button(button_name, new_button_frame),
    )
    delete_button.pack(side=tk.LEFT)


# Initial button to add new buttons
add_button_button = tk.Button(
    button_frame, text="Add Window", bg="SystemButtonFace", command=add_button
)
add_button_button.pack(side=tk.RIGHT, fill=tk.X)


# Function to show/hide the button frame
def toggle_buttons():
    if button_frame.winfo_ismapped():
        button_frame.pack_forget()
    else:
        button_frame.pack(side=tk.LEFT, anchor="nw")


tab.config(command=toggle_buttons)

# Position the overlay on top of the desktop
win32gui.SetWindowPos(
    root_hwnd,
    win32con.HWND_TOPMOST,
    0,
    0,
    win32api.GetSystemMetrics(0),
    win32api.GetSystemMetrics(1),
    win32con.SWP_SHOWWINDOW,
)

root.mainloop()
