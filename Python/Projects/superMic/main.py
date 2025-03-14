import numpy as np
import sounddevice as sd
import threading

CHUNK = 32
FORMAT = "float32"
CHANNELS = 1
RATE = 44100
AMPLIFICATION_FACTOR = 1

current_amplification_factor = AMPLIFICATION_FACTOR


def callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    global current_amplification_factor
    amplified_data = indata * current_amplification_factor
    amplified_data = np.clip(amplified_data, -32768, 32767)
    # Output the amplified audio data
    outdata[:] = amplified_data


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

print("Recording and amplifying... Press Ctrl+C to stop.")

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
