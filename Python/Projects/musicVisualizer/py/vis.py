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
        self.DURATION = 1 / 30
        self.FS = 44100
        self.CHANNELS = 2
        self.FFT_SIZE = 4096

        # Buffer for waveform data (rolling buffer for FFT)
        self.waveform_buffer = np.zeros(self.FFT_SIZE)
        self.buffer_pos = 0

        # Frequency axis for FFT
        self.freqs = np.fft.rfftfreq(self.FFT_SIZE, 1 / self.FS)
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
        self.high_band = (self.freqs >= 4000) & (self.freqs <= 10000)
        self.low_energy_history_size = 15
        self.high_energy_history_size = 15

        self.beat_display_frames = 5
        self.low_beat_frames = 0
        self.high_beat_frames = 0

        # --- Initialize beat detection histories with max values for instant detection ---
        self._init_beat_histories()

        # Device selection
        self.STAR_FILE = os.path.join(os.path.dirname(__file__), "starred_device.txt")
        self.input_devices = self.list_input_devices()
        self.device_names = [name for name, idx in self.input_devices]
        self.device_indices = [idx for name, idx in self.input_devices]
        self.starred_idx = self.load_starred_device()
        if self.starred_idx in self.device_indices:
            self.current_device_idx = self.starred_idx
        else:
            self.current_device_idx = (
                self.device_indices[0] if self.device_indices else None
            )

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
            if dev["max_input_channels"] > 0:
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
            self.waveform_buffer = audio[-self.FFT_SIZE :]
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
            blocksize=int(self.FS * self.DURATION),
            device=self.current_device_idx,
        )
        self.stream.start()
        if self.show_windows:
            if self.ani is not None:
                self.ani.event_source.stop()
            self.ani = animation.FuncAnimation(
                self.fig, self.update_plot, interval=33, blit=True
            )
            plt.draw()

    def stop_stream(self):
        if self.stream is not None:
            self.stream.close()
            self.stream = None
        if self.ani is not None:
            self.ani.event_source.stop()
            self.ani = None

    def _setup_matplotlib(self):
        import matplotlib.pyplot as plt

        plt.ion()  # Ensure interactive mode is on
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(left=0.1, bottom=0.18)  # Leave space for button at bottom
        (self.line,) = self.ax.plot(self.freqs_plot, np.zeros_like(self.freqs_plot))
        self.ax.set_xlim(20, 15000)
        self.ax.set_ylim(-100, 0)
        self.ax.set_xscale("log")
        self.ax.set_xlabel("Frequency [Hz]")
        self.ax.set_ylabel("Magnitude (dB)")
        self.ax.set_title("Live Frequency Spectrum (20Hz-15kHz)")

    def _setup_device_button(self):
        from matplotlib.widgets import Button

        # Place button at bottom center, below the plot
        button_ax = self.fig.add_axes([0.4, 0.05, 0.2, 0.07])
        device_button = Button(button_ax, "Devices")

        # Store a reference to avoid garbage collection
        self._device_button = device_button

        def on_device_button(event):
            print("Opening device selector...")
            self.show_device_selector()
            plt.pause(0.01)

        # Use Button's .on_clicked method, but ensure the reference is kept
        device_button.on_clicked(on_device_button)

    def show_device_selector(self):
        import tkinter as tk
        from tkinter import ttk

        # Use Toplevel if a root window exists, else create root
        root = None
        try:
            root = tk._default_root
        except Exception:
            pass
        if root is None:
            root = tk.Tk()
            root.withdraw()  # Hide the root window

        win = tk.Toplevel(root)
        win.title("Select Input Device")
        tk.Label(win, text="Input Device:").pack(padx=10, pady=5)
        maxlen = max((len(name) for name in self.device_names), default=20)
        combo = ttk.Combobox(
            win, values=self.device_names, state="readonly", width=maxlen
        )
        combo.pack(padx=10, pady=5)
        if self.current_device_idx in self.device_indices:
            combo.current(self.device_indices.index(self.current_device_idx))
        else:
            combo.current(0)

        star_btn = tk.Button(win, text="Star")
        star_btn.pack(pady=5)

        def on_select(event=None):
            idx = combo.current()
            if idx >= 0:
                device_idx = self.device_indices[idx]
                self.start_stream(device_idx)
                star_btn.config(text="Star", state="normal")

        def on_star():
            idx = combo.current()
            if idx >= 0:
                device_idx = self.device_indices[idx]
                self.save_starred_device(device_idx)
                star_btn.config(text="Starred!", state="disabled")

        combo.bind("<<ComboboxSelected>>", on_select)
        star_btn.config(command=on_star)

        def on_ok():
            win.destroy()

        tk.Button(win, text="OK", command=on_ok).pack(pady=5)
        win.transient(root)
        win.grab_set()
        win.focus_set()
        # Do not call win.wait_window(); let the window be non-blocking

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
            lbl = tk.Label(
                win,
                text=name,
                fg="black",
                bg="white",
                width=12,
                font=("Arial", 14, "bold"),
            )
            lbl.pack(padx=10, pady=2)
            labels[name] = lbl
        volume_lbl = tk.Label(
            win,
            text="Volume: 0.00",
            fg="black",
            bg="white",
            width=18,
            font=("Arial", 12, "bold"),
        )
        volume_lbl.pack(padx=10, pady=8)
        labels["Volume"] = volume_lbl
        return win, labels

    def update_beat_labels(self, low_beat, high_beat, volume=0.0):
        if not self.show_windows:
            return
        self.beat_labels["Low Beat"].config(
            bg="red" if low_beat else "white", fg="white" if low_beat else "black"
        )
        self.beat_labels["High Beat"].config(
            bg="cyan" if high_beat else "white", fg="black"
        )
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
        self.spectrum_raw = fft_plot_db

        # Smoothing and noise removal
        fft_plot_db = median_filter(fft_plot_db, size=5)
        kernel = np.ones(5) / 5
        fft_plot_db = np.convolve(fft_plot_db, kernel, mode="same")
        self.spectrum_smooth = (
            self.alpha * fft_plot_db + (1 - self.alpha) * self.spectrum_smooth
        )

        # Energy calculations for bands
        low_energy = np.sum(fft_vals[self.low_band])
        self.low_energy_history.append(low_energy)
        if len(self.low_energy_history) > self.low_energy_history_size:
            self.low_energy_history.pop(0)
        avg_low_energy = (
            np.mean(self.low_energy_history) if self.low_energy_history else 0
        )

        high_energy = np.sum(fft_vals[self.high_band])
        self.high_energy_history.append(high_energy)
        if len(self.high_energy_history) > self.high_energy_history_size:
            self.high_energy_history.pop(0)
        avg_high_energy = (
            np.mean(self.high_energy_history) if self.high_energy_history else 0
        )

        # Compute total volume (RMS of waveform_buffer)
        volume = np.sqrt(np.mean(self.waveform_buffer**2))

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
            if (
                avg_high_energy > 0
                and curr > 1.3 * avg_high_energy
                and curr > 1.2 * prev
            ):
                high_beat = True
                self.high_beat_frames = self.beat_display_frames
        if self.high_beat_frames > 0:
            high_beat = True
            self.high_beat_frames -= 1

        self.update_beat_labels(low_beat, high_beat, volume)

        if self.show_windows:
            self.line.set_color("blue")
            self.line.set_ydata(self.spectrum_smooth)
            return (self.line,)

    def run(self):
        print("Recording system audio... (Press Ctrl+C to stop)")
        self.start_stream(self.current_device_idx)
        if self.show_windows:
            # Run both Tk and Matplotlib in the main thread, non-threaded
            self.beat_win.after(100, lambda: None)  # Ensure Tk is processing events
            plt.show()
            try:
                self.beat_win.mainloop()
            except Exception:
                pass

    def log_to_linear_bins(self, log_data, f_min=20, f_max=2000, num_linear_bins=64):
        """
        Converts log-spaced FFT-like data into linearly spaced bins.

        Parameters:
            log_data: 1D array of values sampled in log-frequency space
            f_min: minimum frequency represented in log_data
            f_max: maximum frequency represented in log_data
            num_linear_bins: number of bins for linear output

        Returns:
            linear_bins: 1D array of averaged values, length = num_linear_bins
        """
        num_log_bins = len(log_data)

        # Step 1: Frequencies corresponding to log_data samples
        log_freqs = np.logspace(np.log10(f_min), np.log10(f_max), num_log_bins)

        # Step 2: Create linear frequency bins
        linear_freq_edges = np.linspace(f_min, f_max, num_linear_bins + 1)
        linear_bins = np.zeros(num_linear_bins)

        for i in range(num_linear_bins):
            # Find all log-freqs that fall within this linear bin
            in_bin = (log_freqs >= linear_freq_edges[i]) & (
                log_freqs < linear_freq_edges[i + 1]
            )
            if np.any(in_bin):
                linear_bins[i] = np.mean(log_data[in_bin])
            else:
                linear_bins[i] = 0

        return linear_bins

    # --- API methods for headless use ---
    def get_spectrum(self):
        # Returns the latest smoothed spectrum (dB)
        return (
            self.freqs_plot,
            self.log_to_linear_bins(self.spectrum_smooth),
            self.log_to_linear_bins(self.spectrum_raw),
        )

    def get_volume(self):
        return np.sqrt(np.mean(self.waveform_buffer**2))

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
        low_beat = avg_low > 0 and low_energy > 1.2 * avg_low
        high_beat = avg_high > 0 and high_energy > 1.2 * avg_high
        return low_beat, high_beat

    def get_mood_energy(self):
        """
        Returns a tuple (mood, energy_level) where:
        - mood: 'calm', 'neutral', or 'energetic'
        - energy_level: float in [0, 1], higher means more energetic
        """
        # Compute spectral centroid (brightness) and volume (RMS)
        window = np.hanning(len(self.waveform_buffer))
        windowed = self.waveform_buffer * window
        scale = np.sum(window) / 2
        fft_vals = np.abs(np.fft.rfft(windowed)) / scale
        fft_vals = np.maximum(fft_vals, np.finfo(float).eps)
        freqs = self.freqs

        # Spectral centroid (weighted mean frequency)
        centroid = np.sum(freqs * fft_vals) / np.sum(fft_vals)
        # Normalize centroid to [0, 1] (20Hz-15kHz)
        centroid_norm = (centroid - 20) / (15000 - 20)
        centroid_norm = np.clip(centroid_norm, 0, 1)

        # Volume (RMS), normalized to a reasonable range
        volume = np.sqrt(np.mean(self.waveform_buffer**2))
        volume_norm = np.clip(volume / 0.2, 0, 1)  # 0.2 is a typical loud RMS

        # Combine for energy
        energy_level = 0.6 * centroid_norm + 0.4 * volume_norm

        # Mood classification
        if energy_level < 0.33:
            mood = "calm"
        elif energy_level > 0.66:
            mood = "energetic"
        else:
            mood = "neutral"
        return mood, float(energy_level)

    def _init_beat_histories(self):
        # Fill histories with high values to allow instant beat detection
        self.low_energy_history = [1e6] * self.low_energy_history_size
        self.high_energy_history = [1e6] * self.high_energy_history_size


# --- Example usage as script or module ---
if __name__ == "__main__":
    # To run with UI windows:
    vis = MusicVisualizer(show_windows=True)
    vis.run()
    # To run headless (no UI), use:
    # vis = MusicVisualizer(show_windows=False)
    # vis.start_stream()
    # ...poll vis.get_spectrum(), vis.get_volume(), vis.get_beat_status() as needed...
