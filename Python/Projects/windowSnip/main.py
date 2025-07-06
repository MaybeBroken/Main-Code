import win32gui
import win32ui
import win32con
import win32api
import win32process
import cv2
import numpy as np
from PIL import Image
import tkinter as tk
from PIL import ImageTk
import ctypes
import ctypes.wintypes  # Explicitly import wintypes
import time
import sys
import os

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


def list_windows():
    """List top-level visible windows."""
    windows = []

    def enum_handler(hwnd, result):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                result.append((hwnd, title))

    win32gui.EnumWindows(enum_handler, windows)
    return windows


def clamp_aspect_ratio(width, height, border_max_width=400, mult_factor=1):
    """Clamp the aspect ratio of the window."""
    if width > border_max_width:
        height = int(height * (border_max_width / width))
        width = border_max_width
    if height > border_max_width:
        width = int(width * (border_max_width / height))
        height = border_max_width
    return int(width * mult_factor), int(height * mult_factor)


def capture_window(hwnd, w, h):
    """Capture the window image."""
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)

    result = user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return bmpinfo, bmpstr, result


def process_image(bmpinfo, bmpstr, w, h):
    """Process the captured image."""
    try:
        img = Image.frombuffer(
            "RGB",
            (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
            bmpstr,
            "raw",
            "BGRX",
            0,
            1,
        )
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except:
        return np.zeros((h, w, 3), np.uint8)


def grab_window(hwnd, bounds=[0, 0, 0, 0]):
    cv2.namedWindow("Live Snip", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    launch = 0
    hwnd_cv = None
    last_w, last_h = 0, 0  # Track previous dimensions
    mult_factor = 1
    start_time = time.time()

    while True:
        try:
            # Use bounds for all calculations
            start_x, start_y, end_x, end_y = bounds
            l, t, r, b = win32gui.GetClientRect(hwnd)
            l, t = win32gui.ClientToScreen(hwnd, (l, t))
            r, b = win32gui.ClientToScreen(hwnd, (r, b))

            # Ensure bounds are within the window's dimensions
            start_x = max(l, l + start_x)
            start_y = max(t, t + start_y)
            end_x = min(r, l + end_x)
            end_y = min(b, t + end_y)

            w = end_x - start_x
            h = end_y - start_y

            if w <= 0 or h <= 0:
                print("Invalid bounds, skipping frame.")
                cv2.imshow("Live Snip", np.zeros((10, 10, 3), np.uint8))
                continue

            if launch == 1:
                for _ in range(10):
                    hwnd_cv = win32gui.FindWindow(None, "Live Snip")
                    if hwnd_cv:
                        break
                    cv2.waitKey(10)
                if hwnd_cv:
                    style = win32gui.GetWindowLong(hwnd_cv, win32con.GWL_STYLE)
                    style &= ~win32con.WS_CAPTION  # Hide the topbar (title bar)
                    style |= win32con.WS_BORDER  # Add a thin border
                    style &= ~win32con.WS_MAXIMIZEBOX
                    win32gui.SetWindowLong(hwnd_cv, win32con.GWL_STYLE, style)
                    win32gui.SetWindowPos(
                        hwnd_cv,
                        win32con.HWND_TOPMOST,
                        start_x,
                        start_y,
                        w,
                        h,
                        win32con.SWP_FRAMECHANGED,
                    )
                    cv2.resizeWindow("Live Snip", w, h)
                    launch = 2

                    def adjust_mult_factor(event, _, __, flags, ___):
                        nonlocal mult_factor
                        if event == cv2.EVENT_MOUSEWHEEL:
                            if flags > 0:  # Scroll up
                                mult_factor += 0.1 * mult_factor
                            elif flags < 0:  # Scroll down
                                mult_factor = max(
                                    0.1, mult_factor - 0.1 * mult_factor
                                )  # Prevent negative values
                            # Apply the updated mult_factor instantly
                            if hwnd_cv and last_w > 0 and last_h > 0:
                                new_w, new_h = clamp_aspect_ratio(
                                    last_w, last_h, mult_factor=mult_factor
                                )
                                win32gui.SetWindowPos(
                                    hwnd_cv,
                                    win32con.HWND_TOPMOST,
                                    0,
                                    0,
                                    new_w,
                                    new_h,
                                    win32con.SWP_NOMOVE | win32con.SWP_FRAMECHANGED,
                                )
                                cv2.resizeWindow("Live Snip", new_w, new_h)

                    cv2.setMouseCallback("Live Snip", adjust_mult_factor)

            bmpinfo, bmpstr, result = capture_window(hwnd, r - l, b - t)
            cvimg = process_image(bmpinfo, bmpstr, r - l, b - t)

            try:
                cropped_img = cvimg[start_y - t : end_y - t, start_x - l : end_x - l]
                win_rect = cv2.getWindowImageRect("Live Snip")
                win_w, win_h = win_rect[2], win_rect[3]
                if win_w > 0 and win_h > 0:
                    cropped_img = cv2.resize(
                        cropped_img, (win_w, win_h), interpolation=cv2.INTER_AREA
                    )
                cv2.imshow("Live Snip", cropped_img)
            except Exception as e:
                print(f"Error cropping or resizing image: {e}")
                cv2.imshow("Live Snip", np.zeros((10, 10, 3), np.uint8))

            if launch >= 2 and hwnd_cv:
                if w != last_w or h != last_h:  # Only resize if dimensions change
                    new_w, new_h = clamp_aspect_ratio(w, h, mult_factor=mult_factor)
                    win32gui.SetWindowPos(
                        hwnd_cv,
                        win32con.HWND_TOPMOST,
                        start_x,
                        start_y,
                        new_w,
                        new_h,
                        win32con.SWP_FRAMECHANGED,
                    )
                    cv2.resizeWindow("Live Snip", new_w, new_h)
                    last_w, last_h = w, h  # Update tracked dimensions

            if cv2.getWindowProperty("Live Snip", cv2.WND_PROP_VISIBLE) < 0:
                break
            if cv2.waitKey(30) & 0xFF == 27:
                break
            if launch == 0:
                hwnd_cv = win32gui.FindWindow(None, "Live Snip")
                if hwnd_cv:
                    win32gui.DestroyWindow(hwnd_cv)
                launch = 1
            if (
                cv2.getWindowProperty("Live Snip", cv2.WND_PROP_VISIBLE) < 1
                and launch == 2
                and time.time() - start_time > 1
            ):
                break

        except Exception as e:
            print(f"error: {e}")
            break

    cv2.destroyAllWindows()
    sys.exit(0)


def bring_window_to_front(hwnd):
    """Bring the chosen window to the front."""
    try:
        # Restore if minimized
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        # Ensure window is not always-on-bottom
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
        )
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_NOTOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
        )

        # Attach input threads if needed
        foreground_hwnd = win32gui.GetForegroundWindow()
        if hwnd != foreground_hwnd:
            current_thread_id = win32api.GetCurrentThreadId()
            foreground_thread_id = win32process.GetWindowThreadProcessId(
                foreground_hwnd
            )[0]
            target_thread_id = win32process.GetWindowThreadProcessId(hwnd)[0]
            if current_thread_id != foreground_thread_id:
                user32.AttachThreadInput(foreground_thread_id, current_thread_id, True)
                user32.AttachThreadInput(target_thread_id, current_thread_id, True)
            win32gui.SetForegroundWindow(hwnd)
            win32gui.BringWindowToTop(hwnd)
            win32gui.SetActiveWindow(hwnd)
            if current_thread_id != foreground_thread_id:
                user32.AttachThreadInput(foreground_thread_id, current_thread_id, False)
                user32.AttachThreadInput(target_thread_id, current_thread_id, False)
        else:
            win32gui.SetForegroundWindow(hwnd)
            win32gui.BringWindowToTop(hwnd)
            win32gui.SetActiveWindow(hwnd)
    except Exception as e:
        print(f"Failed to bring window to front: {e}")


def create_selection_window(hwnd):
    """Create a transparent window for selecting an area."""
    # Get the working area of the desktop (excluding the taskbar)
    screen_working_area = win32gui.GetWindowRect(win32gui.GetDesktopWindow())
    # Use SystemParametersInfo to get the work area (excluding taskbar)
    rect = ctypes.wintypes.RECT()  # Use ctypes.wintypes.RECT directly
    SPI_GETWORKAREA = 0x0030
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_GETWORKAREA, 0, ctypes.byref(rect), 0
    )
    screen_working_area = (rect.left, rect.top, rect.right, rect.bottom)

    selection_root = tk.Tk()
    selection_root.attributes("-alpha", 0.2)  # Transparent background
    selection_root.attributes("-topmost", True)  # Always on top
    selection_root.overrideredirect(True)  # Remove window decorations
    selection_root.geometry(
        f"{screen_working_area[2] - screen_working_area[0]}x{screen_working_area[3] - screen_working_area[1]}+0+0"
    )  # Fullscreen size
    selection_root.title("Select Area")

    selection_canvas = tk.Canvas(selection_root, bg="gray", highlightthickness=0)
    selection_canvas.pack(fill=tk.BOTH, expand=True)

    coords = {"start_x": None, "start_y": None, "end_x": None, "end_y": None}

    def on_mouse_press(event):
        coords["start_x"], coords["start_y"] = event.x, event.y
        selection_canvas.delete("selection_rect")

    def on_mouse_drag(event):
        coords["end_x"], coords["end_y"] = event.x, event.y
        selection_canvas.delete("selection_rect")
        selection_canvas.create_rectangle(
            coords["start_x"],
            coords["start_y"],
            coords["end_x"],
            coords["end_y"],
            outline="red",
            width=2,
            tags="selection_rect",
        )

    def on_mouse_release(event):
        coords["end_x"], coords["end_y"] = event.x, event.y
        selection_root.destroy()

    def on_esc(event):
        sys.exit()

    selection_canvas.bind("<ButtonPress-1>", on_mouse_press)
    selection_canvas.bind("<B1-Motion>", on_mouse_drag)
    selection_canvas.bind("<ButtonRelease-1>", on_mouse_release)
    selection_root.bind("<Escape>", on_esc)
    selection_root.lift()  # Bring the selection window to the front
    selection_root.focus_force()  # Ensure it has focus
    selection_root.mainloop()
    # Translate screen coordinates to local window space
    window_rect = win32gui.GetWindowRect(hwnd)
    coords["start_x"] -= window_rect[0]
    coords["start_y"] -= window_rect[1]
    coords["end_x"] -= window_rect[0]
    coords["end_y"] -= window_rect[1]
    return coords


def pick_window():
    root = tk.Tk()
    root.title("Window Picker")
    frame = tk.Frame(root)
    frame.pack()

    windows = list_windows()
    previews = {}
    listbox = tk.Listbox(frame)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    preview_label = tk.Label(frame)
    preview_label.pack(side=tk.RIGHT)

    for hwnd, title in windows:
        listbox.insert(tk.END, f"{hwnd}: {title}")
        try:
            l, t, r, b = win32gui.GetClientRect(hwnd)
            l, t = win32gui.ClientToScreen(hwnd, (l, t))
            r, b = win32gui.ClientToScreen(hwnd, (r, b))
            w, h = r - l, b - t

            bmpinfo, bmpstr, _ = capture_window(hwnd, w, h)
            img = Image.frombuffer(
                "RGB",
                (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                bmpstr,
                "raw",
                "BGRX",
                0,
                1,
            )
            previews[hwnd] = ImageTk.PhotoImage(img.resize((150, 80)))
        except:
            previews[hwnd] = None

    def on_select(evt):
        idx = listbox.curselection()
        if not idx:
            return
        hwnd_str = listbox.get(idx).split(":")[0]
        h = int(hwnd_str)
        if previews[h]:
            preview_label.config(image=previews[h])
        else:
            preview_label.config(text="No preview")

    listbox.bind("<<ListboxSelect>>", on_select)

    selected_hwnd = tk.IntVar()

    def confirm():
        idx = listbox.curselection()
        if idx:
            hwnd_str = listbox.get(idx).split(":")[0]
            selected_hwnd.set(int(hwnd_str))
        root.destroy()

    tk.Button(root, text="OK", command=confirm).pack()
    root.mainloop()

    hwnd = selected_hwnd.get()
    if hwnd:
        bring_window_to_front(hwnd)
        print("Creating selection window...")
        coords = create_selection_window(hwnd)
        print(f"Selected area: {coords}")
        return hwnd, coords
    return None, None


def main():
    print("Opening window picker...")
    hwnd_pick, coords = pick_window()
    if not hwnd_pick:
        print("No window selected.")
        return
    print(f"Showing live preview of hwnd {hwnd_pick}... press ESC to quit.")
    print(f"Recording area: {coords}")
    grab_window(
        hwnd_pick,
        bounds=[coords["start_x"], coords["start_y"], coords["end_x"], coords["end_y"]],
    )


if __name__ == "__main__":
    main()
