import serial
import re
import time
import math

class Encoder:
    """
    Reads and parses encoder data streamed from an Arduino over serial.

    Example input line:
        Depth: Encoder 0: Count 1089, Vel: 3600.00

    For a 1024 PPR encoder with a 67 mm diameter wheel:
        - Count → depth in mm
        - Velocity (counts/s) → speed in mm/s
    """

    PPR = 1024
    COUNTS_PER_REV = PPR * 4              # 4096 counts per revolution
    WHEEL_DIAMETER_MM = 67.0
    WHEEL_CIRCUM_MM = math.pi * WHEEL_DIAMETER_MM
    MM_PER_COUNT = WHEEL_CIRCUM_MM / COUNTS_PER_REV  # ≈ 0.0514 mm/count

    def __init__(self, port="/dev/ttyACM0", baudrate=115200, timeout=0.1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.last_data = {
            "enc0": {"count": None, "vel": None, "depth_mm": None, "speed_mms": None},
            "enc1": {"count": None, "vel": None, "depth_mm": None, "speed_mms": None}
        }
        self.pattern = re.compile(
            r"Encoder\s*(\d+)\s*:\s*Count\s*(-?\d+)\s*,\s*Vel\s*:\s*([-\d.]+)"
        )

    # --- Connection handling ---
    def connect(self):
        """Open the serial connection."""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # allow Arduino reset
            print(f"Connected to Arduino on {self.port}")
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            raise

    def disconnect(self):
        """Close the serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial connection closed.")

    # --- Reading and parsing ---
    def read_line(self):
        """Read one raw line from serial."""
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Serial port not open.")
        return self.ser.readline().decode(errors="ignore").strip()

    def parse_line(self, line):
        """Parse a single line and compute physical values."""
        match = self.pattern.search(line)
        if match:
            enc_id = int(match.group(1))
            count = int(match.group(2))
            vel_counts = float(match.group(3))
            key = f"enc{enc_id}"

            # Convert to physical values
            depth_mm = count * self.MM_PER_COUNT
            speed_mms = vel_counts * self.MM_PER_COUNT

            self.last_data[key] = {
                "count": count,
                "vel": vel_counts,
                "depth_mm": depth_mm,
                "speed_mms": speed_mms
            }
            
            return {
                "id": enc_id,
                "count": count,
                "vel": vel_counts,
                "depth_mm": depth_mm,
                "speed_mms": speed_mms
            }
            
        return {
            "id": -9999,
            "count": -9999,
            "vel": -9999,
            "depth_mm": -9999,
            "speed_mms": -9999
        }

    def read_data(self):
        """Read and parse the next valid encoder line."""
        line = self.read_line()
        if not line:
            return None
        return self.parse_line(line)

    def get_latest(self):
        """Return the most recent parsed data for both encoders."""
        return self.last_data


if __name__ == "__main__":
    encoder = Encoder("/dev/ttyACM0", 115200)
    encoder.connect()

    try:
        while True:
            data = encoder.read_data()
            if data:
                print("Encoder {id}: Depth={depth_mm:.2f} mm, Speed={speed_mms:.2f} mm/s".format(**data))
    except KeyboardInterrupt:
        encoder.disconnect()
