                                                                                        
import subprocess
import os
import time
import socket
import logging
from AoDAQClient import AoDAQClient


# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # folder where automate_aodaq.py is
AODAQ_EXECUTABLE = os.path.join(SCRIPT_DIR, "AoDAQ-v1.4.2") 
AODAQ_HOST = "127.0.0.1"
AODAQ_PORT = 1242
CHECK_INTERVAL = 2.0  # seconds
MAX_STARTUP_TIME = 30  # seconds

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


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


def main():
    logging.info(f"Starting AoDAQ server: {AODAQ_EXECUTABLE}")
    aodaq_process = subprocess.Popen(
        [AODAQ_EXECUTABLE, "-v"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Stream AoDAQ output live
    def stream_process_output(process):
        for line in process.stdout:
            logging.info(f"[AoDAQ] {line.strip()}")

    import threading
    threading.Thread(target=stream_process_output, args=(aodaq_process,), daemon=True).start()

    try:
        # Step 2: Wait until AoDAQ is ready
        if not wait_for_aodaq(AODAQ_HOST, AODAQ_PORT):
            logging.error("AoDAQ did not become ready in time. Exiting.")
            aodaq_process.terminate()
            return
        
        # Step 3: Run the AoDAQ Client
        logging.info("Starting AoDAQ Client acquisition...")
        client = AoDAQClient(AODAQ_HOST, AODAQ_PORT)
        client.connect()
        client.run_full_matlab_equivalent(
            gain_level="Low",
            apodization="NortonBeerStrong",
            num_averages=5,
            is_igm_avg=False
        )

    except Exception as e:
        logging.error(f"Unexpected error during automation: {e}")

    finally:
        # Step 4: Shutdown AoDAQ properly
        logging.info("Shutting down AoDAQ...")
        aodaq_process.terminate()
        try:
            aodaq_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            logging.warning("AoDAQ did not terminate cleanly, killing...")
            aodaq_process.kill()
        logging.info("Automation completed.")

if __name__ == "__main__":
    main()
