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


# Set the position of the Tkinter window (e.g., 100 pixels from the left and 100 pixels from the top)

# Open the transparent PNG image and display it on the Tkinter window
image = Image.open("vsCode.png").convert("RGBA")
# Resize the image
image = image.resize((int(image.width * 0.25), int(image.height * 0.25)))
photo = ImageTk.PhotoImage(image)

screen_width = win32api.GetSystemMetrics(0)
screen_height = win32api.GetSystemMetrics(1)
xOffset = (screen_width // 2) - image.width // 2
yOffset = (screen_height // 2) - image.height // 2

label = tk.Label(
    root, image=photo, bg="white"
)  # Set the background color to match the transparency color
label.pack()

loadingProgressBar = tk.Canvas(root, width=800, height=10)
loadingProgressBar.pack()

root.geometry(f"+{xOffset-(image.width//2)}+{yOffset-(image.height//2)}")

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

loading_progress = 0


def scale_image():
    def bezier_interpolation(t, p0, p1, p2, p3):
        return (
            (1 - t) ** 3 * p0
            + 3 * (1 - t) ** 2 * t * p1
            + 3 * (1 - t) * t**2 * p2
            + t**3 * p3
        )

    t = 0
    direction = 1
    control_points = [0.25, 0.35, 0.45, 0.5]
    while True:
        time.sleep(0.025)
        t += direction * 0.01
        if t >= 1 or t <= 0:
            direction *= -1
        scale_factor = bezier_interpolation(t, *control_points)
        resized_image = image.resize(
            (int(image.width * scale_factor), int(image.height * scale_factor))
        )
        photo = ImageTk.PhotoImage(resized_image)
        label.config(image=photo)
        label.image = photo
        label.pack(
            anchor="center",
            ipadx=image.width - resized_image.width // 2,
            ipady=image.height - resized_image.height // 2,
        )
        progress = int(1 * 400)
        loadingProgressBar.delete("all")
        loadingProgressBar.create_rectangle(0, 0, 2 * progress, 10, fill="blue")
        root.update_idletasks()


# Start the scaling thread
scaling_thread = threading.Thread(target=scale_image, daemon=True)
scaling_thread.start()
root.mainloop()
