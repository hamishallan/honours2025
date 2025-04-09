import re
import time
import socket
import logging
from datetime import datetime

# --- Configuration ---
RESPONSE_BUFFER_SIZE = 65536
INIT_TIMEOUT = 5.0
SPECTRUM_TIMEOUT = 60.0 * 5
COMMAND_DELAY = 0.5
RETRY_ATTEMPTS = 5
VALIDATE_RESP_OK = ["OK", "ARCspectro"]

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class AoDAQClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None


    def connect(self, timeout=10.0):
        logging.info(f"Connecting to AoDAQ at {self.host}:{self.port}...")
        self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
        logging.info("✅ Connected.")


    def close(self):
        if self.sock:
            self.sock.close()
            logging.info("Connection closed.")


    def send_command(self, command, timeout=INIT_TIMEOUT, delay=COMMAND_DELAY, expect_ok=False) -> str:
        for attempt in range(RETRY_ATTEMPTS):
            try:
                logging.info(f"→ {command}")
                self.sock.sendall((command + "\n").encode())
                time.sleep(delay)
                self.sock.settimeout(timeout)

                response_parts = []
                while True:
                    try:
                        chunk = self.sock.recv(RESPONSE_BUFFER_SIZE)
                        if not chunk:
                            break
                        response_parts.append(chunk)
                    except socket.timeout:
                        break

                response = b"".join(response_parts).decode("utf-8", errors="replace").strip()
                if len(response) > 200:
                    logging.info(f"← (received {len(response)} chars)")
                else:
                    logging.info(f"← {response}")

                if not expect_ok or any(ok in response for ok in VALIDATE_RESP_OK):
                    return response
                else:
                    logging.warning(f"Unexpected response, retrying... [{attempt+1}/{RETRY_ATTEMPTS}]")
                    time.sleep(1)

            except (socket.timeout, socket.error) as e:
                logging.warning(f"Attempt {attempt+1} failed: {e}")
                time.sleep(1)

        logging.error(f"Failed to send command after {RETRY_ATTEMPTS} attempts: {command}")
        return ""


    def parse_spectrum_data(self, response: str):
        lines = response.splitlines()
        spectrum = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    wavelength = float(parts[0])
                    intensity = float(parts[1])
                    spectrum.append((wavelength, intensity))
                except ValueError:
                    continue
        return spectrum


    def save_spectrum_csv(self, spectrum, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"spectrum_{timestamp}.csv"

        try:
            with open(filename, "w") as f:
                f.write("Wavelength,Intensity\n")
                for wl, inten in spectrum:
                    f.write(f"{wl},{inten}\n")
            logging.info(f"Spectrum saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving spectrum: {e}")
            
    
    def extract_value_after_ok(self, response: str, as_type=int):
        """
        Parses the second line after 'OK' in a multi-line AoDAQ response,
        cleans non-numeric characters, and casts to the given type.
        """
        lines = response.splitlines()
        for idx, line in enumerate(lines):
            if "OK" in line and idx + 2 < len(lines):
                val = lines[idx + 2].strip()
                val_clean = re.sub(r"[^\d.eE+-]", "", val)
                try:
                    return as_type(val_clean)
                except ValueError:
                    logging.warning(f"Failed to cast value: {val_clean}")
                    return None
        return None
                            
            
    def run_full_matlab_equivalent(self, gain_level="Low", apodization="NortonBeerStrong", num_averages=5, is_igm_avg=False):
        GAIN_MAP = {"Low": 0, "Medium": 1, "High": 2, "Extreme": 3}
        APO_MAP = {
            "Boxcar": 0, "NortonBeerWeak": 1, "NortonBeerMedium": 2,
            "NortonBeerStrong": 3, "Hamming": 4, "BlackmanHarris3": 5,
            "BlackmanHarris4": 6, "Triangular": 7, "Hann": 8,
            "Tukey": 9, "Cosine": 10, "HappGenzel": 11
        }

        try:
            self.send_command("*IDN?", expect_ok=True)
            status = self.send_command("STAT:INIT?", expect_ok=True)
            if "0" not in status:
                logging.warning("Device is still initializing. Exiting.")
                return

            self.send_command("TRAN:LEN 1", expect_ok=True)
            self.send_command("TRAN:BIN 0", expect_ok=True)
            self.send_command("TRAN:SABS 1", expect_ok=True)
            self.send_command("SPEC:WLG 1", expect_ok=True)  # wavelength mode

            # Set gain
            gain_val = GAIN_MAP.get(gain_level, 0)
            self.send_command(f"GAIN:SET {gain_val}", expect_ok=True)

            # Set apodization
            apo_val = APO_MAP.get(apodization, 3)
            self.send_command(f"SPEC:APO {apo_val}", expect_ok=True)

            # Set spectrum averaging
            self.send_command(f"SPEC:AVG {num_averages}", expect_ok=True)

            # Optional: Set interferogram averaging
            if is_igm_avg:
                self.send_command(f"IFGM:AVG {num_averages}", expect_ok=True)

            # Start acquisition
            self.send_command("SPEC:GET?", expect_ok=True)

            # Wait for completion
            while True:
                rem = self.send_command("MEAS:REM?", expect_ok=True)
                remaining = self.extract_value_after_ok(rem, int)

                if remaining is not None:
                    logging.info(f"Remaining measurements: {remaining}")
                    if remaining == 0:
                        break
                else:
                    logging.warning(f"Couldn't parse MEAS:REM? response: {rem}")
                    break

                time.sleep(1)

            # Check saturation
            sat = self.send_command("SPEC:SAT?", expect_ok=True)
            saturation = self.extract_value_after_ok(sat, float)

            if saturation is not None:
                if saturation > 0.9:
                    logging.warning("⚠️ Detector saturation detected.")

            # Retrieve spectrum
            raw_response = self.send_command("TRAN:SPEC?", timeout=SPECTRUM_TIMEOUT, expect_ok=True)
            spectrum = self.parse_spectrum_data(raw_response)

            if spectrum:
                self.save_spectrum_csv(spectrum)
            else:
                logging.warning("No valid spectrum data parsed.")

        finally:
            self.close()