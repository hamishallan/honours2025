import threading
import time
import logging
from encoder import Encoder
from loadcell import LoadCell
import RPi.GPIO as GPIO

# --- Configuration ---
TARGET_WEIGHT_KG = 3.0        # stop condition
CONTACT_THRESHOLD_KG = 0.05   # first contact detection threshold
STABLE_DELAY_S = 0.1          # sample interval (seconds)
LOG_LEVEL = logging.INFO      # can change to DEBUG for more detail
LOG_FILE = None               # e.g. "probe_run.log" if you want to save to file


class ProbeController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.encoder = Encoder("/dev/ttyACM0", 115200)
        self.loadcell = LoadCell(dout_pin=20, pd_sck_pin=21)

        self.running = True
        self.depth_mm = 0.0
        self.weight_kg = 0.0
        self.surface_depth_mm = None
        self.max_reached = False
        self.recorded_depth = None

        self._setup_logger()
        self.logger.info("System initialised.")

    # --- Logging setup ---
    def _setup_logger(self):
        fmt = "%(asctime)s [%(levelname)s] %(message)s"
        datefmt = "%H:%M:%S"

        handlers = [logging.StreamHandler()]
        if LOG_FILE:
            handlers.append(logging.FileHandler(LOG_FILE, mode="w"))

        logging.basicConfig(level=LOG_LEVEL, format=fmt, datefmt=datefmt, handlers=handlers)
        self.logger = logging.getLogger("ProbeController")

    # --- Main start ---
    def start(self):
        self.logger.info("Starting probe test...")
        self.loadcell.set_calibration(self.loadcell.ratio)
        self.encoder.connect()

        enc_thread = threading.Thread(target=self._encoder_loop, daemon=True)
        lc_thread = threading.Thread(target=self._loadcell_loop, daemon=True)
        enc_thread.start()
        lc_thread.start()

        self._control_loop()

    # --- Sensor threads ---
    def _encoder_loop(self):
        while self.running:
            try:
                data = self.encoder.read_data()
                if data and data["id"] == 0:
                    self.depth_mm = data["depth_mm"]
            except Exception as e:
                self.logger.error(f"Encoder error: {e}")
            time.sleep(STABLE_DELAY_S)

    def _loadcell_loop(self):
        while self.running:
            try:
                self.weight_kg = self.loadcell.hx.get_weight_mean(1)
            except Exception as e:
                self.logger.error(f"Load cell error: {e}")
            time.sleep(STABLE_DELAY_S)

    # --- Control logic ---
    def _control_loop(self):
        try:
            while self.running:
                # Surface detection
                if self.surface_depth_mm is None and self.weight_kg > CONTACT_THRESHOLD_KG:
                    self.surface_depth_mm = self.depth_mm
                    self.logger.info(
                        "🟢 Surface detected at %.2f mm (%.3f kg)",
                        self.surface_depth_mm, self.weight_kg
                    )

                # Maximum weight
                if (self.surface_depth_mm is not None and
                    not self.max_reached and
                    self.weight_kg >= TARGET_WEIGHT_KG):
                    self.recorded_depth = self.depth_mm
                    self.max_reached = True
                    self.logger.info(
                        "💥 Max weight %.2f kg reached at depth %.2f mm",
                        self.weight_kg, self.depth_mm
                    )

                # Return to surface
                if (self.max_reached and self.surface_depth_mm is not None and
                    self.depth_mm < self.surface_depth_mm):
                    self.logger.info(
                        "⬆ Probe crossed surface again (%.2f mm < surface %.2f mm).",
                        self.depth_mm, self.surface_depth_mm
                    )
                    self.running = False

                # Debug stream
                self.logger.debug(
                    "Depth=%.2f mm | Weight=%.2f kg | Surface=%s | Max=%s",
                    self.depth_mm, self.weight_kg,
                    f"{self.surface_depth_mm:.2f}" if self.surface_depth_mm else "None",
                    self.max_reached
                )
                time.sleep(STABLE_DELAY_S)

        except KeyboardInterrupt:
            self.logger.warning("Interrupted by user.")
        finally:
            self.running = False
            self.encoder.disconnect()
            GPIO.cleanup()

            if self.recorded_depth:
                self.logger.info("✅ Final recorded penetration depth: %.2f mm", self.recorded_depth)
            else:
                self.logger.warning("No valid depth recorded (max weight not reached).")


if __name__ == "__main__":
    controller = ProbeController()
    controller.start()
