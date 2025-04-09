import socket
import time
import logging
from datetime import datetime

# --- Configuration ---
AODAQ_HOST = "192.168.64.2"
AODAQ_PORT = 1242
RESPONSE_BUFFER_SIZE = 65536
READ_TIMEOUT = 10.0
SPECTRUM_TIMEOUT = 30.0
COMMAND_DELAY = 0.5

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def send_command(sock: socket.socket, command: str, timeout: float = READ_TIMEOUT) -> str:
    """
    Sends a command to the AoDAQ TCP server and reads the response.
    """
    try:
        logging.info(f"→ {command}")
        sock.sendall((command + "\n").encode())
        time.sleep(COMMAND_DELAY)

        sock.settimeout(timeout)
        response_parts = []
        while True:
            try:
                chunk = sock.recv(RESPONSE_BUFFER_SIZE)
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
        return response
    except Exception as e:
        logging.error(f"Communication error on command '{command}': {e}")
        return ""

def parse_spectrum_data(response: str):
    """
    Parses the spectrum response into (wavelength, intensity) pairs.
    """
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

def save_spectrum_csv(spectrum, filename=None):
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

def main():
    try:
        logging.info(f"Connecting to AoDAQ at {AODAQ_HOST}:{AODAQ_PORT}...")
        with socket.create_connection((AODAQ_HOST, AODAQ_PORT)) as sock:
            logging.info("✅ Connected.")

            idn = send_command(sock, "*IDN?")
            status = send_command(sock, "STAT:INIT?")
            if "0" not in status:
                logging.warning("Device is still initializing. Exiting.")
                return

            # Optional: Set transfer length and format (just for clarity, not used in ASCII mode)
            send_command(sock, "TRAN:LEN 1")
            send_command(sock, "TRAN:BIN 0")

            # Set maximum spectrum points if needed (can be adjusted)
            send_command(sock, "SPEC:MAX 1674")

            # Begin spectrum acquisition
            send_command(sock, "SPEC:AVG 2")
            raw_response = send_command(sock, "SPEC:GET?", timeout=SPECTRUM_TIMEOUT)

            # Parse and save
            spectrum = parse_spectrum_data(raw_response)
            if spectrum:
                save_spectrum_csv(spectrum)
            else:
                logging.warning("No valid spectrum data parsed.")
    except ConnectionRefusedError:
        logging.error("Connection refused. Ensure AoDAQ is running and reachable.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
