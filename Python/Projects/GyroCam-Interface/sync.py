from typing import overload
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
)
from math import radians, degrees, sin, cos, tan, asin, acos, atan2

DATAQUEUE = []


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


class timeline:
    def __init__(self):
        self.start_time = time.time()
        self.data = []  # List to store data points as tuples (time, data)
        self.win = Tk()
        self.win.title("Timeline Viewer")
        self.win.geometry("800x600")
        self.win.configure(bg="black")
        self.canvas = Canvas(self.win, bg="black", width=800, height=600)
        self.canvas.pack(fill=BOTH, expand=True)
        self.canvas.create_line(50, 550, 750, 550, fill="white", width=2)  # X-axis
        self.canvas.create_line(50, 550, 50, 50, fill="white", width=2)  # Y-axis
        self.canvas.create_text(
            400, 580, text="Time (s)", fill="white", font=("Arial", 12)
        )
        self.canvas.create_text(
            20, 300, text="Data", fill="white", font=("Arial", 12), angle=90
        )
        self.canvas.create_text(
            400, 20, text="Timeline Viewer", fill="white", font=("Arial", 16)
        )
        self.listCycle = 33

    def build_graph(self):
        self.canvas.delete("data_line")
        if not self.data:
            return
        x_offset = 750
        y_offset = 550
        x_scale = 100
        y_scale = 200
        for i, (time_point, _x, _y, _z) in enumerate(self.data):
            for _i, (data_point, color) in enumerate(
                [(_x, "red"), (_y, "green"), (_z, "blue")]
            ):
                x = x_offset - (time_point * x_scale)
                y = y_offset - (data_point * y_scale)
                if i > 0:
                    previous_time, previous_data = (
                        self.data[i - 1][0],
                        self.data[i - 1][_i],
                    )
                    previous_x = x_offset - (previous_time * x_scale)
                    previous_y = y_offset - (previous_data * y_scale)
                    if (
                        self.listCycle <= 32
                        and self.listCycle != 0
                        and abs(x - previous_x) < 15
                    ):
                        self.canvas.create_line(
                            previous_x,
                            previous_y,
                            x,
                            y,
                            fill=color,
                            width=2,
                            tags="data_line",
                        )

    def add_data_point(self, dataX, dataY, dataZ):
        current_time = time.time() - self.start_time
        self.data.append((current_time, dataX, dataY, dataZ))
        if self.listCycle > 32:
            self.start_time = time.time()
            self.listCycle = 0
        if len(self.data) > 32:
            self.data.pop(0)
            self.listCycle += 1

    def get_data(self):
        return self.data


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
        # Convert degrees to radians for rotation
        h_rad = radians(data.vec_h)
        p_rad = radians(data.vec_p)
        r_rad = radians(data.vec_r)

        self.model.setPos(data.vec_x, data.vec_y, data.vec_z)
        self.model.setHpr(h_rad, p_rad, r_rad)

    def update(self, task):
        for data in DATAQUEUE:
            viewer.set(
                f"Data from Arduino:\n" + "\n".join([str(item) for item in DATAQUEUE])
            )
            formatted_data = DATA(data).format()
            if formatted_data is not None:
                simulation.setModelState(formatted_data, task)
        DATAQUEUE.clear()
        window.update()
        timeline_viewer.build_graph()
        return task.cont


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
        self.window.update()

    def set(self, text):
        self.emulatedData.config(text=text)


class ArduinoSerialInterface:
    def __init__(self, port, baud_rate=115200, timeout=1):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial_connection = None

    def connect(self):
        try:
            self.serial_connection = serial.Serial(
                self.port, self.baud_rate, timeout=self.timeout
            )
            time.sleep(2)
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
                        timeline_viewer.add_data_point(
                            formatted_data.vec_x,
                            formatted_data.vec_y,
                            formatted_data.vec_z,
                        )
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


if __name__ == "__main__":
    window = Tk()
    window.title("Arduino Serial Interface")
    window.geometry("800x600")
    window.configure(bg="black")
    available_ports = list_active_serial_ports()
    if not available_ports:
        print("No serial ports available.")
        exit(1)
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
        command=lambda: connect(ConnectionListbox.get(ACTIVE)),
        bg="black",
        fg="white",
        font=("Courier New", 12),
    )
    connect_button.pack(pady=10)
    viewer = VIEWER()
    simulation = SIMULATION()
    timeline_viewer = timeline()

    try:
        simulation.run()
    except KeyboardInterrupt:
        ARDUINO.disconnect()
