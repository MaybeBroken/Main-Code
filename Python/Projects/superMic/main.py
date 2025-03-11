import numpy as np
import sounddevice as sd
import threading

# Constants
CHUNK = 1024  # Increased number of audio samples per buffer for higher quality
FORMAT = "float32"  # Audio format (32-bit float for higher precision)
CHANNELS = 1  # Number of audio channels (mono)
RATE = 96000  # Higher sampling rate (samples per second) for better quality
AMPLIFICATION_FACTOR = 15.0  # Initial amplification factor


# Global variable for amplification factor
current_amplification_factor = AMPLIFICATION_FACTOR


def callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    global current_amplification_factor
    # Amplify the audio data
    amplified_data = indata * current_amplification_factor
    # Ensure that values are within the 16-bit range
    amplified_data = np.clip(amplified_data, -32768, 32767)
    # Output the amplified audio data
    outdata[:] = amplified_data


def change_amplification():
    global current_amplification_factor
    while True:
        try:
            new_factor = float(input("Enter new amplification factor: "))
            current_amplification_factor = new_factor
        except ValueError:
            print("Invalid input. Please enter a number.")


# List available input devices
print("Available input devices:")
input_devices = sd.query_devices()
for i, device in enumerate(input_devices):
    if device["max_input_channels"] > 0:
        print(f"{i}: {device['name']}")

# Prompt user to select an input device
device_index = int(input("Select input device index: "))

print("Recording and amplifying... Press Ctrl+C to stop.")

# Start a thread to change amplification factor on the fly
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
        device=(device_index, None),  # Set the input device
    ):
        sd.sleep(int(1e10))  # Keep the stream open indefinitely
except KeyboardInterrupt:
    print("Stopping...")
