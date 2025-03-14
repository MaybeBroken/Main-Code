import numpy as np
import sounddevice as sd
import threading
import os
import platform

CHUNK = 128
FORMAT = "float32"
CHANNELS = 1
RATE = 44100
AMPLIFICATION_FACTOR = 15

current_amplification_factor = AMPLIFICATION_FACTOR


def callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    global current_amplification_factor
    volume = np.linalg.norm(indata) * current_amplification_factor
    set_system_volume(volume)


def set_system_volume(volume):
    # Normalize volume to a range of 0 to 100
    normalized_volume = min(max(int(volume * 100), 0), 100)
    system = platform.system()
    if system == "Windows":
        # Set system volume for Windows
        os.system(f"nircmd.exe setsysvolume {normalized_volume * 655.35}")
    elif system == "Darwin":
        # Set system volume for macOS
        os.system(f"osascript -e 'set volume output volume {normalized_volume}'")
    else:
        print(f"Unsupported OS: {system}")


def change_amplification():
    global current_amplification_factor
    while True:
        try:
            new_factor = float(input(""))
            current_amplification_factor = new_factor
        except ValueError:
            print("Invalid input. Please enter a number.")


print("Available input devices:")
input_devices = sd.query_devices()
for i, device in enumerate(input_devices):
    if device["max_input_channels"] > 0:
        print(f"{i}: {device['name']}")

device_index = int(input("Select input device index: "))

print("Recording and adjusting volume... Press Ctrl+C to stop.")

thread = threading.Thread(target=change_amplification)
thread.daemon = True
thread.start()

try:
    with sd.Stream(
        samplerate=RATE,
        blocksize=CHUNK,
        dtype=FORMAT,
        channels=CHANNELS,
        callback=callback,
        device=(device_index, None),
    ):
        while True:
            sd.sleep(int(1e10))
except KeyboardInterrupt:
    print("Stopping...")
