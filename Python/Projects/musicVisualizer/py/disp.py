from direct.showbase.ShowBase import ShowBase
from panda3d.core import Shader, TransparencyAttrib, loadPrcFileData
from panda3d.core import CardMaker
import sys
from screeninfo import get_monitors
import mouse
from vis import MusicVisualizer
import threading
import subprocess
import os
from panda3d.core import VBase4
from direct.interval.IntervalGlobal import LerpFunc

vis = MusicVisualizer(show_windows=False)
vis.start_stream()


def get_current_monitor():
    x, y = mouse.get_position()
    for idx, m in enumerate(get_monitors()):
        if m.x <= x < m.x + m.width and m.y <= y < m.y + m.height:
            return idx
    return 0  # Default to primary if not found


monitor = get_monitors()[get_current_monitor()]
monitor_width = monitor.width
monitor_height = monitor.height - 49  # Leave some space for the taskbar
aspect_ratio = monitor_width / monitor_height

# Enable transparency and remove window frame
loadPrcFileData("", "framebuffer-alpha true")
loadPrcFileData("", "win-size " + str(monitor_width) + " " + str(monitor_height))
loadPrcFileData("", "win-origin 0 0")
loadPrcFileData("", "window-type onscreen")
loadPrcFileData("", "undecorated true")
loadPrcFileData("", "background-color 0 0 0 0")
loadPrcFileData("", "active-display-region true")
loadPrcFileData("", "sync-video false")

if sys.platform == "win32":
    import win32con
    import win32gui
    import win32api
    import pystray
    from PIL import Image
    import ctypes

    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    import asyncio
    from winrt.windows.media.control import (
        GlobalSystemMediaTransportControlsSessionManager as GSMTCSessionManager,
    )
from PIL import Image
import io


async def get_windows_media_info():
    manager = await GSMTCSessionManager.request_async()
    session = manager.get_current_session()
    if session is None:
        return "No media session is currently active."
    info = await session.try_get_media_properties_async()
    # Extract metadata fields
    metadata = {
        "title": info.title,
        "artist": info.artist,
        "album_artist": info.album_artist,
        "album_title": info.album_title,
        "track_number": info.track_number,
        "genre": [genre.name for genre in info.genres] if info.genres else [],
    }
    return metadata


# To call from sync code:
def get_media_info_sync():
    return asyncio.run(get_windows_media_info())


print("Using Windows Media API for metadata:\n", get_media_info_sync())


class TransparentApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        if sys.platform == "win32":
            self.hide_from_taskbar()  # <-- Move this to the very start, before any rendering
        self.render2d.setTransparency(TransparencyAttrib.MAlpha)
        # Force window transparency using pywin32 (Windows only)
        if sys.platform == "win32":
            self.make_window_transparent()
            # Render one frame to ensure the window is fully created before continuing
            self.graphicsEngine.renderFrame()
            self.create_tray_icon()

        # Create four thin cards, one on each edge of the render2d screen
        card_maker = CardMaker("card")
        thickness = 0.0075  # Thickness in render2d units

        self.cards = []

        # Bottom edge (y = -1)
        card_maker.setFrame(-1, 1, -1, -1 + thickness)
        bottom_card = self.render2d.attachNewNode(card_maker.generate())
        bottom_card.setColor(0.2, 0.5, 1.0, 0.8)
        self.cards.append(bottom_card)

        # Top edge (y = 1)
        card_maker.setFrame(-1, 1, 1 - thickness, 1)
        top_card = self.render2d.attachNewNode(card_maker.generate())
        top_card.setColor(0.4, 0.5, 0.8, 0.8)
        self.cards.append(top_card)

        # Left edge (x = -1)
        card_maker.setFrame(
            -1, -1 + thickness / aspect_ratio, -1 + thickness, 1 - thickness
        )
        left_card = self.render2d.attachNewNode(card_maker.generate())
        left_card.setColor(0.6, 0.5, 0.6, 0.8)
        self.cards.append(left_card)

        # Right edge (x = 1)
        card_maker.setFrame(
            1 - thickness / aspect_ratio, 1, -1 + thickness, 1 - thickness
        )
        right_card = self.render2d.attachNewNode(card_maker.generate())
        right_card.setColor(0.8, 0.5, 0.4, 0.8)
        self.cards.append(right_card)

        self.disableMouse()
        # --- Move initialization here ---
        self.prev_low = None
        self.prev_high = None
        self.lerp_intervals = [None, None, None, None]
        # --- End move ---
        self.taskMgr.add(self.update, "update_music_visualizer")

    def update(self, task):
        # Update the music visualizer
        vis.update_plot()
        low, high = vis.get_beat_status()
        detected_mood, energy = vis.get_mood_energy()
        freqs, spectrum = vis.get_spectrum()

        # Helper to start a lerp interval for a card
        def start_lerp(card, idx, start_color, end_color, duration=0.05):
            if self.lerp_intervals[idx]:
                self.lerp_intervals[idx].finish()

            def lerp_color(t):
                color = start_color * (1 - t) + end_color * t
                card.setColor(color)

            self.lerp_intervals[idx] = LerpFunc(
                lerp_color, fromData=0.0, toData=1.0, duration=duration
            )
            self.lerp_intervals[idx].start()

        # Define target colors
        bottom_on = (0.2, 0.5, 1.0, energy + 0.3)
        bottom_off = (0.1, 0.3, 0.5, energy + 0.3)
        top_on = (0.4, 0.5, 0.8, energy + 0.3)
        top_off = (0.2, 0.3, 0.5, energy + 0.3)
        left_on = (0.6, 0.5, 0.6, energy + 0.3)
        left_off = (0.4, 0.3, 0.4, energy + 0.3)
        right_on = (0.8, 0.5, 0.4, energy + 0.3)
        right_off = (0.5, 0.3, 0.2, energy + 0.3)

        # Only trigger lerp when state changes
        if self.prev_low is None or low != self.prev_low:
            start = VBase4(*self.cards[0].getColor())
            end = VBase4(*(bottom_on if low else bottom_off))
            start_lerp(self.cards[0], 0, start, end)
            start = VBase4(*self.cards[1].getColor())
            end = VBase4(*(top_on if low else top_off))
            start_lerp(self.cards[1], 1, start, end)
        if self.prev_high is None or high != self.prev_high:
            start = VBase4(*self.cards[2].getColor())
            end = VBase4(*(left_on if high else left_off))
            start_lerp(self.cards[2], 2, start, end)
            start = VBase4(*self.cards[3].getColor())
            end = VBase4(*(right_on if high else right_off))
            start_lerp(self.cards[3], 3, start, end)

        # Always update alpha to match energy, even if state didn't change
        for idx, (on_col, off_col) in enumerate(
            [
                (bottom_on, bottom_off),
                (top_on, top_off),
                (left_on, left_off),
                (right_on, right_off),
            ]
        ):
            col = on_col if ((idx < 2 and low) or (idx >= 2 and high)) else off_col
            prev = self.cards[idx].getColor()
            # Only update alpha if it changed
            if abs(prev[3] - col[3]) > 1e-3:
                self.cards[idx].setColor(prev[0], prev[1], prev[2], col[3])

        self.prev_low = low
        self.prev_high = high
        return task.cont

    def make_window_transparent(self):
        # Get Panda3D window handle
        hwnd = self.win.getWindowHandle().getIntHandle()
        # Set layered style
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(
            hwnd, win32con.GWL_EXSTYLE, styles | win32con.WS_EX_LAYERED
        )
        # Set per-pixel alpha (0 = fully transparent, 255 = opaque)
        win32gui.SetLayeredWindowAttributes(
            hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY
        )
        # Make window always on top
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE,
        )

    def hide_from_taskbar(self):
        hwnd = self.win.getWindowHandle().getIntHandle()
        # Remove from taskbar by setting WS_EX_TOOLWINDOW and removing WS_EX_APPWINDOW
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        ex_style = ex_style | win32con.WS_EX_TOOLWINDOW
        ex_style = ex_style & ~win32con.WS_EX_APPWINDOW
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
        # Hide and show to update taskbar state
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

    def create_tray_icon(self):
        # Use a 16x16 or 32x32 PNG icon file, or create a simple one
        image = Image.new(
            "RGBA", (32, 32), (255, 0, 0, 255)
        )  # Red square as placeholder

        def on_quit(icon, item):
            icon.stop()
            os.kill(os.getpid(), 9)

        menu = pystray.Menu(pystray.MenuItem("Quit", on_quit))
        icon = pystray.Icon("musicVisualizer", image, "Music Visualizer", menu)
        # Run the icon in a separate thread so it doesn't block Panda3D

        threading.Thread(target=icon.run).start()


app = TransparentApp()
app.run()
