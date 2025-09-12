import os
import socket
import time
import subprocess
import logging

from AoDAQClient import AoDAQClient
from calibration.calibration import apply_calibrated_model

# ---------------- Configuration ----------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AODAQ_EXECUTABLE = os.path.join(SCRIPT_DIR, "AoDAQ-v1.4.2")
AODAQ_HOST = "127.0.0.1"
AODAQ_PORT = 1242
CHECK_INTERVAL = 2.0  # seconds
MAX_STARTUP_TIME = 60  # seconds
API_URL_SPECTRA = "https://rekehtm1f0.execute-api.us-east-1.amazonaws.com/dev/upload-spectrum/"
API_URL_PREDICTIONS = "https://rekehtm1f0.execute-api.us-east-1.amazonaws.com/dev/upload-prediction/"
DEVICE_ID = "dev testing"


class Spectrometer:
    def __init__(self, executable, host="127.0.0.1", port=1242,
                 device_id="dev testing",
                 api_url_spectra=API_URL_SPECTRA,
                 api_url_predictions=API_URL_PREDICTIONS):
        self.executable = executable
        self.host = host
        self.port = port
        self.device_id = device_id
        self.api_url_spectra = api_url_spectra
        self.api_url_predictions = api_url_predictions

        self.process = None
        self.client = None
        
    # --------------------------------------------------------------------------------
    # ░█░█░▀█▀░▀█▀░█░░░▀█▀░▀█▀░▀█▀░█▀▀░█▀▀
    # ░█░█░░█░░░█░░█░░░░█░░░█░░░█░░█▀▀░▀▀█
    # ░▀▀▀░░▀░░▀▀▀░▀▀▀░▀▀▀░░▀░░▀▀▀░▀▀▀░▀▀▀
    # --------------------------------------------------------------------------------
    
    @staticmethod
    def _send_cmd(sock, cmd):
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


    def _wait_for_aodaq(self, timeout=MAX_STARTUP_TIME):
        """Wait until AoDAQ server responds to *IDN? and finishes initialization (STAT:INIT? == 0)."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                logging.info("Checking if AoDAQ is ready...")

                with socket.create_connection((self.host, self.port), timeout=5) as sock:
                    # Step 1: Check *IDN?
                    idn_response = self._send_cmd(sock, "*IDN?")
                    if "ARCspectro" not in idn_response:
                        logging.info("AoDAQ not fully ready yet (no IDN response), retrying...")
                        time.sleep(CHECK_INTERVAL)
                        continue

                    logging.info("AoDAQ responded to *IDN?")

                    # Step 2: Check STAT:INIT?
                    status_response = self._send_cmd(sock, "STAT:INIT?")
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

    # --------------------------------------------------------------------------------
    # ░█░░░▀█▀░█▀▀░█▀▀░█▀▀░█░█░█▀▀░█░░░█▀▀
    # ░█░░░░█░░█▀▀░█▀▀░█░░░░█░░█░░░█░░░█▀▀
    # ░▀▀▀░▀▀▀░▀░░░▀▀▀░▀▀▀░░▀░░▀▀▀░▀▀▀░▀▀▀
    # --------------------------------------------------------------------------------

    def initialise(self):
        logging.info("Starting AoDAQ server: %s", self.executable)
        self.process = subprocess.Popen(
            [self.executable, "-v"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        if not self._wait_for_aodaq():
            logging.error("AoDAQ did not become ready in time. Exiting.")
            self.process.terminate()
            self.process = None
            return False

        self.client = AoDAQClient()
        self.client.connect()
        logging.info("Spectrometer initialised and ready.")
        return True


    def sample(self):
        if not self.client:
            logging.warning("Client not initialised. Run 'initialise' first.")
            return None

        try:
            self.client.start_stream()
            spectrum = self.client.receive_spectrum()
            if spectrum:
                # Save spectrum with explicit ID
                spectrum_id = self.client.save_spectrum(spectrum, device_id=self.device_id)

                # Compute prediction
                calib_path = os.path.join(os.path.dirname(__file__), "calibration/calibration_coeffs.csv")
                predicted_soc = apply_calibrated_model(spectrum, calib_path)

                # Save prediction with same spectrum_id
                self.client.save_prediction(spectrum_id, predicted_soc, device_id=self.device_id)

                logging.info("Sample collected with %d points.", len(spectrum))
                return spectrum_id, predicted_soc
            self.client.stop_stream()
        except Exception as e:
            logging.error("Error while sampling: %s", e)
            return None


    def upload(self, limit=None):
        if not self.client:
            logging.warning("Client not initialised. Run 'initialise' first.")
            return

        logging.info("Uploading spectra (limit=%s)...", limit or "all")
        mapping = self.client.upload_spectra(self.api_url_spectra,
                                             default_device_id=self.device_id,
                                             limit=limit)

        logging.info("Uploading predictions (limit=%s)...", limit or "all")
        self.client.upload_predictions(self.api_url_predictions, mapping, limit=limit)


    def shutdown(self):
        if self.client:
            self.client.close()
            self.client = None
        if self.process:
            self.process.terminate()
            self.process = None
        logging.info("Shutdown complete.")
