import numpy as np
import sounddevice as sd
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# Prefer concise, reliable devices by default
EXCLUDE_TOKENS = (
    "Voicemeeter",
    "Steam",
    "OCULUS",
    "Wave",
    "bthhfenum",
    "Hands-Free",
    "Headset",
    "VAD",
    "Speakers Wave",
    "Microphone Wave",
    "()",
)
ALWAYS_INCLUDE_TOKENS = (
    "NVIDIA Broadcast",
    "NVIDIA RTX Voice",
)
PREFERRED_HOSTAPI_NAMES = (
    "Windows WASAPI",
    "Windows WDM-KS",
    "Windows DirectSound",
    "MME",
    "ASIO",
)

CHUNK = 256
FORMAT = "float32"
CHANNELS = 1
RATE = 44100
AMPLIFICATION_FACTOR = 1.0

current_amplification_factor = AMPLIFICATION_FACTOR
stream = None
stream_lock = threading.Lock()

# Noise reduction globals
noise_enabled = False
noise_psd = None
noise_lock = threading.Lock()
learn_blocks_remaining = 0
noise_strength = 1.0  # suppression amount
noise_floor = 0.05  # minimum gain floor
noise_blend = 0.5  # blend between original and denoised (0=original, 1=full NR)
gain_smooth = 0.6  # temporal smoothing of gain (0=no memory, 1=slow changes)
freq_smooth_bins = 2  # simple frequency smoothing half-width in bins
prev_gain = None  # to carry gain between blocks


def callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    x = indata[:, 0] if indata.ndim > 1 else indata

    global noise_psd, learn_blocks_remaining, prev_gain

    # Learn/update noise profile
    if learn_blocks_remaining > 0:
        X = np.fft.rfft(x)
        curr_psd = np.abs(X) ** 2
        with noise_lock:
            if noise_psd is None or noise_psd.shape != curr_psd.shape:
                noise_psd = curr_psd.copy()
            else:
                noise_psd = 0.9 * noise_psd + 0.1 * curr_psd
        learn_blocks_remaining -= 1

    y = x

    if noise_enabled:
        with noise_lock:
            psd = None if noise_psd is None else noise_psd.copy()
        if psd is not None:
            X = np.fft.rfft(y)
            Syy = np.abs(X) ** 2
            eps = 1e-8

            # Base Wiener-like gain
            g = 1.0 - noise_strength * (psd / (Syy + eps))
            g = np.clip(g, noise_floor, 1.0)

            # Frequency smoothing (moving average in the spectral domain)
            if freq_smooth_bins > 0:
                k = int(freq_smooth_bins)
                if k > 0:
                    kernel = np.ones(2 * k + 1, dtype=np.float32)
                    kernel /= kernel.sum()
                    g = np.convolve(g, kernel, mode="same")
                    g = np.clip(g, noise_floor, 1.0)

            # Temporal smoothing of gain across blocks
            if prev_gain is None or prev_gain.shape != g.shape:
                prev_gain = g.copy()
            else:
                a = float(np.clip(gain_smooth, 0.0, 0.99))
                g = a * prev_gain + (1.0 - a) * g
                prev_gain = g.copy()

            # Apply gain
            Y = g * X
            y_nr = np.fft.irfft(Y, n=y.shape[0])

            # Blend original and denoised
            b = float(np.clip(noise_blend, 0.0, 1.0))
            y = (1.0 - b) * y + b * y_nr

    # Amplify and output
    amp = current_amplification_factor
    amplified = np.clip(y * amp, -1.0, 1.0).astype(np.float32)
    outdata[:] = amplified.reshape(outdata.shape)


def list_devices():
    devices = sd.query_devices()
    try:
        default_in, default_out = sd.default.device
    except Exception:
        default_in, default_out = (None, None)
    return devices, default_in, default_out


def preferred_hostapi_index():
    hostapis = sd.query_hostapis()
    # Map names to index
    name_to_idx = {h.get("name"): i for i, h in enumerate(hostapis)}
    for name in PREFERRED_HOSTAPI_NAMES:
        if name in name_to_idx:
            return name_to_idx[name]
    # Fallback to first
    return 0 if hostapis else None


def device_is_recommended(dev, is_input, preferred_idx):
    chans = dev.get("max_input_channels" if is_input else "max_output_channels", 0)
    if chans < CHANNELS:
        return False
    name = dev.get("name") or ""
    # Always include NVIDIA virtual devices if present (they provide RTX/Broadcast NR)
    if any(tok in name for tok in ALWAYS_INCLUDE_TOKENS):
        return True
    if preferred_idx is not None and dev.get("hostapi") != preferred_idx:
        return False
    if any(tok in name for tok in EXCLUDE_TOKENS):
        return False
    return True


def filtered_indices(devices, is_input, recommended=True):
    if not recommended:
        return [
            i
            for i, d in enumerate(devices)
            if d.get("max_input_channels" if is_input else "max_output_channels", 0)
            >= CHANNELS
        ]
    pref_idx = preferred_hostapi_index()
    return [
        i for i, d in enumerate(devices) if device_is_recommended(d, is_input, pref_idx)
    ]


def choose_samplerate(devices, i, o):
    try:
        in_sr = devices[i].get("default_samplerate") or RATE
        out_sr = devices[o].get("default_samplerate") or RATE
        sr = int(round(min(in_sr, out_sr)))
        return sr
    except Exception:
        return RATE


def outputs_compatible_with_input(devices, input_idx, recommended=True, limit=12):
    outs = filtered_indices(devices, is_input=False, recommended=recommended)
    compatible = []
    for o in outs:
        sr = choose_samplerate(devices, input_idx, o)
        try:
            test = sd.Stream(
                samplerate=sr,
                blocksize=CHUNK,
                dtype=FORMAT,
                channels=CHANNELS,
                callback=callback,
                device=(input_idx, o),
            )
            test.close()
            compatible.append(o)
            if len(compatible) >= limit:
                break
        except Exception:
            continue
    return compatible


def find_compatible_pair(pref_in=None, recommended=True, prefer_nvidia=False):
    devices, default_in, default_out = list_devices()
    ins = filtered_indices(devices, is_input=True, recommended=recommended)
    outs = filtered_indices(devices, is_input=False, recommended=recommended)

    def nvidia_first(indices):
        if not prefer_nvidia:
            return indices
        nv = [
            i
            for i in indices
            if any(
                tok in (devices[i].get("name") or "") for tok in ALWAYS_INCLUDE_TOKENS
            )
        ]
        rest = [i for i in indices if i not in nv]
        return nv + rest

    ordered_inputs = []
    if pref_in is not None and pref_in in ins:
        ordered_inputs.append(pref_in)
    if (
        default_in is not None
        and default_in in ins
        and default_in not in ordered_inputs
    ):
        ordered_inputs.append(default_in)
    ordered_inputs += [i for i in ins if i not in ordered_inputs]
    ordered_inputs = nvidia_first(ordered_inputs)

    ordered_outputs = []
    if default_out is not None and default_out in outs:
        ordered_outputs.append(default_out)
    ordered_outputs += [o for o in outs if o not in ordered_outputs]
    ordered_outputs = nvidia_first(ordered_outputs)

    for i in ordered_inputs:
        compatible_outs = (
            outputs_compatible_with_input(devices, i, recommended=recommended)
            or ordered_outputs
        )
        compatible_outs = nvidia_first(compatible_outs)
        for o in compatible_outs:
            sr = choose_samplerate(devices, i, o)
            try:
                test = sd.Stream(
                    samplerate=sr,
                    blocksize=CHUNK,
                    dtype=FORMAT,
                    channels=CHANNELS,
                    callback=callback,
                    device=(i, o),
                )
                test.close()
                return i, o
            except Exception:
                continue
    return None, None


def _name_with_tags(dev, idx, is_in, default_in, default_out):
    name = dev.get("name") or f"Device {idx}"
    tags = []
    if any(tok in name for tok in ALWAYS_INCLUDE_TOKENS):
        tags.append("NVIDIA NR")
    if (is_in and idx == default_in) or ((not is_in) and idx == default_out):
        tags.append("default")
    if tags:
        name = f"{name} [{'|'.join(tags)}]"
    return f"{idx}: {name}"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("superMic")
        self.geometry("680x360")

        self.devices, self.default_in, self.default_out = list_devices()
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.recommended_var = tk.BooleanVar(value=True)
        self.is_running = False

        # Noise UI state
        self.noise_enabled_var = tk.BooleanVar(value=False)
        self.noise_strength_var = tk.DoubleVar(value=noise_strength)
        self.noise_floor_var = tk.DoubleVar(value=noise_floor)
        self.noise_blend_var = tk.DoubleVar(value=noise_blend)
        self.gain_smooth_var = tk.DoubleVar(value=gain_smooth)
        self.freq_smooth_var = tk.IntVar(value=freq_smooth_bins)

        # NVIDIA pref
        self.prefer_nvidia_var = tk.BooleanVar(value=True)

        self._build_ui()
        self.refresh_devices(auto_select=True)

    def _build_ui(self):
        pad = {"padx": 8, "pady": 6}

        frm = ttk.Frame(self)
        frm.pack(fill=tk.BOTH, expand=True)

        # Input device
        ttk.Label(frm, text="Input device:").grid(row=0, column=0, sticky="w", **pad)
        self.input_combo = ttk.Combobox(
            frm, textvariable=self.input_var, state="readonly", width=60
        )
        self.input_combo.grid(row=0, column=1, sticky="ew", **pad)
        self.input_combo.bind("<<ComboboxSelected>>", lambda e: self._on_input_change())

        # Output device
        ttk.Label(frm, text="Output device:").grid(row=1, column=0, sticky="w", **pad)
        self.output_combo = ttk.Combobox(
            frm, textvariable=self.output_var, state="readonly", width=60
        )
        self.output_combo.grid(row=1, column=1, sticky="ew", **pad)

        # Amplification
        ttk.Label(frm, text="Amplification:").grid(row=2, column=0, sticky="w", **pad)
        self.amp = tk.DoubleVar(value=AMPLIFICATION_FACTOR)
        self.amp_scale = ttk.Scale(
            frm,
            from_=0.0,
            to=100.0,
            variable=self.amp,
            orient=tk.HORIZONTAL,
            command=self._on_amp_change,
        )
        self.amp_scale.grid(row=2, column=1, sticky="ew", **pad)

        # Options row
        opts = ttk.Frame(frm)
        opts.grid(row=3, column=0, columnspan=2, sticky="w", **pad)
        ttk.Checkbutton(
            opts,
            text="Recommended only",
            variable=self.recommended_var,
            command=lambda: self.refresh_devices(auto_select=False),
        ).pack(side=tk.LEFT)
        ttk.Checkbutton(
            opts,
            text="Prefer NVIDIA RTX/Broadcast",
            variable=self.prefer_nvidia_var,
            command=lambda: self.refresh_devices(auto_select=False),
        ).pack(side=tk.LEFT, padx=8)

        # Noise reduction controls
        nfrm = ttk.LabelFrame(frm, text="Noise Reduction")
        nfrm.grid(row=4, column=0, columnspan=2, sticky="ew", padx=8, pady=4)
        ttk.Checkbutton(
            nfrm,
            text="Enable",
            variable=self.noise_enabled_var,
            command=self._on_noise_toggle,
        ).grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Button(nfrm, text="Learn Noise (3s)", command=self._learn_noise).grid(
            row=0, column=1, sticky="w", padx=6, pady=4
        )
        ttk.Button(nfrm, text="Clear Profile", command=self._clear_noise).grid(
            row=0, column=2, sticky="w", padx=6, pady=4
        )

        ttk.Label(nfrm, text="Strength:").grid(row=1, column=0, sticky="e", padx=6)
        ttk.Scale(
            nfrm,
            from_=0.0,
            to=2.0,
            variable=self.noise_strength_var,
            orient=tk.HORIZONTAL,
            command=self._on_noise_params,
        ).grid(row=1, column=1, columnspan=2, sticky="ew", padx=6)
        ttk.Label(nfrm, text="Floor:").grid(row=2, column=0, sticky="e", padx=6)
        ttk.Scale(
            nfrm,
            from_=0.0,
            to=0.5,
            variable=self.noise_floor_var,
            orient=tk.HORIZONTAL,
            command=self._on_noise_params,
        ).grid(row=2, column=1, columnspan=2, sticky="ew", padx=6)
        ttk.Label(nfrm, text="Blend:").grid(row=3, column=0, sticky="e", padx=6)
        ttk.Scale(
            nfrm,
            from_=0.0,
            to=1.0,
            variable=self.noise_blend_var,
            orient=tk.HORIZONTAL,
            command=self._on_noise_params,
        ).grid(row=3, column=1, columnspan=2, sticky="ew", padx=6)
        ttk.Label(nfrm, text="Smooth (time):").grid(row=4, column=0, sticky="e", padx=6)
        ttk.Scale(
            nfrm,
            from_=0.0,
            to=0.95,
            variable=self.gain_smooth_var,
            orient=tk.HORIZONTAL,
            command=self._on_noise_params,
        ).grid(row=4, column=1, columnspan=2, sticky="ew", padx=6)
        ttk.Label(nfrm, text="Freq smooth (bins):").grid(
            row=5, column=0, sticky="e", padx=6
        )
        self.freq_spin = ttk.Spinbox(
            nfrm,
            from_=0,
            to=10,
            textvariable=self.freq_smooth_var,
            width=5,
            command=self._on_noise_params,
        )
        self.freq_spin.grid(row=5, column=1, sticky="w", padx=6)
        nfrm.columnconfigure(1, weight=1)

        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, sticky="ew")
        ttk.Button(
            btns,
            text="Refresh",
            command=lambda: self.refresh_devices(auto_select=False),
        ).pack(side=tk.LEFT, padx=4)
        self.start_btn = ttk.Button(btns, text="Start", command=self.start_stream)
        self.start_btn.pack(side=tk.LEFT, padx=4)
        self.stop_btn = ttk.Button(
            btns, text="Stop", command=self.stop_stream, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=4)

        # Status
        ttk.Label(frm, textvariable=self.status_var).grid(
            row=6, column=0, columnspan=2, sticky="w", **pad
        )

        frm.columnconfigure(1, weight=1)

    def _on_amp_change(self, _):
        global current_amplification_factor
        current_amplification_factor = float(self.amp.get())

    def _fmt(self, i, is_in):
        d = self.devices[i]
        return _name_with_tags(d, i, is_in, self.default_in, self.default_out)

    def _on_input_change(self):
        i, _ = self._selected_indices()
        if i is None:
            return
        outs = outputs_compatible_with_input(
            self.devices, i, recommended=self.recommended_var.get()
        )
        self.output_combo["values"] = [self._fmt(o, is_in=False) for o in outs]
        if outs:
            self.output_combo.current(0)
        self.status_var.set(f"Filtered outputs: {len(outs)} compatible")

    def refresh_devices(self, auto_select=True):
        self.devices, self.default_in, self.default_out = list_devices()
        rec = self.recommended_var.get()
        inputs = filtered_indices(self.devices, is_input=True, recommended=rec)

        self.input_combo["values"] = [self._fmt(i, is_in=True) for i in inputs]

        tip_found = any(
            (
                d.get("name")
                and any(tok in d.get("name") for tok in ALWAYS_INCLUDE_TOKENS)
            )
            and d.get("max_input_channels", 0) >= CHANNELS
            for d in self.devices
        )

        if auto_select:
            sel_in, sel_out = find_compatible_pair(
                pref_in=self.default_in,
                recommended=rec,
                prefer_nvidia=self.prefer_nvidia_var.get(),
            )
            if sel_in is not None and sel_out is not None:
                if sel_in in inputs:
                    self.input_combo.current(inputs.index(sel_in))
                else:
                    if inputs:
                        self.input_combo.current(0)
                        sel_in = inputs[0]
                outs = outputs_compatible_with_input(
                    self.devices, sel_in, recommended=rec
                )
                self.output_combo["values"] = [self._fmt(o, is_in=False) for o in outs]
                if sel_out in outs:
                    self.output_combo.current(outs.index(sel_out))
                elif outs:
                    self.output_combo.current(0)
                    sel_out = outs[0]
                tip = (
                    " | Tip: NVIDIA Broadcast/RTX Voice input detected"
                    if tip_found
                    else ""
                )
                self.status_var.set(f"Selected input {sel_in}, output {sel_out}{tip}")
            else:
                outs = filtered_indices(self.devices, is_input=False, recommended=rec)
                self.output_combo["values"] = [self._fmt(o, is_in=False) for o in outs]
                tip = (
                    " Tip: NVIDIA Broadcast/RTX Voice input detected"
                    if tip_found
                    else ""
                )
                self.status_var.set(
                    "No compatible pair found. Adjust filters or Refresh." + tip
                )
        else:
            i, _ = self._selected_indices()
            if i is None and inputs:
                self.input_combo.current(0)
                i = inputs[0]
            outs = (
                outputs_compatible_with_input(self.devices, i, recommended=rec)
                if i is not None
                else filtered_indices(self.devices, is_input=False, recommended=rec)
            )
            self.output_combo["values"] = [self._fmt(o, is_in=False) for o in outs]
            if outs:
                self.output_combo.current(0)
            tip = " | NVIDIA Broadcast/RTX Voice available" if tip_found else ""
            self.status_var.set(
                f"Devices: {len(inputs)} inputs, {len(outs)} outputs shown{tip}"
            )

    def _selected_indices(self):
        def parse_index(text):
            try:
                return int(str(text).split(":", 1)[0])
            except Exception:
                return None

        return parse_index(self.input_var.get()), parse_index(self.output_var.get())

    def start_stream(self):
        if self.is_running:
            return
        i, o = self._selected_indices()
        if i is None or o is None:
            messagebox.showerror(
                "Error", "Please select both input and output devices."
            )
            return
        sr = choose_samplerate(self.devices, i, o)
        try:
            global stream
            with stream_lock:
                stream = sd.Stream(
                    samplerate=sr,
                    blocksize=CHUNK,
                    dtype=FORMAT,
                    channels=CHANNELS,
                    callback=callback,
                    device=(i, o),
                )
                stream.start()
            self.is_running = True
            self.start_btn.configure(state=tk.DISABLED)
            self.stop_btn.configure(state=tk.NORMAL)
            self.status_var.set(f"Streaming @ {sr} Hz from {i} to {o}")
        except Exception as e:
            messagebox.showerror("Error opening stream", str(e))
            self.status_var.set("Failed to start stream.")

    def stop_stream(self):
        if not self.is_running:
            return
        global stream
        try:
            with stream_lock:
                if stream is not None:
                    stream.stop()
                    stream.close()
                    stream = None
            self.is_running = False
            self.start_btn.configure(state=tk.NORMAL)
            self.stop_btn.configure(state=tk.DISABLED)
            self.status_var.set("Stopped.")
        except Exception as e:
            messagebox.showwarning("Warning", f"Error stopping stream: {e}")

    def _on_noise_toggle(self):
        global noise_enabled
        noise_enabled = bool(self.noise_enabled_var.get())
        self.status_var.set(
            f"Noise reduction {'enabled' if noise_enabled else 'disabled'}"
        )

    def _on_noise_params(self, _=None):
        global noise_strength, noise_floor, noise_blend, gain_smooth, freq_smooth_bins
        noise_strength = float(self.noise_strength_var.get())
        noise_floor = float(self.noise_floor_var.get())
        noise_blend = float(self.noise_blend_var.get())
        gain_smooth = float(self.gain_smooth_var.get())
        freq_smooth_bins = int(self.freq_smooth_var.get())

    def _learn_noise(self):
        # Learn noise for ~3 seconds (while user keeps environment quiet)
        global learn_blocks_remaining
        blocks = int(3 * RATE / CHUNK)
        learn_blocks_remaining = blocks
        self.status_var.set("Learning noise profile for 3s...")

    def _clear_noise(self):
        global noise_psd
        with noise_lock:
            noise_psd = None
        self.status_var.set("Noise profile cleared.")


if __name__ == "__main__":
    App().mainloop()
