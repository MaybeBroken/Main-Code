import win32gui
import win32con
import win32api
import tkinter as tk
import subprocess

# Register a window class
wc = win32gui.WNDCLASS()
wc.lpfnWndProc = win32gui.DefWindowProc
wc.lpszClassName = "LeftClickUtil"
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

# Create a small frame window
root = tk.Tk()
root.attributes("-topmost", True)  # Ensure the Tkinter window is always on top
root.wm_attributes("-toolwindow", True)  # Hide the window from the taskbar
root.wm_overrideredirect(True)

# Set the size and position of the window
window_width = 200
window_height = 300
root.geometry(
    f"{window_width}x{window_height}+{root.winfo_pointerx()}+{root.winfo_pointery()}"
)

# Create a frame to hold the buttons
frame = tk.Frame(root, bg="white")
frame.pack(fill=tk.BOTH, expand=True)


# Function to run custom scripts
def run_script(name, script):
    try:
        hwnd = subprocess.Popen(script)
        win32gui.SetForegroundWindow(hwnd)
        root.quit()
    except FileNotFoundError:
        notifyText = tk.Label(frame, text=f"Script '{name}' not found", fg="red")
        print(f"Script '{script}' not found")
        notifyText.pack(pady=5, padx=10, fill=tk.X)
        root.after(1000, lambda: notifyText.destroy())


# Create buttons and add them to the frame
button_names = [
    ["youtubeDownloader", ["python3", "scripts/youtubeDownloader.py"]],
    ["explorer", "explorer"],
    ["cmd", "cmd"],
    [
        "mediaPlayer",
        ["python3", "scripts/mediaPlayer.py"],
    ],
]
for name, script in button_names:
    button = tk.Button(
        frame, text=name, command=lambda n=name, s=script: run_script(n, s)
    )
    button.pack(pady=5, padx=10, fill=tk.X)


# Function to exit the program when the window loses focus
def on_focus_out(event):
    root.quit()


# Bind the focus out event to the function
root.bind("<FocusOut>", on_focus_out)

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
