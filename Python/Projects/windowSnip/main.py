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
import ctypes.wintypes
import time
import sys
import os
import keyboard
import winshell
import pythoncom
from win32com.client import Dispatch
import threading
import pystray
from pystray import MenuItem, Menu
from PIL import Image as PilImage
import subprocess
import uuid  # Import for generating unique IDs
from obs_interface import OBSInterface
import json  # Add json import for preferences


user32 = ctypes.windll.user32
DEVMODE = False

pythoncom.CoInitialize()
shell = Dispatch("WScript.Shell")
startup_folder = winshell.startup()
shortcut_path = os.path.join(startup_folder, "WindowGrabHook.lnk")
user_data_dir = os.path.join(os.path.expanduser("~"), ".windowSnip")
if not os.path.exists(user_data_dir):
    os.makedirs(user_data_dir)

# Default preferences
DEFAULT_PREFERENCES = {
    "keybind": "",
    "launch_at_startup": False,
    "extraction_mode": "OBS",  # Default mode: OBS or WIN
}

# Path to preferences file
preferences_file = os.path.join(user_data_dir, "preferences.json")


def load_preferences():
    """Load preferences from JSON file or create default if it doesn't exist"""
    if os.path.exists(preferences_file):
        try:
            with open(preferences_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading preferences: {e}")

    # Check for legacy keybind.txt file
    keybind_file = os.path.join(user_data_dir, "keybind.txt")
    if os.path.exists(keybind_file):
        try:
            with open(keybind_file, "r") as f:
                keybind = f.read().strip()
                prefs = DEFAULT_PREFERENCES.copy()
                prefs["keybind"] = keybind
                prefs["launch_at_startup"] = os.path.exists(shortcut_path)
                return prefs
        except Exception:
            pass

    return DEFAULT_PREFERENCES.copy()


def save_preferences(preferences):
    """Save preferences to JSON file"""
    with open(preferences_file, "w") as f:
        json.dump(preferences, f, indent=4)


# Load preferences at startup
preferences = load_preferences()

if DEVMODE:
    deleteShortcutRequest = input(
        "| DEVMODE: delete shortcut and hotkey association? (RETURN to skip):\n|->"
    )
    if not deleteShortcutRequest == "":
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
        preferences["keybind"] = ""
        save_preferences(preferences)


def get_shortcut_target_info():
    """
    Return the appropriate target path and arguments for creating shortcuts
    based on whether the application is running as a script or executable.

    Returns:
        tuple: (target_path, arguments)
    """
    # Check if running as frozen executable (PyInstaller, cx_Freeze, etc.)
    if getattr(sys, "frozen", False):
        # Running as compiled executable - target the exe directly with no arguments
        return sys.executable, ""
    else:
        # Running as script - use pythonw with script path as argument
        python_path = sys.executable
        pythonw_path = os.path.join(os.path.dirname(python_path), "pythonw.exe")
        if not os.path.exists(pythonw_path):
            pythonw_path = python_path  # Fall back to regular python

        return pythonw_path, f'"{os.path.abspath(__file__)}"'


def set_keybind():
    def on_set_keybind():
        set_button.config(state=tk.DISABLED)
        keybind_result["combo"] = None

        recorded = keyboard.record("enter")
        combo = []
        for event in recorded:
            if (
                event.event_type == "down"
                and event.name not in combo
                and event.name != "enter"
                and event.name != "left"
                and event.name != "right"
            ):
                combo.append(event.name)
        if combo:
            if "left windows" in combo:
                combo[combo.index("left windows")] = "windows"
            keybind_result["combo"] = "+".join(combo).lower()
        keybind_label.config(text=f"Keybind set: {keybind_result['combo']}")
        confirm_button.config(state=tk.NORMAL)
        set_button.config(state=tk.NORMAL)

    def on_confirm():
        combo = keybind_result["combo"]
        if combo:
            preferences["keybind"] = combo
            save_preferences(preferences)
            prompt_label.config(text=f"Keybind '{combo}' saved!")
        else:
            prompt_label.config(text="No keybind selected.")
        confirm_button.config(state=tk.DISABLED)
        set_button.config(state=tk.NORMAL)
        window.destroy()

    def run_gui():
        nonlocal prompt_label, set_button, confirm_button, keybind_label, window
        window = tk.Tk()
        window.title("Set Launch Keybind")
        prompt_label = tk.Label(
            window,
            text="Press your desired launch key combination\nthen press enter when finished",
        )
        prompt_label.pack(padx=10, pady=10)
        keybind_label = tk.Label(window, text="No keybind set")
        keybind_label.pack(padx=10, pady=10)
        set_button = tk.Button(window, text="Set Keybind", command=on_set_keybind)
        set_button.pack(pady=5)
        confirm_button = tk.Button(
            window, text="Confirm", state=tk.DISABLED, command=on_confirm
        )
        confirm_button.pack(pady=10)
        window.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        window.bind("<Escape>", lambda e: sys.exit(0))
        window.focus_force()
        window.mainloop()

    keybind_result = {"combo": None}
    prompt_label = None
    set_button = None
    confirm_button = None
    keybind_label = None
    window = None
    run_gui()


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
        return np.zeros((int(round(h)), int(round(w)), 3), np.uint8)


# Global list to track active snips
active_snips = []


def grab_window(
    hwnd,
    bounds=[0, 0, 0, 0],
    obs_interface: OBSInterface = None,
    obs_initalize_sucess: bool | None = None,
    wm_info: dict | None = None,
):
    global active_snips

    # Check if the window is already being snipped
    if hwnd in active_snips:
        print(f"Window {hwnd} is already being snipped. Skipping duplicate snip.")
        raise HotkeyExit

    # Mark the window as being snipped
    active_snips.append(hwnd)

    try:
        window_title = win32gui.GetWindowText(hwnd)  # Get the window title
        unique_id = str(uuid.uuid4())[:8]  # Generate a short unique ID
        dynamic_window_name = f"{window_title} - {unique_id}"  # Combine title and ID

        cv2.namedWindow(dynamic_window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        launch = 0
        hwnd_cv = None
        last_w, last_h = 0, 0  # Track previous dimensions
        mult_factor = 1
        start_time = time.time()
        drag_start = None  # Track drag start position

        global_pos_x, global_pos_y = 0.0, 0.0
        global_width, global_height = bounds[2] - bounds[0], bounds[3] - bounds[1]
        global_width, global_height = clamp_aspect_ratio(
            global_width, global_height, mult_factor=mult_factor
        )

        def on_mouse_drag(event, x, y, flags, param):
            nonlocal drag_start, hwnd_cv
            if event == cv2.EVENT_LBUTTONDOWN:
                drag_start = (x, y)
            elif event == cv2.EVENT_MOUSEMOVE and drag_start:
                dx, dy = x - drag_start[0], y - drag_start[1]
                if hwnd_cv:
                    win_rect = win32gui.GetWindowRect(hwnd_cv)
                    new_x = win_rect[0] + dx
                    new_y = win_rect[1] + dy
                    win32gui.SetWindowPos(
                        hwnd_cv,
                        win32con.HWND_TOPMOST,
                        new_x,
                        new_y,
                        win_rect[2] - win_rect[0],
                        win_rect[3] - win_rect[1],
                        win32con.SWP_FRAMECHANGED,
                    )
            elif event == cv2.EVENT_LBUTTONUP:
                drag_start = None

        while True:
            try:
                # Check if the window is minimized
                if win32gui.IsIconic(hwnd):
                    cv2.imshow(
                        dynamic_window_name,
                        np.zeros(
                            (int(round(global_height)), int(round(global_width)), 3),
                            np.uint8,
                        ),
                    )
                    cv2.waitKey(30)  # Prevent blocking
                    continue

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
                    cv2.imshow(
                        dynamic_window_name,
                        np.zeros(
                            (int(round(global_height)), int(round(global_width)), 3),
                            np.uint8,
                        ),
                    )
                    cv2.waitKey(30)  # Prevent blocking
                    continue

                # Handle window initialization
                if launch == 1:
                    for _ in range(10):
                        hwnd_cv = win32gui.FindWindow(None, dynamic_window_name)
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
                        cv2.resizeWindow(
                            dynamic_window_name, int(round(w)), int(round(h))
                        )
                        launch = 2

                        def adjust_mult_factor(event, x, y, flags, param):
                            on_mouse_drag(event, x, y, flags, param)
                            nonlocal mult_factor, last_w, last_h, global_pos_x, global_pos_y, global_width, global_height
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

                                    # Calculate new top-left position to keep the center fixed
                                    win_rect = win32gui.GetWindowRect(hwnd_cv)
                                    cur_x, cur_y = win_rect[0], win_rect[1]
                                    center_x = cur_x + (win_rect[2] - win_rect[0]) / 2.0
                                    center_y = cur_y + (win_rect[3] - win_rect[1]) / 2.0
                                    global_pos_x = center_x - new_w / 2.0
                                    global_pos_y = center_y - new_h / 2.0

                                    # Apply new position and size (rounded for Windows API calls)
                                    global_width, global_height = new_w, new_h
                                    win32gui.SetWindowPos(
                                        hwnd_cv,
                                        win32con.HWND_TOPMOST,
                                        int(round(global_pos_x)),
                                        int(round(global_pos_y)),
                                        int(round(global_width)),
                                        int(round(global_height)),
                                        win32con.SWP_FRAMECHANGED,
                                    )
                                    cv2.resizeWindow(
                                        dynamic_window_name,
                                        int(round(global_width)),
                                        int(round(global_height)),
                                    )

                        cv2.setMouseCallback(dynamic_window_name, adjust_mult_factor)
                        # Hide the window from the taskbar and minimize to tray
                        import win32com.client

                        # Hide from taskbar
                        ex_style = win32gui.GetWindowLong(hwnd_cv, win32con.GWL_EXSTYLE)
                        ex_style |= win32con.WS_EX_TOOLWINDOW
                        ex_style &= ~win32con.WS_EX_APPWINDOW
                        win32gui.SetWindowLong(hwnd_cv, win32con.GWL_EXSTYLE, ex_style)

                # Cache for OBS processing parameters
                obs_cache = getattr(
                    grab_window,
                    "_obs_cache",
                    {
                        "screen_rect": None,
                        "taskbar_height": None,
                        "last_window_dims": None,
                        "scaling_factors": None,
                    },
                )

                # Capture frame using OBS or Windows API based on mode
                if (
                    obs_interface
                    and obs_initalize_sucess
                    and preferences.get("extraction_mode") == "OBS"
                ):
                    # OBS mode: Get screenshot from OBS
                    try:
                        # Prepare screen dimensions cache (calculate only once)
                        if obs_cache["screen_rect"] is None:
                            obs_cache["screen_rect"] = (
                                0,
                                0,
                                user32.GetSystemMetrics(0),
                                user32.GetSystemMetrics(1),
                            )
                            work_rect = ctypes.wintypes.RECT()
                            ctypes.windll.user32.SystemParametersInfoW(
                                0x0030, 0, ctypes.byref(work_rect), 0
                            )
                            obs_cache["taskbar_height"] = (
                                obs_cache["screen_rect"][3] - work_rect.bottom
                            )

                        # Get the actual window dimensions
                        window_w, window_h = r - l, b - t
                        current_dims = (
                            window_w,
                            window_h,
                            start_x - l,
                            start_y - t,
                            end_x - start_x,
                            end_y - start_y,
                        )

                        # Only recalculate scaling factors if window dimensions changed
                        if obs_cache["last_window_dims"] != current_dims:
                            obs_cache["last_window_dims"] = current_dims
                            # Get the screenshot once to determine dimensions
                            obs_screenshot = obs_interface.get_screenshot(1920, 1080)
                            if obs_screenshot is not None:
                                # Pre-calculate all scaling factors
                                obs_h, obs_w = obs_screenshot.shape[:2]

                                # Apply taskbar adjustment to OBS height
                                if obs_cache["taskbar_height"] > 0:
                                    crop_pixels = int(
                                        (
                                            obs_cache["taskbar_height"]
                                            / obs_cache["screen_rect"][3]
                                        )
                                        * obs_h
                                    )
                                    obs_h_adjusted = obs_h - crop_pixels
                                else:
                                    obs_h_adjusted = obs_h
                                    crop_pixels = 0

                                # Store all scaling parameters
                                obs_cache["scaling_factors"] = {
                                    "obs_w": obs_w,
                                    "obs_h": obs_h,
                                    "obs_h_adjusted": obs_h_adjusted,
                                    "crop_pixels": crop_pixels,
                                    "scale_x": obs_w / window_w if window_w > 0 else 1,
                                    "scale_y": (
                                        obs_h_adjusted / window_h if window_h > 0 else 1
                                    ),
                                    "window_aspect": (
                                        window_w / window_h if window_h > 0 else 1
                                    ),
                                    "obs_aspect": (
                                        obs_w / obs_h_adjusted
                                        if obs_h_adjusted > 0
                                        else 1
                                    ),
                                }

                                # Determine which scaling to use based on aspect ratios
                                sf = obs_cache["scaling_factors"]
                                if abs(sf["window_aspect"] - sf["obs_aspect"]) < 0.01:
                                    sf["scale"] = sf[
                                        "scale_x"
                                    ]  # Nearly identical aspect ratios
                                elif sf["window_aspect"] > sf["obs_aspect"]:
                                    sf["scale"] = sf["scale_x"]  # Window is wider
                                else:
                                    sf["scale"] = sf["scale_y"]  # Window is taller

                        # Fast path for actual screenshot processing with cached parameters
                        obs_screenshot = obs_interface.get_screenshot(1920, 1080)
                        if (
                            obs_screenshot is not None
                            and obs_cache["scaling_factors"] is not None
                        ):
                            sf = obs_cache["scaling_factors"]

                            # Fast crop of taskbar area using direct slicing
                            if sf["crop_pixels"] > 0:
                                obs_screenshot = obs_screenshot[: -sf["crop_pixels"]]

                            # Direct calculation of crop coordinates using cached scaling factors
                            rel_x, rel_y = start_x - l, start_y - t
                            rel_w, rel_h = end_x - start_x, end_y - start_y

                            # Use numpy's efficient array operations for cropping
                            crop_x = max(
                                0, min(int(rel_x * sf["scale_x"]), sf["obs_w"] - 1)
                            )
                            crop_y = max(
                                0,
                                min(
                                    int(rel_y * sf["scale_y"]), sf["obs_h_adjusted"] - 1
                                ),
                            )
                            crop_w = max(
                                1, min(int(rel_w * sf["scale_x"]), sf["obs_w"] - crop_x)
                            )
                            crop_h = max(
                                1,
                                min(
                                    int(rel_h * sf["scale_y"]),
                                    sf["obs_h_adjusted"] - crop_y,
                                ),
                            )

                            # Extract region using direct numpy slicing (creates a view, not a copy)
                            cropped_img = obs_screenshot[
                                crop_y : crop_y + crop_h, crop_x : crop_x + crop_w
                            ]

                            # Only resize if necessary
                            win_rect = cv2.getWindowImageRect(dynamic_window_name)
                            win_w, win_h = win_rect[2], win_rect[3]
                            if (
                                win_w > 0
                                and win_h > 0
                                and (
                                    abs(win_w - cropped_img.shape[1]) > 2
                                    or abs(win_h - cropped_img.shape[0]) > 2
                                )
                            ):
                                cropped_img = cv2.resize(
                                    cropped_img,
                                    (win_w, win_h),
                                    interpolation=cv2.INTER_LINEAR,
                                )

                            cv2.imshow(dynamic_window_name, cropped_img)
                    except Exception as e:
                        print(
                            f"OBS screenshot failed: {e}, falling back to Windows API"
                        )
                        # Fall back to Windows API capture if OBS fails
                        bmpinfo, bmpstr, result = capture_window(hwnd, r - l, b - t)
                        cvimg = process_image(bmpinfo, bmpstr, r - l, b - t)
                        try:
                            cropped_img = cvimg[
                                start_y - t : end_y - t, start_x - l : end_x - l
                            ]
                            win_rect = cv2.getWindowImageRect(dynamic_window_name)
                            win_w, win_h = win_rect[2], win_rect[3]
                            if (
                                win_w > 0
                                and win_h > 0
                                and (
                                    win_w != cropped_img.shape[1]
                                    or win_h != cropped_img.shape[0]
                                )
                            ):
                                cropped_img = cv2.resize(
                                    cropped_img,
                                    (win_w, win_h),
                                    interpolation=cv2.INTER_AREA,
                                )
                            cv2.imshow(dynamic_window_name, cropped_img)
                        except Exception:
                            cv2.imshow(
                                dynamic_window_name,
                                np.zeros(
                                    (
                                        int(round(global_height)),
                                        int(round(global_width)),
                                        3,
                                    ),
                                    np.uint8,
                                ),
                            )
                else:
                    # Windows API mode: Use direct window capture
                    bmpinfo, bmpstr, result = capture_window(hwnd, r - l, b - t)
                    cvimg = process_image(bmpinfo, bmpstr, r - l, b - t)
                    try:
                        cropped_img = cvimg[
                            start_y - t : end_y - t, start_x - l : end_x - l
                        ]
                        win_rect = cv2.getWindowImageRect(dynamic_window_name)
                        win_w, win_h = win_rect[2], win_rect[3]
                        if (
                            win_w > 0
                            and win_h > 0
                            and (
                                win_w != cropped_img.shape[1]
                                or win_h != cropped_img.shape[0]
                            )
                        ):
                            cropped_img = cv2.resize(
                                cropped_img,
                                (win_w, win_h),
                                interpolation=cv2.INTER_AREA,
                            )
                        cv2.imshow(dynamic_window_name, cropped_img)
                    except Exception as e:
                        cv2.imshow(
                            dynamic_window_name,
                            np.zeros(
                                (
                                    int(round(global_height)),
                                    int(round(global_width)),
                                    3,
                                ),
                                np.uint8,
                            ),
                        )

                if launch >= 2 and hwnd_cv:
                    if w != last_w or h != last_h:  # Only resize if dimensions change
                        new_w, new_h = clamp_aspect_ratio(w, h, mult_factor=mult_factor)
                        global_width, global_height = new_w, new_h
                        global_pos_x, global_pos_y = start_x, start_y
                        win32gui.SetWindowPos(
                            hwnd_cv,
                            win32con.HWND_TOPMOST,
                            int(round(global_pos_x)),
                            int(round(global_pos_y)),
                            int(round(global_width)),
                            int(round(global_height)),
                            win32con.SWP_FRAMECHANGED,
                        )
                        cv2.resizeWindow(
                            dynamic_window_name,
                            int(round(global_width)),
                            int(round(global_height)),
                        )
                        last_w, last_h = w, h  # Update tracked dimensions

                if cv2.getWindowProperty(dynamic_window_name, cv2.WND_PROP_VISIBLE) < 0:
                    break
                if cv2.waitKey(30) & 0xFF == 27:
                    break
                if launch == 0:
                    hwnd_cv = win32gui.FindWindow(None, dynamic_window_name)
                    if hwnd_cv:
                        win32gui.DestroyWindow(hwnd_cv)
                    launch = 1
                if (
                    cv2.getWindowProperty(dynamic_window_name, cv2.WND_PROP_VISIBLE) < 1
                    and launch == 2
                    and time.time() - start_time > 1
                ):
                    break

            except Exception as e:
                print(f"error: {e}")
                break

    finally:
        # Ensure the window is removed from the active snips list
        if hwnd in active_snips:
            active_snips.remove(hwnd)
        cv2.destroyWindow(dynamic_window_name)
        raise HotkeyExit


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


def get_tk_hwnd(root):
    """Get the HWND of the Tkinter root window (Windows only)."""
    hwnd = root.winfo_id()
    # Ensure we get the real HWND (sometimes winfo_id returns a child widget id)
    return ctypes.windll.user32.GetParent(hwnd) or hwnd


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
    selection_root.attributes("-alpha", 0.35)  # Transparent background
    selection_root.attributes("-topmost", True)  # Always on top
    selection_root.overrideredirect(True)  # Remove window decorations
    selection_root.geometry(
        f"{screen_working_area[2] - screen_working_area[0]}x{screen_working_area[3] - screen_working_area[1]}+0+0"
    )  # Fullscreen size
    selection_root.title("Select Area")

    selection_canvas = tk.Canvas(selection_root, bg="black", highlightthickness=0)
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
            outline="white",
            width=2,
            tags="selection_rect",
        )

    def on_mouse_release(event):
        coords["end_x"], coords["end_y"] = event.x, event.y
        selection_root.destroy()

    def on_esc(event):
        print("Selection cancelled.")
        selection_root.destroy()
        return HotkeyExit

    selection_canvas.bind("<ButtonPress-1>", on_mouse_press)
    selection_canvas.bind("<B1-Motion>", on_mouse_drag)
    selection_canvas.bind("<ButtonRelease-1>", on_mouse_release)
    selection_root.bind("<Escape>", on_esc)
    selection_root.focus_force()  # Ensure it has focus
    bring_window_to_front(get_tk_hwnd(selection_root))
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
    root.lift()
    root.focus_force()

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
        if coords == HotkeyExit:
            return HotkeyExit
        print(f"Selected area: {coords}")
        return hwnd, coords
    return None, None


def get_active_window():
    """Return the currently active window and its full area as a coords dict."""
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return None, None
    bring_window_to_front(hwnd)
    coords = create_selection_window(hwnd)
    if coords == HotkeyExit:
        return HotkeyExit
    return hwnd, coords


def main():
    if not preferences["keybind"]:
        return

    if DEVMODE:
        hwnd_pick, coords = pick_window()
    else:
        hwnd_pick, coords = get_active_window()

    if not hwnd_pick:
        return
    if hwnd_pick == HotkeyExit:
        raise HotkeyExit

    if preferences["extraction_mode"] == "OBS":
        # OBS mode - use OBS interface
        window_info = obs_interface.get_window_by_hwnd(hwnd_pick)
        source_name = "WindowCapture"
        success = obs_interface.set_window_capture(source_name, window_info)
        print(
            f"Showing live preview of hwnd {hwnd_pick} using OBS mode... press ESC to quit."
        )
    else:
        # WIN mode - just use direct window capture without OBS
        window_info = None
        success = None
        print(
            f"Showing live preview of hwnd {hwnd_pick} using WIN mode... press ESC to quit."
        )

    print(f"Recording area: {coords}")
    grab_window(
        hwnd_pick,
        bounds=[coords["start_x"], coords["start_y"], coords["end_x"], coords["end_y"]],
        obs_interface=(
            obs_interface if preferences["extraction_mode"] == "OBS" else None
        ),
        obs_initalize_sucess=success,
        wm_info=window_info,
    )


class HotkeyExit(BaseException):
    """Custom exception to exit the hotkey listener."""

    pass


def _th():
    try:
        main()
    except HotkeyExit:
        pass
    except Exception as e:
        print(f"Error in hotkey listener: {e}")
        time.sleep(1)


def wait_for_hotkey_and_run():
    while True:
        if not preferences["keybind"]:
            time.sleep(0.1)
            continue

        combo = preferences["keybind"]
        print(f"Waiting for hotkey: {combo}")
        keyboard.wait(combo)
        threading.Thread(target=_th).start()


def clear_keybind(icon, item: MenuItem):
    """Clear the saved keybind."""
    preferences["keybind"] = ""
    save_preferences(preferences)
    print("Keybind cleared.")
    item._text = item._wrap("Set Keybind")
    item._action = lambda icon, item=item: [
        set_keybind(),
        setattr(item, "_text", item._wrap("Clear Keybind")),
        icon._update_menu(),
    ]
    icon._update_menu()


def toggle_launch_at_startup(icon, item: MenuItem):
    """Toggle the launch at Windows startup."""
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
        preferences["launch_at_startup"] = False
        print("Launch at startup disabled.")
        item._checked = item._wrap(False)
    else:
        target_path, arguments = get_shortcut_target_info()
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target_path
        shortcut.Arguments = arguments
        shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(__file__))
        shortcut.save()
        preferences["launch_at_startup"] = True
        print("Launch at startup enabled.")
        item._checked = item._wrap(True)
    save_preferences(preferences)
    icon._update_menu()


def toggle_extraction_mode(icon, item: MenuItem):
    """Toggle between OBS and WIN extraction modes."""
    if preferences["extraction_mode"] == "OBS":
        preferences["extraction_mode"] = "WIN"
        item._text = item._wrap("Mode: WIN (Switch to OBS)")
    else:
        preferences["extraction_mode"] = "OBS"
        item._text = item._wrap("Mode: OBS (Switch to WIN)")
    save_preferences(preferences)
    icon._update_menu()


def exit_program(icon):
    """Exit the program."""
    icon.stop()


def restart_program(icon):
    """Restart the program."""
    icon.stop()
    subprocess.Popen([sys.executable] + sys.argv)


def create_tray_icon():
    """Create and run the tray icon."""

    def setup(icon):
        icon.visible = True
        if not preferences["keybind"]:
            icon.notify(
                "open taskbar menu to configure",
                "WindowSnip is not configured",
            )
            return
        else:
            keybind = preferences["keybind"]
            if not keybind:
                icon.notify(
                    "open taskbar menu to configure",  # Fixed typo from "openF" to "open"
                    "WindowSnip is not configured",
                )
                return
        icon.notify(
            "press " + keybind + " to capture a window",
            "WindowSnip is running",
        )

    tray_icon_path = "./tray.png"
    if os.path.exists(tray_icon_path):
        tray_image = PilImage.open(tray_icon_path)
    else:
        tray_image = PilImage.new("RGB", (64, 64), (0, 0, 0))  # Fallback: black square

    # Set up menu items based on current preferences
    keybind_action_text = "Clear Keybind" if preferences["keybind"] else "Set Keybind"
    keybind_action = lambda icon, item=None: (
        clear_keybind(icon, clear_keybind_item)
        if preferences["keybind"]
        else threading.Thread(target=set_keybind, daemon=True).start()
    )

    clear_keybind_item = MenuItem(
        keybind_action_text,
        keybind_action,
    )

    toggle_launch_item = MenuItem(
        "Launch at Windows Startup",
        lambda icon: toggle_launch_at_startup(icon, toggle_launch_item),
        radio=False,
        checked=clear_keybind_item._wrap(preferences["launch_at_startup"]),
    )

    mode_text = f"Mode: {preferences['extraction_mode']} (Switch to {'WIN' if preferences['extraction_mode'] == 'OBS' else 'OBS'})"
    mode_toggle_item = MenuItem(
        mode_text,
        lambda icon: toggle_extraction_mode(icon, mode_toggle_item),
    )

    menu = Menu(
        clear_keybind_item,
        toggle_launch_item,
        mode_toggle_item,
        MenuItem("Restart", lambda icon: restart_program(icon)),
        MenuItem("Exit", lambda icon: exit_program(icon)),
    )

    icon = pystray.Icon("WindowSnip", tray_image, "WindowSnip", menu)
    try:
        icon.run(setup)
    except SystemExit:
        pass


# Modify the main program to start the tray icon
if __name__ == "__main__":
    obs_interface = OBSInterface()
    obs_interface.set_current_scene("Scene")
    t = threading.Thread(target=wait_for_hotkey_and_run, daemon=True)
    t.start()
    create_tray_icon()
