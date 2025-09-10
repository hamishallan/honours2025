import os
import socket
import time
import subprocess
import logging

from AoDAQClient import AoDAQClient

# ---------------- Configuration ----------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # folder where automate_aodaq.py is
AODAQ_EXECUTABLE = os.path.join(SCRIPT_DIR, "AoDAQ-v1.4.2") 
AODAQ_HOST = "127.0.0.1"
AODAQ_PORT = 1242
DB_FILE = "spectra.db"
CHECK_INTERVAL = 2.0  # seconds
MAX_STARTUP_TIME = 60  # seconds
HEADER_SIZE = 256


# ---------------- Utilities ----------------
def wait_for_aodaq(host, port, timeout=MAX_STARTUP_TIME):
    """Wait until AoDAQ server responds to *IDN? and finishes initialization (STAT:INIT? == 0)."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            logging.info("Checking if AoDAQ is ready...")

            with socket.create_connection((host, port), timeout=5) as sock:
                def send_cmd(cmd):
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

                # Step 1: Check *IDN?
                idn_response = send_cmd("*IDN?")
                if "ARCspectro" not in idn_response:
                    logging.info("AoDAQ not fully ready yet (no IDN response), retrying...")
                    time.sleep(CHECK_INTERVAL)
                    continue

                logging.info("AoDAQ responded to *IDN?")

                # Step 2: Check STAT:INIT?
                status_response = send_cmd("STAT:INIT?")
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








# ---------------- Main ----------------
def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    logging.info(f"Starting AoDAQ server: {AODAQ_EXECUTABLE}")
    aodaq_process = subprocess.Popen(
        [AODAQ_EXECUTABLE, "-v"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    try:
        if not wait_for_aodaq(AODAQ_HOST, AODAQ_PORT):
            logging.error("AoDAQ did not become ready in time. Exiting.")
            aodaq_process.terminate()
            return

        client = AoDAQClient()
        client.connect()

        try:
            client.start_stream()
            for _ in range(1):  # collect 5 spectra as example
                spectrum = client.receive_spectrum()
                if spectrum:
                    client.save_spectrum(spectrum)
            client.stop_stream()
        finally:
            client.close()

    except KeyboardInterrupt:
        logging.info("Interrupted by user.")
    finally:
        aodaq_process.terminate()
        logging.info("AoDAQ server stopped.")


if __name__ == "__main__":
    main()
