#!/usr/bin/env python3
import RPi.GPIO as GPIO
from hx711 import HX711
import math
import time


class LoadCell:
    def __init__(self, dout_pin=20, pd_sck_pin=21, diameter_mm=12):
        self.dout_pin = dout_pin
        self.pd_sck_pin = pd_sck_pin
        self.hx = HX711(dout_pin=self.dout_pin, pd_sck_pin=self.pd_sck_pin)
        self.g = 9.81
        self.r = (diameter_mm / 1000) / 2       # convert mm → m and get radius
        self.A = math.pi * self.r**2             # cross-sectional area in m²
        self.ratio = -23554.02

    def calibrate(self, known_weight_kg):
        """Zero the scale, take a reading, and compute calibration factor."""
        print("Zeroing... remove any weight from the load cell.")
        self.hx.zero()
        input("Apply known weight and press Enter when ready...")
        reading = self.hx.get_data_mean()
        self.ratio = reading / known_weight_kg
        print("Calibration factor: {:.2f}".format(self.ratio))
        return self.ratio

    def set_calibration(self, ratio):
        """Manually set the calibration ratio (skip calibration step)."""
        self.ratio = ratio
        self.hx.set_scale_ratio(ratio)

    def stream(self):
        """Continuously read and display weight and pressure."""
        if self.ratio is None:
            raise ValueError("Calibration ratio not set. Run calibrate() first or use set_calibration().")

        self.hx.set_scale_ratio(self.ratio)
        print("Starting live readings... Press Ctrl+C to stop.\n")
        while True:
            weight = self.hx.get_weight_mean(1) # change to average more readings if necessary
            force = weight * self.g
            pressure = force / self.A
            print("Weight: {:.3f} kg | Pressure: {:.3f} Pa".format(weight, pressure))


# if __name__ == "__main__":
#     try:
#         GPIO.setmode(GPIO.BCM)
#         loadcell = LoadCell(dout_pin=20, pd_sck_pin=21)

#         mode = input("Enter 'c' to calibrate or 'r' to read: ").strip().lower()
#         if mode == "c":
#             known_weight = float(input("Enter known weight (kg): "))
#             ratio = loadcell.calibrate(known_weight)
#             print("Save this calibration factor for future runs:", ratio)
#         elif mode == "r":
#             # ratio = float(input("Enter saved calibration factor: "))
#             ratio = loadcell.ratio
#             loadcell.set_calibration(ratio)
#             loadcell.stream()
#         else:
#             print("Invalid selection.")

#     finally:
#         GPIO.cleanup()
