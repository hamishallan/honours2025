import os
import re
import json
import time
import socket
import logging
import requests
from datetime import datetime
from calibration import apply_calibrated_model

# --- Configuration ---
RESPONSE_BUFFER_SIZE = 65536
INIT_TIMEOUT = 5.0
SPECTRUM_TIMEOUT = 60.0 * 2 # minutes
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
            
            
    def upload_spectrum(self, spectrum, api_url, device_id="pi-01"):
        """
        Upload the given spectrum data to the Django API.
        """
        wavelengths, intensities = zip(*spectrum)  # unzip the list of tuples

        payload = {
            "wavelengths": list(wavelengths),
            "intensities": list(intensities),
            "device_id": device_id
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(api_url, data=json.dumps(payload), headers=headers)
            if response.status_code == 201:
                logging.info("✅ Spectrum uploaded successfully to API.")
                spectrum_id = response.json().get("spectrum_id")
                return spectrum_id
            else:
                logging.error(f"❌ Failed to upload spectrum. Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            logging.error(f"⚠️ Exception during spectrum upload: {e}")

        return None
    
    
    def upload_prediction(self, predicted_value, spectrum_id, device_id, api_url):
        """
        Uploads a predicted SOC value to the Django API.

        Args:
            predicted_value (float): The predicted SOC value.
            spectrum_id (str): UUID of the associated spectrum.
            device_id (str): Identifier of the device used to capture the spectrum.
            api_url (str): Full URL to the prediction upload endpoint.

        Returns:
            bool: True if upload successful, False otherwise.
        """
        payload = {
            "device_id": device_id,
            "predicted_value": predicted_value,
            "spectrum": spectrum_id
        }

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            if response.status_code == 201:
                logging.info("✅ Predicted value uploaded to API.")
                return True
            else:
                logging.error(f"❌ Prediction upload failed: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"⚠️ Error uploading predicted value: {e}")

        return False

    
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
                            
            
    def run_full_matlab_equivalent(self, gain_level="Low", apodization="NortonBeerStrong", num_averages=5, is_igm_avg=False, message=""):
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
                # Add device_id tag with settings
                device_id_tag = "simulated-pi_Gain-{0}_Apo-{1}_Avg-{2}_'{3}'".format(
                    gain_level, apodization, num_averages, message
                )
                
                # Compute and log predicted SOC using calibration model
                calib_path = os.path.join(os.path.dirname(__file__), "calibration_coeffs.csv")
                predicted_soc = apply_calibrated_model(spectrum, calib_path)
                
                spectrum_id = self.upload_spectrum(
                    spectrum,
                    api_url="https://rekehtm1f0.execute-api.us-east-1.amazonaws.com/dev/upload-spectrum/",
                    device_id=device_id_tag
                )
                
                self.upload_prediction(
                    predicted_value=predicted_soc,
                    spectrum_id=spectrum_id,
                    device_id=device_id_tag,
                    api_url="https://rekehtm1f0.execute-api.us-east-1.amazonaws.com/dev/upload-prediction/"
                )
                
            else:
                logging.warning("No valid spectrum data parsed.")

        finally:
            self.close()