import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.ndimage import median_filter
import threading
import tkinter as tk
from tkinter import ttk
import os
from scipy.signal import argrelextrema

class MusicVisualizer:
    def __init__(self, show_windows=True):
        # Parameters
        self.DURATION = 1/30
        self.FS = 44100
        self.CHANNELS = 2
        self.FFT_SIZE = 4096

        # Buffer for waveform data (rolling buffer for FFT)
        self.waveform_buffer = np.zeros(self.FFT_SIZE)
        self.buffer_pos = 0

        # Frequency axis for FFT
        self.freqs = np.fft.rfftfreq(self.FFT_SIZE, 1/self.FS)
        self.freq_mask = (self.freqs >= 20) & (self.freqs <= 15000)
        self.freqs_plot = self.freqs[self.freq_mask]

        # Smoothing
        self.spectrum_smooth = np.zeros_like(self.freqs_plot)
        self.alpha = 0.5

        # Beat/rhythm detection state
        self.energy_history = []
        self.energy_history_size = 80

        self.low_energy_history = []
        self.high_energy_history = []
        self.low_band = (self.freqs >= 20) & (self.freqs <= 200)
        self.high_band = (self.freqs >= 2000) & (self.freqs <= 8000)
        self.low_energy_history_size = 20
        self.high_energy_history_size = 20

        self.beat_display_frames = 5
        self.low_beat_frames = 0
        self.high_beat_frames = 0

        # Device selection
        self.STAR_FILE = os.path.join(os.path.dirname(__file__), "starred_device.txt")
        self.input_devices = self.list_input_devices()
        self.device_names = [name for name, idx in self.input_devices]
        self.device_indices = [idx for name, idx in self.input_devices]
        self.starred_idx = self.load_starred_device()
        if self.starred_idx in self.device_indices:
            self.current_device_idx = self.starred_idx
        else:
            self.current_device_idx = self.device_indices[0] if self.device_indices else None

        self.stream = None
        self.ani = None
        self.show_windows = show_windows

        # UI
        self.fig = None
        self.ax = None
        self.line = None
        self.beat_win = None
        self.beat_labels = None

        if self.show_windows:
            self._setup_matplotlib()
            self._setup_beat_window()
            self._setup_device_button()

    def list_input_devices(self):
        devices = sd.query_devices()
        input_devices = []
        for idx, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                name = f"{idx}: {dev['name']}"
                input_devices.append((name, idx))
        return input_devices

    def save_starred_device(self, device_idx):
        with open(self.STAR_FILE, "w") as f:
            f.write(str(device_idx))

    def load_starred_device(self):
        try:
            with open(self.STAR_FILE, "r") as f:
                idx = int(f.read().strip())
                return idx
        except Exception:
            return None

    def _callback(self, indata, frames, time, status):
        # Convert to mono
        audio = np.mean(indata, axis=1)
        n = len(audio)
        if n >= self.FFT_SIZE:
            self.waveform_buffer = audio[-self.FFT_SIZE:]
        else:
            self.waveform_buffer = np.roll(self.waveform_buffer, -n)
            self.waveform_buffer[-n:] = audio

    def start_stream(self, device_idx=None):
        if device_idx is not None:
            self.current_device_idx = device_idx
        if self.stream is not None:
            self.stream.close()
        def stream_callback(indata, frames, time, status):
            self._callback(indata, frames, time, status)
        self.stream = sd.InputStream(
            samplerate=self.FS,
            channels=self.CHANNELS,
            callback=stream_callback,
            blocksize=int(self.FS*self.DURATION),
            device=self.current_device_idx
        )
        self.stream.start()
        if self.show_windows:
            if self.ani is not None:
                self.ani.event_source.stop()
            self.ani = animation.FuncAnimation(self.fig, self.update_plot, interval=33, blit=True)
            plt.draw()

    def stop_stream(self):
        if self.stream is not None:
            self.stream.close()
            self.stream = None
        if self.ani is not None:
            self.ani.event_source.stop()
            self.ani = None

    def _setup_matplotlib(self):
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(left=0.1)
        self.line, = self.ax.plot(self.freqs_plot, np.zeros_like(self.freqs_plot))
        self.ax.set_xlim(20, 15000)
        self.ax.set_ylim(-100, 0)
        self.ax.set_xscale('log')
        self.ax.set_xlabel("Frequency [Hz]")
        self.ax.set_ylabel("Magnitude (dB)")
        self.ax.set_title("Live Frequency Spectrum (20Hz-15kHz)")

    def _setup_device_button(self):
        from matplotlib.widgets import Button
        button_ax = self.fig.add_axes([0.01, 0.92, 0.08, 0.06])
        device_button = Button(button_ax, 'Devices')
        def on_device_button(event):
            threading.Thread(target=self.show_device_selector, daemon=True).start()
        device_button.on_clicked(on_device_button)

    def show_device_selector(self):
        def on_select(event=None):
            idx = combo.current()
            if idx >= 0:
                device_idx = self.device_indices[idx]
                self.start_stream(device_idx)
        def on_star():
            idx = combo.current()
            if idx >= 0:
                device_idx = self.device_indices[idx]
                self.save_starred_device(device_idx)
                star_btn.config(text="Starred!", state="disabled")
        win = tk.Tk()
        win.title("Select Input Device")
        tk.Label(win, text="Input Device:").pack(padx=10, pady=5)
        maxlen = max(len(name) for name in self.device_names) if self.device_names else 20
        combo = ttk.Combobox(win, values=self.device_names, state="readonly", width=maxlen)
        combo.pack(padx=10, pady=5)
        if self.current_device_idx in self.device_indices:
            combo.current(self.device_indices.index(self.current_device_idx))
        else:
            combo.current(0)
        combo.bind("<<ComboboxSelected>>", on_select)
        star_btn = tk.Button(win, text="Star", command=on_star)
        star_btn.pack(pady=5)
        tk.Button(win, text="OK", command=win.destroy).pack(pady=5)
        win.mainloop()

    def _setup_beat_window(self):
        self.beat_win, self.beat_labels = self.create_beat_window()

    def create_beat_window(self):
        win = tk.Tk()
        win.title("Beat/Rhythm Detection")
        labels = {}
        for name, color in [
            ("Low Beat", "red"),
            ("High Beat", "cyan"),
        ]:
            lbl = tk.Label(win, text=name, fg="black", bg="white", width=12, font=("Arial", 14, "bold"))
            lbl.pack(padx=10, pady=2)
            labels[name] = lbl
        volume_lbl = tk.Label(win, text="Volume: 0.00", fg="black", bg="white", width=18, font=("Arial", 12, "bold"))
        volume_lbl.pack(padx=10, pady=8)
        labels["Volume"] = volume_lbl
        return win, labels

    def update_beat_labels(self, low_beat, high_beat, volume=0.0):
        if not self.show_windows:
            return
        self.beat_labels["Low Beat"].config(bg="red" if low_beat else "white", fg="white" if low_beat else "black")
        self.beat_labels["High Beat"].config(bg="cyan" if high_beat else "white", fg="black")
        self.beat_labels["Volume"].config(text=f"Volume: {volume:.2f}")

    def update_plot(self, frame=None):
        # Apply window function
        window = np.hanning(len(self.waveform_buffer))
        windowed = self.waveform_buffer * window
        scale = np.sum(window) / 2
        fft_vals = np.abs(np.fft.rfft(windowed)) / scale
        fft_plot = fft_vals[self.freq_mask]
        fft_plot = np.maximum(fft_plot, np.finfo(float).eps)
        fft_plot_db = 20 * np.log10(fft_plot)

        # Smoothing and noise removal
        fft_plot_db = median_filter(fft_plot_db, size=5)
        kernel = np.ones(5) / 5
        fft_plot_db = np.convolve(fft_plot_db, kernel, mode='same')
        self.spectrum_smooth = self.alpha * fft_plot_db + (1 - self.alpha) * self.spectrum_smooth

        # Energy calculations for bands
        low_energy = np.sum(fft_vals[self.low_band])
        self.low_energy_history.append(low_energy)
        if len(self.low_energy_history) > self.low_energy_history_size:
            self.low_energy_history.pop(0)
        avg_low_energy = np.mean(self.low_energy_history) if self.low_energy_history else 0

        high_energy = np.sum(fft_vals[self.high_band])
        self.high_energy_history.append(high_energy)
        if len(self.high_energy_history) > self.high_energy_history_size:
            self.high_energy_history.pop(0)
        avg_high_energy = np.mean(self.high_energy_history) if self.high_energy_history else 0

        # Compute total volume (RMS of waveform_buffer)
        volume = np.sqrt(np.mean(self.waveform_buffer ** 2))

        # Beat detection
        low_beat = False
        high_beat = False
        if len(self.low_energy_history) >= 3:
            prev = self.low_energy_history[-2]
            curr = self.low_energy_history[-1]
            if avg_low_energy > 0 and curr > 1.3 * avg_low_energy and curr > 1.2 * prev:
                low_beat = True
                self.low_beat_frames = self.beat_display_frames
        if self.low_beat_frames > 0:
            low_beat = True
            self.low_beat_frames -= 1

        if len(self.high_energy_history) >= 3:
            prev = self.high_energy_history[-2]
            curr = self.high_energy_history[-1]
            if avg_high_energy > 0 and curr > 1.3 * avg_high_energy and curr > 1.2 * prev:
                high_beat = True
                self.high_beat_frames = self.beat_display_frames
        if self.high_beat_frames > 0:
            high_beat = True
            self.high_beat_frames -= 1

        self.update_beat_labels(low_beat, high_beat, volume)

        if self.show_windows:
            self.line.set_color('blue')
            self.line.set_ydata(self.spectrum_smooth)
            return self.line,

    def run(self):
        print("Recording system audio... (Press Ctrl+C to stop)")
        self.start_stream(self.current_device_idx)
        if self.show_windows:
            threading.Thread(target=self.beat_win.mainloop, daemon=True).start()
            plt.show()

    # --- API methods for headless use ---
    def get_spectrum(self):
        # Returns the latest smoothed spectrum (dB)
        return self.freqs_plot, self.spectrum_smooth.copy()

    def get_volume(self):
        return np.sqrt(np.mean(self.waveform_buffer ** 2))

    def get_beat_status(self):
        # Returns (low_beat, high_beat)
        # (recompute using latest data)
        window = np.hanning(len(self.waveform_buffer))
        windowed = self.waveform_buffer * window
        scale = np.sum(window) / 2
        fft_vals = np.abs(np.fft.rfft(windowed)) / scale
        low_energy = np.sum(fft_vals[self.low_band])
        high_energy = np.sum(fft_vals[self.high_band])
        avg_low = np.mean(self.low_energy_history) if self.low_energy_history else 0
        avg_high = np.mean(self.high_energy_history) if self.high_energy_history else 0
        low_beat = avg_low > 0 and low_energy > 1.3 * avg_low
        high_beat = avg_high > 0 and high_energy > 1.3 * avg_high
        return low_beat, high_beat

# --- Example usage as script or module ---
if __name__ == "__main__":
    # To run with UI windows:
    vis = MusicVisualizer(show_windows=True)
    vis.run()
    # To run headless (no UI), use:
    # vis = MusicVisualizer(show_windows=False)
    # vis.start_stream()
    # ...poll vis.get_spectrum(), vis.get_volume(), vis.get_beat_status() as needed...
