from src.stream_analyzer import Stream_Analyzer
import time


def run_FFT_analyzer():
    ear = Stream_Analyzer(
        device=None,  # Pyaudio (portaudio) device index, defaults to first mic input
        rate=None,  # Audio samplerate, None uses the default source settings
        FFT_window_size_ms=60,  # Window size used for the FFT transform
        updates_per_second=500,  # How often to read the audio stream for new data
        smoothing_length_ms=50,  # Apply some temporal smoothing to reduce noisy features
        n_frequency_bins=400,  # The FFT features are grouped in bins
        verbose=None,  # Print running statistics (latency, fps, ...)
    )

    fps = 60  # How often to update the FFT features + display
    last_update = time.time()
    fft_samples = 0
    while True:
        if (time.time() - last_update) > (1.0 / fps):
            last_update = time.time()
            raw_fftx, raw_fft, binned_fftx, binned_fft = ear.get_audio_features()
            fft_samples += 1


if __name__ == "__main__":
    run_FFT_analyzer()
