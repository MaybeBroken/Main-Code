import sys
import subprocess
import logging

if not sys.platform.startswith("win"):
    raise OSError("This module is only available on Windows.")


def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        __import__(package)
        print(f"Installed and imported {package} successfully.")


try:
    import win32gui  # type: ignore
    import win32con  # type: ignore
    import win32api  # type: ignore
    import win32process  # type: ignore
except ImportError:
    install_and_import("pywin32")
    import win32gui  # type: ignore
    import win32con  # type: ignore
    import win32api  # type: ignore
    import win32process  # type: ignore

# Configure logging to handle exceptions gracefully
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Win32Error(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class win32_SYS_Interface:
    def __init__(self):
        pass

    def hideWindowsTaskbar(self):
        try:
            taskbar = win32gui.FindWindow("Shell_TrayWnd", None)
            if taskbar:
                win32gui.ShowWindow(taskbar, win32con.SW_HIDE)
            rebar = win32gui.FindWindowEx(taskbar, None, "ReBarWindow32", None)
            if rebar:
                win32gui.ShowWindow(rebar, win32con.SW_HIDE)
        except Exception as e:
            logging.error(f"Failed to hide Windows taskbar: {e}")

    def showWindowsTaskbar(self):
        try:
            taskbar = win32gui.FindWindow("Shell_TrayWnd", None)
            if taskbar:
                win32gui.ShowWindow(taskbar, win32con.SW_SHOW)
            rebar = win32gui.FindWindowEx(taskbar, None, "ReBarWindow32", None)
            if rebar:
                win32gui.ShowWindow(rebar, win32con.SW_SHOW)
        except Exception as e:
            logging.error(f"Failed to show Windows taskbar: {e}")


class win32_WIN_Interface:
    def __init__(self, handle):
        try:
            if not isinstance(handle, int):
                raise TypeError(
                    "The handle must be an integer representing a valid window handle.\nValue provided: {}".format(
                        handle
                    )
                )
            if not win32gui.IsWindow(handle):
                raise ValueError(
                    "Invalid window handle provided.\nValue provided: {}".format(handle)
                )
            self.handle = handle
        except Exception as e:
            logging.error(f"Failed to initialize win32_WIN_Interface: {e}")

    def getForegroundWindow(self):
        try:
            return win32gui.GetForegroundWindow()
        except Exception as e:
            logging.error(f"Failed to get foreground window: {e}")

    def setForegroundWindow(self):
        try:
            win32gui.SetForegroundWindow(self.handle)
        except Exception as e:
            logging.error(f"Failed to set foreground window: {e}")

    def getWindowClass(self):
        try:
            return win32gui.GetClassName(self.handle)
        except Exception as e:
            logging.error(f"Failed to get window class: {e}")

    def getWindowProcessId(self):
        try:
            return win32process.GetWindowThreadProcessId(self.handle)[1]
        except Exception as e:
            logging.error(f"Failed to get window process ID: {e}")

    def getWindowThreadId(self):
        try:
            return win32process.GetWindowThreadProcessId(self.handle)[0]
        except Exception as e:
            logging.error(f"Failed to get window thread ID: {e}")

    def getWindowStyle(self):
        try:
            return win32gui.GetWindowLong(self.handle, win32con.GWL_STYLE)
        except Exception as e:
            logging.error(f"Failed to get window style: {e}")

    def setWindowStyle(self, style):
        try:
            win32gui.SetWindowLong(self.handle, win32con.GWL_STYLE, style)
        except Exception as e:
            logging.error(f"Failed to set window style: {e}")

    def moveWindow(self, x, y):
        try:
            x = max(0, int(x))
            y = max(0, int(y))
            win32gui.SetWindowPos(
                self.handle, 0, x, y, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
            )
        except Exception as e:
            logging.error(f"Failed to move window: {e}")

    def resizeWindow(self, width, height):
        try:
            rect = win32gui.GetWindowRect(self.handle)
            x, y = rect[0], rect[1]
            width = max(1, int(width))
            height = max(1, int(height))
            win32gui.MoveWindow(self.handle, x, y, width, height, True)
        except Exception as e:
            logging.error(f"Failed to resize window: {e}")

    def getWindowSize(self):
        try:
            rect = win32gui.GetWindowRect(self.handle)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            return width, height
        except Exception as e:
            logging.error(f"Failed to get window size: {e}")

    def getWindowPosition(self):
        try:
            rect = win32gui.GetWindowRect(self.handle)
            return rect[0], rect[1]
        except Exception as e:
            logging.error(f"Failed to get window position: {e}")

    def getWindowTitle(self):
        try:
            return win32gui.GetWindowText(self.handle)
        except Exception as e:
            logging.error(f"Failed to get window title: {e}")

    def setWindowTitle(self, title):
        try:
            win32gui.SetWindowText(self.handle, title)
        except Exception as e:
            logging.error(f"Failed to set window title: {e}")

    def getWindowHandle(self):
        return self.handle

    def setWindowHandle(self, handle):
        self.handle = handle

    def setWindowMonitor(self, monitor):
        try:
            monitors = win32api.EnumDisplayMonitors()
            if monitor < len(monitors):
                monitor_info = win32api.GetMonitorInfo(monitors[monitor][0])
                x, y, _, _ = monitor_info["Monitor"]
                self.moveWindow(x, y)
        except Exception as e:
            logging.error(f"Failed to set window monitor: {e}")

    def getWindowMonitor(self):
        try:
            rect = win32gui.GetWindowRect(self.handle)
            monitors = win32api.EnumDisplayMonitors()
            for i, monitor in enumerate(monitors):
                monitor_info = win32api.GetMonitorInfo(monitor[0])
                monitor_rect = monitor_info["Monitor"]
                if (
                    rect[0] >= monitor_rect[0]
                    and rect[1] >= monitor_rect[1]
                    and rect[2] <= monitor_rect[2]
                    and rect[3] <= monitor_rect[3]
                ):
                    return i
            return -1
        except Exception as e:
            logging.error(f"Failed to get window monitor: {e}")

    def setFullscreen(self):
        try:
            self.setBorderless()
            win32gui.ShowWindow(self.handle, win32con.SW_MAXIMIZE)
        except Exception as e:
            logging.error(f"Failed to set fullscreen: {e}")

    def exitFullscreen(self):
        try:
            self.exitBorderless()
            win32gui.ShowWindow(self.handle, win32con.SW_RESTORE)
        except Exception as e:
            logging.error(f"Failed to exit fullscreen: {e}")

    def isFullscreen(self):
        try:
            rect = win32gui.GetWindowRect(self.handle)
            screen_width = win32api.GetSystemMetrics(0)
            screen_height = win32api.GetSystemMetrics(1)
            return (
                rect[2] - rect[0] == screen_width and rect[3] - rect[1] == screen_height
            )
        except Exception as e:
            logging.error(f"Failed to check if window is fullscreen: {e}")

    def setBorderless(self):
        try:
            style = self.getWindowStyle()
            style &= ~win32con.WS_BORDER
            style &= ~win32con.WS_DLGFRAME
            self.setWindowStyle(style)
        except Exception as e:
            logging.error(f"Failed to set borderless: {e}")

    def exitBorderless(self):
        try:
            style = self.getWindowStyle()
            style |= win32con.WS_BORDER
            style |= win32con.WS_DLGFRAME
            self.setWindowStyle(style)
        except Exception as e:
            logging.error(f"Failed to exit borderless: {e}")

    def setNonResizable(self):
        try:
            style = self.getWindowStyle()
            style &= ~win32con.WS_THICKFRAME
            self.setWindowStyle(style)
        except Exception as e:
            logging.error(f"Failed to set non-resizable: {e}")

    def resetResizable(self):
        try:
            style = self.getWindowStyle()
            style |= win32con.WS_THICKFRAME
            self.setWindowStyle(style)
        except Exception as e:
            logging.error(f"Failed to reset resizable: {e}")

    def setMaximized(self):
        try:
            win32gui.ShowWindow(self.handle, win32con.SW_MAXIMIZE)
        except Exception as e:
            logging.error(f"Failed to set window maximized: {e}")

    def setMinimized(self):
        try:
            win32gui.ShowWindow(self.handle, win32con.SW_MINIMIZE)
        except Exception as e:
            logging.error(f"Failed to set window minimized: {e}")
