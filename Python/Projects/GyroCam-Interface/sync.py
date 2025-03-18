from random import randint
import serial
import time
import threading
from serial.tools import list_ports
from tkinter import messagebox, Tk, Label, Button, Entry, StringVar, Frame, Listbox
from tkinter import *
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.core import *
from panda3d.core import (
    Vec4,
    loadPrcFileData,
    GraphicsEngine,
)
from math import radians, degrees, sin, cos, tan, asin, acos, atan2

from matplotlib import (
    pyplot as plt,
    animation as anm,
    colors as cl,
    cm,
)
from direct.interval.IntervalGlobal import *
from opensimplex import OpenSimplex as SimplexNoise

simplex_noise = SimplexNoise(seed=0)

DATAQUEUE = []

loadPrcFileData(
    "",
    """window-title GyroCam Interface
want-pstats 1
show-frame-rate-meter 1
clock-mode global
sync-video 0
""",
)


class DATA:
    def __init__(self, data):
        self.data = data

    def format(self):
        try:
            self.vec_x = round(float(self.data[0][1]), 1)
            self.vec_y = round(float(self.data[0][2]), 1)
            self.vec_z = round(float(self.data[0][3]), 1) - 1
            self.vec_total = float(self.data[1][1]) * 5
            self.vec_h = round(float(self.data[2][1]), 1)
            self.vec_p = round(float(self.data[2][2]), 1)
            self.vec_r = round(float(self.data[2][3]), 1)
            self.temp_celcius = float(self.data[3][1])
            self.temp_fahrenheit = (self.temp_celcius * 9 / 5) + 32
            self.acc_x = self.vec_x * 9.81 * 10
            self.acc_y = self.vec_y * 9.81 * 10
            self.acc_z = self.vec_z * 9.81 * 10
        except IndexError as e:
            return None
        return self


class OBJECT:
    def __init__(self, name):
        self.name = name
        self.vec_x = 0
        self.vec_y = 0
        self.vec_z = 0

        self.vec_total = 0

        self.vec_h = 0
        self.vec_p = 0
        self.vec_r = 0

        self.pos_x = 0
        self.pos_y = 0
        self.pos_z = 0

        self.pos_total = 0

        self.pos_h = 0
        self.pos_p = 0
        self.pos_r = 0

        self.temp_celcius = 0
        self.temp_fahrenheit = 0

    def set_data(self, data: DATA, dt):
        self.vec_h = data.vec_h
        self.vec_p = data.vec_p
        self.vec_r = data.vec_r
        self.vec_x = data.vec_x
        self.vec_y = data.vec_y
        self.vec_z = data.vec_z
        self.vec_total = data.vec_total

        self.pos_h += data.vec_h
        self.pos_p += data.vec_p
        self.pos_r += data.vec_r

        # Update position directly based on acceleration data
        self.pos_x += data.acc_x * dt / 2
        self.pos_y += data.acc_y * dt / 2
        self.pos_z += data.acc_z * dt / 2
        self.pos_total = self.pos_x + self.pos_y + self.pos_z

        self.temp_celcius = data.temp_celcius
        self.temp_fahrenheit = data.temp_fahrenheit


class SIMULATION(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.setBackgroundColor(0, 0, 0)
        self.camera.setPos(25, 30, 12)
        self.camera.lookAt(0, 0, 0)
        self.model = self.loader.loadModel("models/box")
        self.model.reparentTo(self.render)
        self.task_mgr.add(self.update, "update_task")
        self.last_time = time.time()

    def setModelState(self, object: OBJECT):
        self.model.setPos(object.pos_x, object.pos_y, object.pos_z)
        self.model.setHpr(object.pos_h, object.pos_p, object.pos_r)

    def update(self, task):
        global DATAQUEUE
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        if DATAQUEUE:
            try:
                data = DATAQUEUE.pop(-1)
                viewer.set(f"Data from Arduino:\n" + str(data))
                formatted_data = DATA(data).format()
                if formatted_data is not None:
                    camera.set_data(formatted_data, dt)
                    self.setModelState(camera)
                    plot.add_data(camera)
            except Exception as e:
                viewer.print(f"Error processing data: {e}\n{data}")
        if len(DATAQUEUE) > 10:
            DATAQUEUE = DATAQUEUE[5:]
        return task.cont

    def update_graphics_only(self):
        self.graphicsEngine.renderFrame()


class PLOT:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(-20, 20)
        self.lines = {
            "x": self.ax.plot([], [], lw=2, label="X")[0],
            "y": self.ax.plot([], [], lw=2, label="Y")[0],
            "z": self.ax.plot([], [], lw=2, label="Z")[0],
        }
        self.xdata = []
        self.ydata = {"x": [], "y": [], "z": []}
        self.ax.legend()
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Value")
        self.ax.set_title("Sensor Data")
        self.ax.grid()
        self.ax.set_facecolor("black")
        self.ax.xaxis.label.set_color("white")
        self.ax.yaxis.label.set_color("white")
        self.ax.tick_params(axis="x", colors="red")
        self.ax.tick_params(axis="y", colors="green")
        self.fig.patch.set_facecolor("black")

    def setup(self):
        plt.ion()
        plt.show(block=False)  # Ensure the plot updates in the background
        viewer.print("Plotting setup complete")

    def add_data(self, data: OBJECT):
        self.xdata.append(len(self.xdata))
        self.ydata["x"].append(data.pos_x)
        self.ydata["y"].append(data.pos_y)
        self.ydata["z"].append(data.pos_z)
        if len(self.xdata) > 100:
            self.reset_plot()
        for key in self.lines:
            self.lines[key].set_data(self.xdata, self.ydata[key])
        self.fig.canvas.draw_idle()  # Update the plot without bringing it to the front
        self.fig.canvas.flush_events()  # Ensure the plot updates in the background

    def reset_plot(self):
        self.xdata.clear()
        self.ydata["x"].clear()
        self.ydata["y"].clear()
        self.ydata["z"].clear()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(-20, 20)
        for key in self.lines:
            self.lines[key].set_data([], [])
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()


class VIEWER:
    def __init__(self):
        self.window = Tk()
        self.window.title("Output Viewer")
        self.window.geometry("900x500")
        self.window.configure(bg="#000000")
        self.emulatedTerminal = Text(
            self.window,
            bg="#000000",
            fg="white",
            font=("Arial", 12),
            width=70,
            height=20,
            state=DISABLED,
        )
        self.emulatedTerminal.pack(pady=10)
        self.emulatedData = Label(
            self.window,
            text="Data from Arduino:",
            bg="#000000",
            fg="white",
            font=("Arial", 12),
        )
        self.emulatedData.pack(pady=10)
        self.emulatedData.config(wraplength=800)
        self.emulatedData.config(anchor="w")

    def print(self, text):
        self.emulatedTerminal.config(state=NORMAL)
        self.emulatedTerminal.insert(END, text + "\n")
        self.emulatedTerminal.config(state=DISABLED)
        self.emulatedTerminal.see(END)
        self.window.update_idletasks()  # Ensure pending events are processed
        self.window.update()

    def set(self, text):
        self.emulatedData.config(text=text)
        self.window.update_idletasks()  # Ensure pending events are processed
        self.window.update()


class PsuedoSerial:
    def __init__(self):
        self.is_open = True
        self.port = "BLANK"
        self.baud_rate = 115200
        self.timeout = 1
        self.last_read = 0

    def disconnect(self): ...
    def close(self): ...
    def write(self, data): ...
    def readline(self):
        self.last_read += 0.00001
        noise1 = simplex_noise.noise3(32, -32, self.last_read) * 20
        noise2 = simplex_noise.noise3(32, 32, self.last_read) * 20
        noise3 = simplex_noise.noise3(-32, 32, self.last_read) * 20
        return f"0:{noise1}:{noise2}:{noise3}|0:{noise1 + noise2 + noise3}|0:{randint(0, 10)}:{randint(0, 10)}:{randint(0, 10)}|0:{randint(0, 10)}".encode()


class ArduinoSerialInterface:
    def __init__(self, port, baud_rate=115200, timeout=1):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial_connection = None

    def connect(self):
        try:
            if not self.port == "BLANK":
                self.serial_connection = serial.Serial(
                    self.port, self.baud_rate, timeout=self.timeout
                )
                time.sleep(2)
            else:
                self.serial_connection = PsuedoSerial()
            print(f"Connected to Arduino on port {self.port}")
            viewer.print(f"Streaming to Arduino on port {self.port}")
            self.start_reading_thread()
        except PermissionError as e:
            print(
                f"PermissionError: {e}. Please check if the port is already in use or if you have the necessary permissions."
            )
            viewer.print(
                f"PermissionError: {e}. Please check if the port is already in use or if you have the necessary permissions."
            )
        except serial.SerialException as e:
            print(f"Error connecting to Arduino: {e}")
            viewer.print(f"Error connecting to Arduino: {e}")

    def start_reading_thread(self):
        self.reading_thread = threading.Thread(target=self.read_data_continuously)
        self.reading_thread.daemon = True
        self.reading_thread.start()

    def read_data_continuously(self):
        global DATAQUEUE
        while self.serial_connection and self.serial_connection.is_open:
            try:
                data = self.read_data()
                if data and ":" in data and "|" in data:
                    data = data.strip()
                    data = data.split("|")
                    for i in range(len(data)):
                        data[i] = data[i].strip()
                        data[i] = data[i].split(":")
                    formatted_data = DATA(data).format()
                    if len(data) == 4 and formatted_data is not None:
                        DATAQUEUE.append(data)
                        if len(DATAQUEUE) > 1000:  # Prevent excessive memory usage
                            DATAQUEUE.pop(0)
            except serial.SerialException as e:
                print(f"Error reading data: {e}")

    def disconnect(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print(f"Disconnected from Arduino on port {self.port}")
            viewer.print(f"Disconnected from Arduino on port {self.port}")

    def send_data(self, data):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(data.encode())
        else:
            print("Serial connection is not open")
        viewer.print("Serial connection is not open")

    def read_data(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                data = self.serial_connection.readline().decode(errors="ignore").strip()
                if data:
                    return data
            except serial.SerialException as e:
                viewer.print(f"Error reading data: {e}")
        return None


def list_active_serial_ports():
    """Lists all active serial ports on the system."""
    ports = list_ports.comports()
    active_ports = []
    inactive_ports = []
    for port in ports:
        if port.device.startswith("COM") or port.device.startswith("/dev/"):
            active_ports.append(port.device)
        else:
            inactive_ports.append(port.device)
    print("Available ports:")
    for port in active_ports:
        print(port)
    print("Inactive ports:")
    for port in inactive_ports:
        print(port)
    return active_ports


ARDUINO: ArduinoSerialInterface = None


def connect(port):
    global ARDUINO
    viewer.print(f"Connecting to Arduino on port {port}@115.2k baud")
    ARDUINO = ArduinoSerialInterface(port=port, baud_rate=115200)
    ARDUINO.connect()


def update_simulation():
    simulation.task_mgr.step()
    window.after(16, update_simulation)  # Schedule the next update in ~16ms (60 FPS)


if __name__ == "__main__":
    window = Tk()
    window.title("Arduino Serial Interface")
    window.geometry("800x600")
    window.configure(bg="black")
    available_ports = list_active_serial_ports()
    if not available_ports:
        print("No serial ports available.")
        available_ports = ["BLANK"]
    port_label = Label(
        window,
        text="Select a serial port:",
        bg="black",
        fg="white",
        font=("Courier New", 12),
    )
    port_label.pack(pady=10)

    ConnectionListbox = Listbox(
        window,
        bg="black",
        fg="white",
        font=("Courier New", 12),
        selectbackground="blue",
    )
    ConnectionListbox.pack(pady=10, fill=BOTH, expand=True)
    for port in available_ports:
        ConnectionListbox.insert(END, port)
    selected_port = StringVar()
    selected_port.set(available_ports[0])

    connect_button = Button(
        window,
        text="Connect",
        command=lambda: (
            print("Connecting to Arduino..."),
            connect(ConnectionListbox.get(ACTIVE)),
            window.withdraw(),
        ),
        bg="black",
        fg="black",
        font=("Courier New", 12),
    )
    connect_button.pack(pady=10)
    viewer = VIEWER()
    simulation = SIMULATION()
    plot = PLOT()
    plot.setup()
    camera = OBJECT("Camera")

    viewer.print("Loaded simulation configuration")
    update_simulation()  # Start the simulation update loop
    viewer.print("Simulation started")

    try:
        window.mainloop()  # Run Tkinter main loop in the main thread
    except KeyboardInterrupt:
        ARDUINO.disconnect()
    finally:
        print("Exiting program, clearing DATAQUEUE")
        DATAQUEUE.clear()
