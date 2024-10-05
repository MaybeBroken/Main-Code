import argparse
import sys
from time import sleep
import numpy as np
import sounddevice as sd


start_idx = 0


def play(hz):
    def int_or_str(text):
        """Helper function for argument parsing."""
        try:
            return int(text)
        except ValueError:
            return text

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-l",
        "--list-devices",
        action="store_true",
        help="show list of audio devices and exit",
    )
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser],
    )
    parser.add_argument(
        "frequency",
        nargs="?",
        metavar="FREQUENCY",
        type=float,
        default=hz,
        help="frequency in Hz (default: %(default)s)",
    )
    parser.add_argument(
        "-d",
        "--device",
        type=int_or_str,
        help="output device (numeric ID or substring)",
    )
    parser.add_argument(
        "-a",
        "--amplitude",
        type=float,
        default=0.2,
        help="amplitude (default: %(default)s)",
    )
    args = parser.parse_args(remaining)

    try:
        samplerate = sd.query_devices(args.device, "output")["default_samplerate"]

        def callback(outdata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            global start_idx
            t = (start_idx + np.arange(frames)) / samplerate
            t = t.reshape(-1, 1)
            outdata[:] = args.amplitude * np.sin(2 * np.pi * args.frequency * t)
            start_idx += frames

        with sd.OutputStream(
            device=args.device, channels=1, callback=callback, samplerate=samplerate
        ):
            sleep(0.5)
    except KeyboardInterrupt:
        parser.exit("")
    except Exception as e:
        parser.exit(type(e).__name__ + ": " + str(e))


while True:
    for i in range(50, 1500, 1):
        play(i)
