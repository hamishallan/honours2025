import subprocess
import logging
import time
import socket
from AoDAQClient import AoDAQClient

AODAQ_EXECUTABLE = "./AoDAQ-v1.4.2"
AODAQ_HOST = "127.0.0.1"
AODAQ_PORT = 1242
CHECK_INTERVAL = 2.0
MAX_STARTUP_TIME = 60


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
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=5) as sock:
                idn_response = send_cmd(sock, "*IDN?")
                if "ARCspectro" not in idn_response:
                    logging.info("AoDAQ not ready (no IDN), retrying...")
                    time.sleep(CHECK_INTERVAL)
                    continue
                status_response = send_cmd(sock, "STAT:INIT?")
                if "0" in status_response:
                    logging.info("AoDAQ initialisation complete.")
                    return True
                else:
                    logging.info("AoDAQ still initialising...")
        except Exception as e:
            logging.debug(f"AoDAQ not reachable yet: {e}")
        time.sleep(CHECK_INTERVAL)
    logging.error("Timeout waiting for AoDAQ initialisation.")
    return False


# ---------------- Real Sensor ----------------
class RealSensor:
    def __init__(self, sensor_id):
        self.sensor_id = sensor_id
        self.process = None
        self.client = None

    def initialise(self):
        if self.process:
            logging.info(f"[{self.sensor_id}] Already initialised.")
            return
        logging.info(f"[{self.sensor_id}] Starting AoDAQ server...")
        logfile = open("aodaq.log", "w")
        self.process = subprocess.Popen(
            [AODAQ_EXECUTABLE, "-v"],
            stdout=logfile,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        if not wait_for_aodaq(AODAQ_HOST, AODAQ_PORT):
            logging.error(f"[{self.sensor_id}] AoDAQ failed to initialise.")
            self.process.terminate()
            self.process = None
            return

        logging.info(f"[{self.sensor_id}] Creating AoDAQ client...")
        self.client = AoDAQClient()
        logging.info(f"[{self.sensor_id}] Connecting AoDAQ client...")
        self.client.connect()
        logging.info(f"[{self.sensor_id}] Ready for sampling.")

        

    def sample(self):
        logging.info(f"[{self.sensor_id}] Entering sample()")
        if not self.client:
            logging.warning(f"[{self.sensor_id}] Must initialise first.")
            return
        logging.info(f"[{self.sensor_id}] Taking one sample...")
        self.client.send_cmd("SPEC:GET")
        spectrum = self.client.receive_spectrum()

        if spectrum:
            self.client.save_spectrum(spectrum)
            logging.info(f"[{self.sensor_id}] Sample saved with {len(spectrum)} points.")
        else:
            logging.warning(f"[{self.sensor_id}] No spectrum received.")


    def shutdown(self):
        if self.client:
            self.client.close()
            self.client = None
        if self.process:
            self.process.terminate()
            self.process = None
        logging.info(f"[{self.sensor_id}] Shutdown complete.")


# ---------------- Master ----------------
class MasterProcess:
    def __init__(self):
        self.sensors = {}
        self.default_sensor = "sensor1"

    def get_sensor(self, sensor_id=None):
        sid = sensor_id if sensor_id else self.default_sensor
        if sid not in self.sensors:
            logging.info(f"Creating new RealSensor for {sid}")
            self.sensors[sid] = RealSensor(sid)
        return self.sensors[sid]

    def handle_command(self, cmd):
        parts = cmd.strip().split()
        logging.info(f"Handling command: {parts}")  # <-- add this
        if not parts:
            return

        action = parts[0]
        sensor_id = parts[1] if len(parts) > 1 else None
        sensor = self.get_sensor(sensor_id)

        if action == "init":
            sensor.initialise()
        elif action == "sample":
            print("Calling sensor.sample() on", sensor)
            try:
                sensor.sample()
            except Exception as e:
                logging.error(f"Sample crashed: {e}", exc_info=True)
        elif action == "shutdown":
            sensor.shutdown()
        else:
            print(f"Unknown command: {action}")



def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    master = MasterProcess()
    print("Commands: init [id], sample [id], shutdown [id], quit")

    import sys

    while True:
        sys.stdout.write("READY FOR INPUT\n> ")
        sys.stdout.flush()
        cmd = sys.stdin.readline().strip()
        if not cmd:
            continue
        logging.debug(f"DEBUG raw cmd: {repr(cmd)}")
        if cmd == "quit":
            for sensor in master.sensors.values():
                sensor.shutdown()
            break
        master.handle_command(cmd)


if __name__ == "__main__":
    main()
