import os
import logging
from Spectrometer import Spectrometer   # <-- assuming you put the class in spectrometer.py

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # folder where automate_aodaq.py is
AODAQ_EXECUTABLE = os.path.join(SCRIPT_DIR, "AoDAQ-v1.4.2") 
AODAQ_HOST = "127.0.0.1"
AODAQ_PORT = 1242
DEVICE_ID = "dev testing"

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    spectrometer = Spectrometer(
        executable=AODAQ_EXECUTABLE,
        host=AODAQ_HOST,
        port=AODAQ_PORT,
        device_id=DEVICE_ID
    )

    print("Commands: init, sample, upload [N], quit")

    try:
        while True:
            cmd_line = input("> ").strip().split()
            if not cmd_line:
                continue

            cmd, *args = cmd_line

            if cmd == "init":
                spectrometer.initialise()

            elif cmd == "sample":
                result = spectrometer.sample()
                if result:
                    spectrum_id, soc = result
                    print("Sampled spectrum_id={} | SOC={:.3f}".format(spectrum_id, soc))

            elif cmd == "upload":
                limit = int(args[0]) if args else None
                spectrometer.upload(limit=limit)

            elif cmd == "quit":
                break

            else:
                print("Unknown command. Available: init, sample, upload [N], quit")

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        spectrometer.shutdown()


if __name__ == "__main__":
    main()
