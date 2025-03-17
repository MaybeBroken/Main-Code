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
)
from math import radians, degrees, sin, cos, tan, asin, acos, atan2

from matplotlib import (
    pyplot as plt,
    animation as anm,
    colors as cl,
    cm,
)
from direct.interval.IntervalGlobal import *

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
            self.vec_x = float(self.data[0][1])
            self.vec_y = float(self.data[0][2])
            self.vec_z = float(self.data[0][3])
            self.vec_total = float(self.data[1][1])
            self.vec_h = float(self.data[2][1])
            self.vec_p = float(self.data[2][2])
            self.vec_r = float(self.data[2][3])
            self.temp_celcius = float(self.data[3][1])
        except IndexError as e:
            return None
        return self


class SIMULATION(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.setBackgroundColor(0, 0, 0)
        self.camera.setPos(15, 10, 12)
        self.camera.lookAt(0, 0, 0)
        self.model = self.loader.loadModel("models/box")
        self.model.reparentTo(self.render)
        self.task_mgr.add(self.update, "update_task")

    def setModelState(self, data: DATA, task):

        pos_interval = LerpPosInterval(
            self.model, 0.01, (data.vec_x, data.vec_y, data.vec_z)
        )
        hpr_interval = LerpHprInterval(
            self.model, 0.01, (data.vec_h, data.vec_p, data.vec_r)
        )
        pos_interval.start()
        hpr_interval.start()

    def update(self, task):
        global DATAQUEUE
        if DATAQUEUE:
            data = DATAQUEUE.pop(0)
            viewer.set(
                f"Data from Arduino:\n" + "\n".join([str(item) for item in DATAQUEUE])
            )
            formatted_data = DATA(data).format()
            if formatted_data is not None:
                self.setModelState(formatted_data, task)
                plot.add_data(formatted_data)
        return task.cont


class PLOT:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(-10, 10)
        self.lines = {
            "x": self.ax.plot([], [], lw=2, label="X")[0],
            "y": self.ax.plot([], [], lw=2, label="Y")[0],
            "z": self.ax.plot([], [], lw=2, label="Z")[0],
        }
        self.xdata = []
        self.ydata = {"x": [], "y": [], "z": []}
        self.ax.legend()

    def setup(self):
        plt.ion()
        plt.show(block=False)  # Ensure the plot updates in the background

    def add_data(self, data: DATA):
        self.xdata.append(len(self.xdata))
        self.ydata["x"].append(data.vec_x)
        self.ydata["y"].append(data.vec_y)
        self.ydata["z"].append(data.vec_z)
        if len(self.xdata) > 100:
            self.xdata.pop(0)
            self.ydata["x"].pop(0)
            self.ydata["y"].pop(0)
            self.ydata["z"].pop(0)
        for key in self.lines:
            self.lines[key].set_data(self.xdata, self.ydata[key])
        self.fig.canvas.draw_idle()  # Update the plot without bringing it to the front
        self.fig.canvas.flush_events()  # Ensure the plot updates in the background


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

    def disconnect(self): ...
    def close(self): ...
    def write(self, data): ...
    def readline(self):
        return f"0:{randint(0, 10)}:{randint(0, 10)}:{randint(0, 10)}|0:{randint(0, 10)}|0:{randint(0, 10)}:{randint(0, 10)}:{randint(0, 10)}|0:{randint(0, 10)}".encode()


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
            self.start_reading_thread()
        except PermissionError as e:
            print(
                f"PermissionError: {e}. Please check if the port is already in use or if you have the necessary permissions."
            )
        except serial.SerialException as e:
            print(f"Error connecting to Arduino: {e}")

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

    def send_data(self, data):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(data.encode())
        else:
            print("Serial connection is not open")

    def read_data(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                data = self.serial_connection.readline().decode(errors="ignore").strip()
                if data:
                    return data
            except serial.SerialException as e:
                print(f"Error reading data: {e}")
        return None


def list_active_serial_ports():
    """Lists all active serial ports on the system."""
    ports = list_ports.comports()
    active_ports = []
    for port in ports:
        if port.device.startswith("COM") or port.device.startswith("/dev/tty"):
            active_ports.append(port.device)
    return active_ports


ARDUINO: ArduinoSerialInterface = None


def connect(port):
    global ARDUINO
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

    update_simulation()  # Start the simulation update loop

    try:
        window.mainloop()  # Run Tkinter main loop in the main thread
    except KeyboardInterrupt:
        ARDUINO.disconnect()
    finally:
        print("Exiting program, clearing DATAQUEUE")
        DATAQUEUE.clear()
