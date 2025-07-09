import cv2
import subprocess
import os
import time
import atexit
import ctypes
import win32gui
import win32con
import win32process
import tkinter as tk
from tkinter import ttk, simpledialog
import threading
import numpy as np
from PIL import Image, ImageTk
from obswebsocket import obsws, requests
import base64
import psutil


class OBSInterface:
    """Main class for interfacing with OBS Studio"""

    # Default OBS WebSocket configuration
    OBS_HOST = "localhost"
    OBS_PORT = 4455
    OBS_PASSWORD = ""

    def __init__(
        self, host=None, port=None, password=None, auto_start=True, auto_connect=True
    ):
        """Initialize the OBS interface

        Args:
            host (str): OBS WebSocket host
            port (int): OBS WebSocket port
            password (str): OBS WebSocket password
            auto_start (bool): Automatically start OBS and nginx if not running
            auto_connect (bool): Automatically connect to OBS WebSocket
        """
        self.host = host or self.OBS_HOST
        self.port = port or self.OBS_PORT
        self.password = password or self.OBS_PASSWORD
        self.ws = None

        # Register cleanup function
        atexit.register(self.cleanup)

        if auto_start:
            self.start_services()

        if auto_connect:
            self.connect()

    def is_process_running(self, process_name):
        """Check if a process is running by name"""
        call = subprocess.run(
            ["tasklist", "/FI", f"imagename eq {process_name}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        return process_name.lower() in call.stdout.lower()

    def close_obs_window(self, hwnd, extra):
        """Callback function to close OBS window"""
        title = win32gui.GetWindowText(hwnd)
        if "OBS" in title and win32gui.GetClassName(hwnd) == "Qt5QWindowIcon":
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    def cleanup(self):
        """Clean up resources when exiting"""
        print("Cleaning up OBS interface...")
        if self.ws:
            try:
                self.ws.call(requests.StopStreaming())
                self.ws.call(requests.Disconnect())
            except Exception as e:
                print(f"OBS WebSocket cleanup failed: {e}")
        win32gui.EnumWindows(self.close_obs_window, None)

    def start_services(self):
        """Start nginx-rtmp and OBS if not running"""
        # Start nginx-rtmp
        if not self.is_process_running("nginx.exe"):
            print("Starting nginx-rtmp...")
            nginx_path = os.path.abspath("nginx-rtmp/")
            os.chdir(nginx_path)
            subprocess.Popen(["nginx"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            time.sleep(1)
        else:
            print("Nginx is already running")

        # Launch OBS
        if not self.is_process_running("obs64.exe"):
            print("Launching OBS...")
            obs_path = os.path.abspath("OBS-Studio/bin/64bit")
            obs_cmd = [
                "obs64.exe",
                "--startreplaybuffer",
                "--minimize-to-tray",
                "--profile",
                "ScreenSnip",
                "--scene",
                "Scene",
                "-d",
            ]
            os.chdir(obs_path)
            subprocess.Popen(obs_cmd)
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

            # Wait for OBS to start
            print("Waiting for OBS to start...")
            time.sleep(5)
        else:
            print("OBS is already running")

    def connect(self):
        """Connect to OBS via WebSocket"""
        try:
            self.ws = obsws(self.host, self.port, self.password)
            self.ws.connect()
            # Verify connection by getting version
            version = self.ws.call(requests.GetVersion())
            print(
                f"Connected to OBS WebSocket. OBS Version: {version.getObsVersion()}, WebSocket Version: {version.getObsWebSocketVersion()}"
            )
            return True
        except Exception as e:
            print(f"Failed to connect to OBS WebSocket: {e}")
            self.ws = None
            return False

    def is_connected(self):
        """Check if connected to OBS WebSocket"""
        return self.ws is not None

    def safe_obs_call(self, request_name, request_obj):
        """Safely execute OBS commands with error handling"""
        if not self.ws:
            print(f"Cannot execute {request_name}: WebSocket not connected")
            return None

        try:
            result = self.ws.call(request_obj)
            return result
        except Exception as e:
            print(f"OBS command {request_name} failed: {e}")
            return None

    def get_screenshot(self, width=1280, height=720):
        """Get a screenshot of the current scene from OBS WebSocket"""
        if not self.ws:
            print("Cannot get screenshot: WebSocket not connected")
            return None

        try:
            # Request a screenshot of the current scene
            response = self.safe_obs_call(
                "GetSourceScreenshot",
                requests.GetSourceScreenshot(
                    sourceName="Scene",
                    imageFormat="png",
                    imageWidth=width,
                    imageHeight=height,
                    imageCompressionQuality=70,
                ),
            )

            if not response:
                return None

            # The response contains a base64 encoded image with a data URI prefix
            img_data = response.getImageData()

            # Remove the data URI prefix if present
            if "," in img_data:
                img_data = img_data.split(",", 1)[1]

            # Decode the base64 image data
            img_bytes = base64.b64decode(img_data)

            # Convert to numpy array for OpenCV processing
            img_array = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            return img

        except Exception as e:
            print(f"Error getting screenshot from OBS: {e}")
            return None

    def get_windows_by_pid(self, pid):
        """Get window info by PID"""
        result = []

        def callback(hwnd, lparam):
            try:
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        result.append({"hwnd": hwnd, "title": title})
            except:
                pass
            return True

        win32gui.EnumWindows(callback, None)
        return result

    def get_window_by_hwnd(self, hwnd):
        """Get window info by HWND"""
        try:
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                return {"hwnd": hwnd, "title": title, "pid": pid}
        except:
            pass
        return None

    def get_detailed_window_info(self, hwnd):
        """Get detailed window info by HWND"""
        if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
            return None

        import win32process
        import psutil

        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)

        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                exe_name = process.name()
                exe_path = process.exe()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                exe_name = "unknown"
                exe_path = "unknown"
        except:
            pid = 0
            exe_name = "unknown"
            exe_path = "unknown"

        return {
            "hwnd": hwnd,
            "title": title,
            "class": class_name,
            "pid": pid,
            "exe_name": exe_name,
            "exe_path": exe_path,
        }

    def set_window_capture(self, source_name, window_info):
        """Set a window capture source"""
        if not self.ws:
            print("Cannot update window capture: WebSocket not connected")
            return False

        # Create a new source with the correct settings
        return self.ensure_window_capture_source(source_name, window_info)

    def ensure_window_capture_source(self, source_name, window_info):
        """Check if an input source exists and create/update it if needed"""
        if not self.ws:
            print("Cannot check/create source: WebSocket not connected")
            return False

        # First, remove existing window capture sources
        input_list = self.safe_obs_call(
            "GetInputList", requests.GetInputList(inputKind="window_capture")
        )

        # Remove ALL window capture sources regardless of name
        if input_list and hasattr(input_list, "getInputs"):
            inputs = input_list.getInputs()
            removed_count = 0

            # Loop through all window capture inputs and remove them
            for input_info in inputs:
                input_name = input_info.get("inputName")
                input_source = input_info.get("inputSource")
                print(
                    f"Found existing window capture: {input_name} (Source: {input_source})"
                )
                print(f"input_info: {input_info}")
                self.safe_obs_call(
                    "RemoveInput", requests.RemoveInput(inputName=input_name)
                )
                removed_count += 1

            if removed_count > 0:
                print(f"Removed {removed_count} existing window capture sources")
                time.sleep(0.5)  # Give OBS a moment to process

        # Get more detailed window info
        detailed_info = self.get_detailed_window_info(window_info["hwnd"])
        if not detailed_info:
            print(f"Failed to get detailed info for window HWND: {window_info['hwnd']}")
            detailed_info = window_info
        else:
            print(f"Detailed window info: {detailed_info}")

        # Create window identifier
        window_title = detailed_info.get("title", "")
        window_class = detailed_info.get("class", "")
        exe_name = detailed_info.get("exe_name", "")

        # Escape colons in window title, class, and exe_name
        # Replace colons with a character that's unlikely to be in window titles
        window_title = window_title.replace(":", "___COLON___")
        window_class = window_class.replace(":", "___COLON___")
        exe_name = exe_name.replace(":", "___COLON___")

        print(
            f"Creating window capture for: Title='{window_title}' Class='{window_class}' Exe='{exe_name}'"
        )

        # Different window identifier formats to try for OBS 31.x and above
        hwnd_decimal = str(window_info["hwnd"])
        hwnd_hex = f"0x{window_info['hwnd']:08X}"

        # Try each capture method
        methods = [0]  # 2=WindowsGraphicsCapture
        method_names = ["WindowsGraphicsCapture"]

        # Keep track of successful captures
        successful_captures = []
        attempt_count = 0

        for method_idx, method in enumerate(methods):
            method_name = method_names[method]

            window_format = f"{window_title}:{window_class}:{exe_name}"

            attempt_name = f"{source_name}_{method_name}"
            attempt_count += 1

            settings = {
                "window": window_format,
                "method": method,
                "priority": 0,
                "capture_cursor": True,
                "compatibility": False,
                "client_area": False,
            }

            print(f"Trying window format: {window_format} with method: {method_name}")

            # Create the source - set to enabled from the start
            result = self.safe_obs_call(
                "CreateInput",
                requests.CreateInput(
                    sceneName="Scene",
                    inputName=attempt_name,
                    inputKind="window_capture",
                    inputSettings=settings,
                    inputSource=window_format,
                    sceneItemEnabled=True,  # Create as enabled
                ),
            )

            if not result:
                print(f"Failed with format: {window_format} and method: {method_name}")
                continue

            # Verify if the source was created correctly
            time.sleep(0.3)  # Give OBS more time to initialize the source
            verify_result = self.safe_obs_call(
                "GetInputSettings",
                requests.GetInputSettings(inputName=attempt_name),
            )

            if verify_result:
                print(
                    f"Successfully created window capture with format: {window_format} and method: {method_name}"
                )

                # Force a refresh of the source
                try:
                    self.safe_obs_call(
                        "PressInputPropertiesButton",
                        requests.PressInputPropertiesButton(
                            inputName=attempt_name, propertyName="refresh"
                        ),
                    )
                except Exception as e:
                    print(f"Error refreshing source: {e}")
                    pass

                # Ensure the source is enabled in the scene
                try:
                    # Find the scene item ID for this input
                    scene_items = self.safe_obs_call(
                        "GetSceneItemList", requests.GetSceneItemList(sceneName="Scene")
                    )

                    if scene_items:
                        for item in scene_items.getSceneItems():
                            if item.get("sourceName") == attempt_name:
                                # Enable this source item
                                self.safe_obs_call(
                                    "SetSceneItemEnabled",
                                    requests.SetSceneItemEnabled(
                                        sceneName="Scene",
                                        sceneItemId=item["sceneItemId"],
                                        sceneItemEnabled=True,
                                    ),
                                )
                                print(
                                    f"Explicitly enabled scene item for {attempt_name}"
                                )
                                break
                except Exception as e:
                    print(f"Error enabling scene item: {e}")

                # Add to successful list with details
                successful_captures.append(
                    {
                        "name": attempt_name,
                        "format": window_format,
                        "method": method_name,
                        "method_id": method,
                    }
                )
            else:
                # If source verification failed, remove it and continue
                print(f"Source created but verification failed for: {window_format}")
                self.safe_obs_call(
                    "RemoveInput", requests.RemoveInput(inputName=attempt_name)
                )

        print(
            f"Created {len(successful_captures)} window capture sources out of {attempt_count} attempts"
        )

        # If we have successful captures, enable the one with highest priority method
        if successful_captures:
            # Sort by method priority: WindowsGraphicsCapture (2) > Auto (0) > BitBlt (1)
            successful_captures.sort(key=lambda x: (3 - x["method_id"]))

            # Get the primary source (best method)
            primary_source = successful_captures[0]
            print(
                f"Setting primary source to: {primary_source['name']} using {primary_source['method']}"
            )

            # Get all scene items
            scene_items = self.safe_obs_call(
                "GetSceneItemList", requests.GetSceneItemList(sceneName="Scene")
            )

            if scene_items:
                # Enable primary source, disable others
                for item in scene_items.getSceneItems():
                    self.safe_obs_call(
                        "SetSceneItemEnabled",
                        requests.SetSceneItemEnabled(
                            sceneName="Scene",
                            sceneItemId=item["sceneItemId"],
                            sceneItemEnabled=True,
                        ),
                    )

            return True

        # If all window capture attempts failed, try display capture as fallback
        print("All window capture attempts failed. Trying display capture as fallback.")

        display_result = self.safe_obs_call(
            "CreateInput",
            requests.CreateInput(
                sceneName="Scene",
                inputName=f"{source_name}_DisplayCapture",
                inputKind="monitor_capture",
                inputSettings={},
                sceneItemEnabled=True,
            ),
        )

        if display_result:
            print("Created display capture as fallback")
            return True

        print("Failed to create any capture source")
        return False

    def get_all_visible_windows(self):
        """Get all visible windows that are valid for OBS window capture."""

        windows = []

        def is_valid_process(pid):
            # Only allow processes with a valid executable path and not system processes
            try:
                p = psutil.Process(pid)
                exe = p.exe()
                # Exclude system processes and background services
                if (
                    not exe
                    or "system32" in exe.lower()
                    or "windows\\explorer.exe" in exe.lower()
                ):
                    return False
                # Exclude processes without a window (like background tasks)
                if p.status() == psutil.STATUS_ZOMBIE:
                    return False
                return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                return False

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    # Filter out windows that are not valid for OBS
                    if is_valid_process(pid):
                        windows.append(
                            {
                                "hwnd": hwnd,
                                "title": win32gui.GetWindowText(hwnd),
                                "pid": pid,
                            }
                        )
                except Exception:
                    pass
            return True

        win32gui.EnumWindows(callback, None)
        return windows

    def create_display_capture(self, source_name="DisplayCapture"):
        """Create a display capture source"""
        if not self.ws:
            print("Cannot create display capture: WebSocket not connected")
            return False

        result = self.safe_obs_call(
            "CreateInput",
            requests.CreateInput(
                sceneName="Scene",
                inputName=source_name,
                inputKind="monitor_capture",
                inputSettings={},
                sceneItemEnabled=True,
            ),
        )

        return result is not None

    def set_current_scene(self, scene_name):
        """Set the current scene in OBS"""
        if not self.ws:
            print("Cannot set scene: WebSocket not connected")
            return False

        result = self.safe_obs_call(
            "SetCurrentProgramScene",
            requests.SetCurrentProgramScene(sceneName=scene_name),
        )

        return result is not None

    def get_scenes(self):
        """Get list of available scenes"""
        if not self.ws:
            print("Cannot get scenes: WebSocket not connected")
            return []

        scenes = self.safe_obs_call("GetSceneList", requests.GetSceneList())
        if scenes:
            return [scene["sceneName"] for scene in scenes.getScenes()]
        return []


# GUI Classes - only used when run as standalone
class OBSSourceSelector:
    def __init__(self, parent, obs_interface):
        self.parent = parent
        self.obs_interface = obs_interface
        self.top = tk.Toplevel(parent)
        self.top.title("OBS Source Selector")
        self.top.geometry("600x500")
        self.top.transient(parent)
        self.top.grab_set()

        # Create notebook with tabs
        self.notebook = ttk.Notebook(self.top)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Windows tab
        self.windows_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.windows_frame, text="Window Capture")

        # Search field for windows
        search_frame = ttk.Frame(self.windows_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_windows)
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True
        )

        # Refresh button
        ttk.Button(search_frame, text="Refresh", command=self.refresh_windows).pack(
            side=tk.RIGHT, padx=5
        )

        # Window list
        list_frame = ttk.Frame(self.windows_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Columns: Title, PID, HWND
        self.tree = ttk.Treeview(
            list_frame, columns=("title", "pid", "hwnd"), show="headings"
        )
        self.tree.heading("title", text="Window Title")
        self.tree.heading("pid", text="PID")
        self.tree.heading("hwnd", text="HWND")
        self.tree.column("title", width=300)
        self.tree.column("pid", width=70)
        self.tree.column("hwnd", width=100)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Source name entry
        name_frame = ttk.Frame(self.windows_frame)
        name_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(name_frame, text="Source Name:").pack(side=tk.LEFT, padx=5)
        self.source_name_var = tk.StringVar(value="WindowCapture")
        ttk.Entry(name_frame, textvariable=self.source_name_var, width=30).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True
        )

        # Button frame
        btn_frame = ttk.Frame(self.windows_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=10)
        ttk.Button(btn_frame, text="Create Source", command=self.create_source).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(btn_frame, text="Cancel", command=self.top.destroy).pack(
            side=tk.RIGHT, padx=5
        )

        # Display Capture tab
        self.display_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.display_frame, text="Display Capture")

        # Display capture options
        display_name_frame = ttk.Frame(self.display_frame)
        display_name_frame.pack(fill=tk.X, padx=5, pady=20)
        ttk.Label(display_name_frame, text="Source Name:").pack(side=tk.LEFT, padx=5)
        self.display_name_var = tk.StringVar(value="DisplayCapture")
        ttk.Entry(
            display_name_frame, textvariable=self.display_name_var, width=30
        ).pack(side=tk.LEFT, padx=5)

        # Display capture button
        display_btn_frame = ttk.Frame(self.display_frame)
        display_btn_frame.pack(fill=tk.X, padx=5, pady=10)
        ttk.Button(
            display_btn_frame,
            text="Create Display Capture",
            command=self.create_display_capture,
        ).pack(side=tk.RIGHT, padx=5)
        ttk.Button(display_btn_frame, text="Cancel", command=self.top.destroy).pack(
            side=tk.RIGHT, padx=5
        )

        # Load windows on init
        self.all_windows = []
        self.refresh_windows()

        # Center the window
        self.center_window()

    def center_window(self):
        self.top.update_idletasks()
        width = self.top.winfo_width()
        height = self.top.winfo_height()
        x = (self.top.winfo_screenwidth() // 2) - (width // 2)
        y = (self.top.winfo_screenheight() // 2) - (height // 2)
        self.top.geometry(f"{width}x{height}+{x}+{y}")

    def refresh_windows(self):
        # Clear the tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get all windows
        self.all_windows = self.obs_interface.get_all_visible_windows()

        # Sort windows by title
        self.all_windows.sort(key=lambda w: w["title"].lower())

        # Add windows to the tree
        for window in self.all_windows:
            self.tree.insert(
                "",
                tk.END,
                values=(window["title"], window["pid"], f"0x{window['hwnd']:08X}"),
            )

    def filter_windows(self, *args):
        # Clear the tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get search term
        search = self.search_var.get().lower()

        # Filter and add windows to the tree
        for window in self.all_windows:
            if search in window["title"].lower():
                self.tree.insert(
                    "",
                    tk.END,
                    values=(window["title"], window["pid"], f"0x{window['hwnd']:08X}"),
                )

    def create_source(self):
        # Get selected window
        selection = self.tree.selection()
        if not selection:
            tk.messagebox.showerror("Error", "Please select a window")
            return

        # Get window info from selected item
        item = self.tree.item(selection[0])
        title, pid, hwnd_str = item["values"]

        # Convert HWND string back to integer
        if hwnd_str.startswith("0x"):
            hwnd = int(hwnd_str, 16)
        else:
            hwnd = int(hwnd_str)

        # Get window info
        window_info = self.obs_interface.get_window_by_hwnd(hwnd)
        if not window_info:
            tk.messagebox.showerror("Error", f"No visible window found for HWND {hwnd}")
            return

        # Get source name
        source_name = self.source_name_var.get().strip()
        if not source_name:
            source_name = "WindowCapture"

        # Create the source
        success = self.obs_interface.set_window_capture(source_name, window_info)

        if success:
            tk.messagebox.showinfo(
                "Success", f"Created window capture source: {source_name}"
            )
            self.top.destroy()
        else:
            tk.messagebox.showerror("Error", "Failed to create window capture source")

    def create_display_capture(self):
        # Get source name
        source_name = self.display_name_var.get().strip()
        if not source_name:
            source_name = "DisplayCapture"

        # Create display capture source
        result = self.obs_interface.create_display_capture(source_name)

        if result:
            tk.messagebox.showinfo(
                "Success", f"Created display capture source: {source_name}"
            )
            self.top.destroy()
        else:
            tk.messagebox.showerror("Error", "Failed to create display capture source")


class RTMPViewer:
    def __init__(self, root, obs_interface):
        self.root = root
        self.obs_interface = obs_interface
        self.root.title("OBS Scene Viewer")
        self.root.geometry("1280x720")

        # Create a frame for the video
        self.video_frame = ttk.Frame(root)
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for the video
        self.canvas = tk.Canvas(self.video_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Create a toolbar
        self.toolbar = ttk.Frame(root)
        self.toolbar.pack(fill=tk.X)

        # Add buttons to toolbar
        ttk.Button(
            self.toolbar,
            text="Configure OBS Sources",
            command=self.open_source_selector,
        ).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(self.toolbar, text="Exit", command=self.exit_app).pack(
            side=tk.RIGHT, padx=5, pady=5
        )

        # Status bar
        self.status_var = tk.StringVar(value="Connecting to OBS...")
        self.status_bar = ttk.Label(
            root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Frame variables
        self.running = True
        self.frame_width = 1280
        self.frame_height = 720
        self.frame_rate = 30  # Target frame rate
        self.frame_interval = 1.0 / self.frame_rate

        # Start frame capture in a separate thread
        self.video_thread = threading.Thread(target=self.update_frame, daemon=True)
        self.video_thread.start()

        # Set up window close handling
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def open_source_selector(self):
        OBSSourceSelector(self.root, self.obs_interface)

    def update_frame(self):
        last_frame_time = 0

        while self.running:
            current_time = time.time()
            elapsed = current_time - last_frame_time

            # Check if it's time for a new frame based on our target frame rate
            if elapsed >= self.frame_interval:
                # Get frame from OBS WebSocket
                frame = self.obs_interface.get_screenshot(
                    self.frame_width, self.frame_height
                )

                if frame is not None:
                    # Convert frame to RGB (from BGR)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Convert to PIL Image
                    pil_img = Image.fromarray(frame_rgb)

                    # Get current canvas size
                    canvas_width = self.canvas.winfo_width()
                    canvas_height = self.canvas.winfo_height()

                    # Only resize if canvas size is valid
                    if canvas_width > 1 and canvas_height > 1:
                        # Calculate aspect ratio preserving resize
                        img_width, img_height = pil_img.size
                        ratio = min(
                            canvas_width / img_width, canvas_height / img_height
                        )
                        new_width = int(img_width * ratio)
                        new_height = int(img_height * ratio)

                        # Resize image
                        pil_img = pil_img.resize((new_width, new_height), Image.LANCZOS)

                    # Convert to PhotoImage
                    self.photo = ImageTk.PhotoImage(image=pil_img)

                    # Update canvas with new image (in main thread)
                    self.root.after(1, self._update_canvas)

                    # Update status if needed
                    if self.status_var.get() != "Connected to OBS":
                        self.status_var.set("Connected to OBS")

                    # Update last frame time
                    last_frame_time = current_time
                else:
                    # Handle connection issues
                    self.status_var.set("Waiting for OBS connection...")
                    time.sleep(1)
            else:
                # Small sleep to prevent CPU hogging
                time.sleep(0.005)  # 5ms sleep

    def _update_canvas(self):
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Calculate position to center the image
        if hasattr(self, "photo"):
            x = (canvas_width - self.photo.width()) // 2
            y = (canvas_height - self.photo.height()) // 2

            # Clear canvas and display the image
            self.canvas.delete("all")
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo)

    def exit_app(self):
        self.running = False
        self.root.destroy()


# Create a global instance if needed (but only when imported)
obs = None


def get_instance(auto_start=True, auto_connect=True):
    """Get or create a global OBS interface instance"""
    global obs
    if obs is None:
        obs = OBSInterface(auto_start=auto_start, auto_connect=auto_connect)
    return obs


# Standalone execution
if __name__ == "__main__":
    # Create the OBS interface
    obs_interface = OBSInterface()

    # Set initial scene
    if obs_interface.is_connected():
        scenes = obs_interface.get_scenes()
        if scenes:
            print("Available scenes:", scenes)
        obs_interface.set_current_scene("Scene")

    # Create Tkinter root and app
    root = tk.Tk()
    app = RTMPViewer(root, obs_interface)

    # Start Tkinter main loop
    root.mainloop()
