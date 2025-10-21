import threading
import time
import logging
import RPi.GPIO as GPIO
from encoder import Encoder
from loadcell import LoadCell
from database import DataLogger
from compaction import CompactionCalculator
import config


class ProbeController:
    def __init__(self):
        # --- Hardware setup ---
        GPIO.setmode(GPIO.BCM)
        self.encoder = Encoder("/dev/ttyACM0", 115200)
        self.loadcell = LoadCell(dout_pin=20, pd_sck_pin=21)

        # --- Runtime state ---
        self.depth_mm = 0.0
        self.weight_kg = 0.0
        self.max_weight = 0.0
        self.surface_depth_mm = None
        self.max_depth_mm = None
        self.running = True

        # --- Services ---
        self.db = DataLogger(config.DB_FILE)
        self.compaction = CompactionCalculator(self.loadcell)
        self._setup_logging()

        self.logger.info("System initialised.")

    # --- Logging ---
    def _setup_logging(self):
        fmt = "%(asctime)s [%(levelname)s] %(message)s"
        handlers = [logging.StreamHandler()]
        if config.LOG_FILE:
            handlers.append(logging.FileHandler(config.LOG_FILE, mode="w"))
        logging.basicConfig(level=config.LOG_LEVEL, format=fmt, datefmt="%H:%M:%S", handlers=handlers)
        self.logger = logging.getLogger("ProbeController")

    # --- Thread loops ---
    def _encoder_loop(self):
        """Continuously update encoder depth."""
        while self.running:
            try:
                data = self.encoder.read_data()
                if data and data["id"] == 0:
                    self.depth_mm = data["depth_mm"]
            except Exception as e:
                self.logger.error(f"Encoder error: {e}")
            time.sleep(config.STABLE_DELAY_S)

    def _loadcell_loop(self):
        """Continuously update weight and track max."""
        while self.running:
            try:
                w = self.loadcell.hx.get_weight_mean(1)
                self.weight_kg = w
                self.max_weight = max(self.max_weight, w)
            except Exception as e:
                self.logger.error(f"Load cell error: {e}")
            time.sleep(config.STABLE_DELAY_S)

    # --- Core logic ---
    def start(self):
        """Run probe test."""
        self.logger.info("Starting probe test...")
        self.loadcell.set_calibration(self.loadcell.ratio)
        self.encoder.connect()

        # Start sensor threads
        threading.Thread(target=self._encoder_loop, daemon=True).start()
        threading.Thread(target=self._loadcell_loop, daemon=True).start()

        try:
            self._control_loop()
        finally:
            self._shutdown()

    def _control_loop(self):
        """High-level probe control logic."""
        while self.running:
            # Detect surface
            if self.surface_depth_mm is None and self.weight_kg > config.CONTACT_THRESHOLD_KG:
                self.surface_depth_mm = self.depth_mm
                self.logger.info("Surface detected at %.2f mm (%.3f kg)",
                                 self.surface_depth_mm, self.weight_kg)

            # Detect max load
            if (self.surface_depth_mm is not None and
                self.max_depth_mm is None and
                self.weight_kg >= config.TARGET_WEIGHT_KG):
                self.max_depth_mm = self.depth_mm
                self.logger.info("Max load %.2f kg reached at depth %.2f mm",
                                 self.weight_kg, self.depth_mm)

            # Detect retraction
            if self.max_depth_mm and self.surface_depth_mm and self.depth_mm < self.surface_depth_mm:
                self.logger.info("Probe returned above surface (%.2f mm < %.2f mm).",
                                 self.depth_mm, self.surface_depth_mm)
                self.running = False

            time.sleep(config.STABLE_DELAY_S)

    def _shutdown(self):
        """Safely close hardware and save data."""
        self.running = False
        self.encoder.disconnect()
        GPIO.cleanup()

        compaction_pa = self.compaction.compute(self.max_weight)
        if self.max_depth_mm:
            self.db.log_run(self.max_depth_mm, self.max_weight, compaction_pa)
            self.logger.info("Saved run → depth: %.2f mm | weight: %.2f kg | compaction: %.2f Pa",
                             self.max_depth_mm, self.max_weight, compaction_pa)
        else:
            self.logger.warning("No valid depth recorded (max weight not reached).")

        self.db.close()


if __name__ == "__main__":
    controller = ProbeController()
    controller.start()
