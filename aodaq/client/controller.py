import os
import socket
import time
import subprocess
import logging

from AoDAQClient import AoDAQClient
from calibration import apply_calibrated_model

# ---------------- Configuration ----------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # folder where automate_aodaq.py is
AODAQ_EXECUTABLE = os.path.join(SCRIPT_DIR, "AoDAQ-v1.4.2") 
AODAQ_HOST = "127.0.0.1"
AODAQ_PORT = 1242
DB_FILE = "spectra.db"
CHECK_INTERVAL = 2.0  # seconds
MAX_STARTUP_TIME = 60  # seconds
HEADER_SIZE = 256
API_URL_SPECTRA = "https://rekehtm1f0.execute-api.us-east-1.amazonaws.com/dev/upload-spectrum/"
API_URL_PREDICTIONS = "https://rekehtm1f0.execute-api.us-east-1.amazonaws.com/dev/upload-prediction/"
DEVICE_ID = "dev testing"


# ---------------- Utilities ----------------
def send_cmd(sock, cmd):
    sock.sendall((cmd + "\n").encode())
    time.sleep(0.5)
    sock.settimeout(5)
    response_parts = []
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response_parts.append(chunk)
        except socket.timeout:
            break
    return b''.join(response_parts).decode('utf-8', errors='replace').strip()


def wait_for_aodaq(host, port, timeout=MAX_STARTUP_TIME):
    """Wait until AoDAQ server responds to *IDN? and finishes initialization (STAT:INIT? == 0)."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            logging.info("Checking if AoDAQ is ready...")

            with socket.create_connection((host, port), timeout=5) as sock:
                # Step 1: Check *IDN?
                idn_response = send_cmd(sock, "*IDN?")
                if "ARCspectro" not in idn_response:
                    logging.info("AoDAQ not fully ready yet (no IDN response), retrying...")
                    time.sleep(CHECK_INTERVAL)
                    continue

                logging.info("AoDAQ responded to *IDN?")

                # Step 2: Check STAT:INIT?
                status_response = send_cmd(sock,"STAT:INIT?")
                if "0" in status_response:
                    logging.info("AoDAQ initialization complete.")
                    return True
                else:
                    logging.info("AoDAQ still initializing... waiting.")
        except Exception as e:
            logging.info(f"AoDAQ not reachable yet ({e}), retrying...")

        time.sleep(CHECK_INTERVAL)

    logging.error("Timeout waiting for AoDAQ to initialize.")
    return False






def initialise():
    global client, aodaq_process

    logging.info("Starting AoDAQ server: %s", AODAQ_EXECUTABLE)
    aodaq_process = subprocess.Popen(
        [AODAQ_EXECUTABLE, "-v"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    if not wait_for_aodaq(AODAQ_HOST, AODAQ_PORT):
        logging.error("AoDAQ did not become ready in time. Exiting.")
        aodaq_process.terminate()
        aodaq_process = None
        return

    client = AoDAQClient()
    client.connect()
    logging.info("Spectrometer initialised and ready.")


def sample():
    global client
    if not client:
        logging.warning("Client not initialised. Run 'init' first.")
        return

    try:
        client.start_stream()
        spectrum = client.receive_spectrum()
        if spectrum:
            # Save spectrum with explicit ID
            spectrum_id = client.save_spectrum(spectrum, device_id=DEVICE_ID)

            # Compute prediction
            calib_path = os.path.join(os.path.dirname(__file__), "calibration_coeffs.csv")
            predicted_soc = apply_calibrated_model(spectrum, calib_path)

            # Save prediction with same spectrum_id
            client.save_prediction(spectrum_id, predicted_soc, device_id=DEVICE_ID)

            logging.info("Sample collected with %d points.", len(spectrum))
        client.stop_stream()
    except Exception as e:
        logging.error("Error while sampling: %s", e)


def shutdown():
    global client, aodaq_process
    if client:
        # logging.info("Uploading latest spectra before shutdown...")
        # client.upload_spectra(API_URL, default_device_id="from shutdown", limit=3)
        client.close()
        client = None
    if aodaq_process:
        aodaq_process.terminate()
        aodaq_process = None
    logging.info("Shutdown complete.")


def upload_cmd(args):
    global client
    if not client:
        logging.warning("Client not initialised. Run 'init' first.")
        return

    limit = None
    if args:
        try:
            limit = int(args[0])
        except ValueError:
            logging.warning("Invalid number for upload limit: %s", args[0])
            return

    logging.info("Uploading spectra (limit=%s)...", limit or "all")
    mapping = client.upload_spectra(API_URL_SPECTRA, default_device_id="stream_testing", limit=limit)

    logging.info("Uploading predictions (limit=%s)...", limit or "all")
    client.upload_predictions(API_URL_PREDICTIONS, mapping, limit=limit)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print("Commands: init, sample, upload [N], quit")

    try:
        while True:
            cmd_line = input("> ").strip().split()
            if not cmd_line:
                continue
            cmd, *args = cmd_line

            if cmd == "init":
                initialise()
            elif cmd == "sample":
                sample()
            elif cmd == "upload":
                upload_cmd(args)
            elif cmd == "quit":
                break
            else:
                print("Unknown command. Available: init, sample, upload [N], quit")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        shutdown()



if __name__ == "__main__":
    main()
