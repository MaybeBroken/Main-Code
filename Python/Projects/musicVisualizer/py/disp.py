from direct.showbase.ShowBase import ShowBase
from panda3d.core import Shader, TransparencyAttrib, loadPrcFileData
from panda3d.core import CardMaker
import sys
from screeninfo import get_monitors
import mouse
from vis import MusicVisualizer

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

# Enable transparency and remove window frame
loadPrcFileData('', 'framebuffer-alpha true')
loadPrcFileData('', 'win-size ' + str(monitor_width) + ' ' + str(monitor_height))
loadPrcFileData('', 'win-origin 0 0')
loadPrcFileData('', 'window-type onscreen')
loadPrcFileData('', 'undecorated true')
loadPrcFileData('', 'background-color 0 0 0 0')
loadPrcFileData('', 'active-display-region true')
loadPrcFileData('', 'sync-video false')

if sys.platform == "win32":
    import win32con
    import win32gui
    import win32api
    import pystray
    from PIL import Image
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

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
        card_maker = CardMaker('card')
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
        card_maker.setFrame(-1, -1 + thickness, -1, 1)
        left_card = self.render2d.attachNewNode(card_maker.generate())
        left_card.setColor(0.6, 0.5, 0.6, 0.8)
        self.cards.append(left_card)

        # Right edge (x = 1)
        card_maker.setFrame(1 - thickness, 1, -1, 1)
        right_card = self.render2d.attachNewNode(card_maker.generate())
        right_card.setColor(0.8, 0.5, 0.4, 0.8)
        self.cards.append(right_card)

        self.disableMouse()
        self.taskMgr.add(self.update, 'update_music_visualizer')
    
    def update(self, task):
        # Update the music visualizer
        vis.update_plot()
        low, high = vis.get_beat_status()
        if low:
            self.cards[0].setColor(0.2, 0.5, 1.0, 0.8)  # Bottom edge
            self.cards[1].setColor(0.4, 0.5, 0.8, 0.8)  # Top edge
        else:
            self.cards[0].setColor(0.1, 0.3, 0.5, 0.8)
            self.cards[1].setColor(0.2, 0.3, 0.5, 0.8)
        if high:
            self.cards[2].setColor(0.6, 0.5, 0.6, 0.8)  # Left edge
            self.cards[3].setColor(0.8, 0.5, 0.4, 0.8)
        else:
            self.cards[2].setColor(0.4, 0.3, 0.4, 0.8)
            self.cards[3].setColor(0.5, 0.3, 0.2, 0.8)
        return task.cont


    def make_window_transparent(self):
        # Get Panda3D window handle
        hwnd = self.win.getWindowHandle().getIntHandle()
        # Set layered style
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles | win32con.WS_EX_LAYERED)
        # Set per-pixel alpha (0 = fully transparent, 255 = opaque)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), 0, win32con.LWA_COLORKEY)
        # Make window always on top
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
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
        image = Image.new('RGBA', (32, 32), (255, 0, 0, 255))  # Red square as placeholder
        def on_quit(icon, item):
            icon.stop()
            sys.exit(0)
        menu = pystray.Menu(pystray.MenuItem('Quit', on_quit))
        icon = pystray.Icon("musicVisualizer", image, "Music Visualizer", menu)
        # Run the icon in a separate thread so it doesn't block Panda3D
        import threading
        threading.Thread(target=icon.run).start()

app = TransparentApp()
app.run()