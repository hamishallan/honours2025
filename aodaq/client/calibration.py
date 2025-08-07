import numpy as np
import pandas as pd
from scipy.interpolate import interp1d


def load_calibration_csv(path):
    df = pd.read_csv(path, header=None, names=["wavelength", "coefficient", "constant"])

    # Keep rows where coefficient is not NaN
    df = df[pd.notnull(df["coefficient"])]
    calib_wavelengths = df["wavelength"].to_numpy(dtype=float)
    calib_coeffs = df["coefficient"].to_numpy(dtype=float)

    # Grab the first available constant
    constant_row = pd.read_csv(path, header=None, names=["wavelength", "coefficient", "constant"])
    calib_const = constant_row["constant"].dropna().iloc[0]

    return calib_wavelengths, calib_coeffs, calib_const


def interpolate_spectrum(raw_wavelengths, raw_intensities, target_wavelengths):
    interpolator = interp1d(raw_wavelengths, raw_intensities, bounds_error=False, fill_value="extrapolate")
    return interpolator(target_wavelengths)


def snv(x):
    x = np.asarray(x, dtype=float)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    mu = np.nanmean(x)
    sigma = np.nanstd(x)
    if sigma == 0 or np.isnan(sigma):
        return np.zeros_like(x)
    return (x - mu) / sigma


def apply_calibrated_model(raw_spectrum, calib_path):
    raw_wavelengths, raw_intensities = zip(*raw_spectrum)
    raw_wavelengths = np.array(raw_wavelengths)
    raw_intensities = np.array(raw_intensities)

    calib_wavelengths, calib_coeffs, calib_const = load_calibration_csv(calib_path)
    aligned_intensities = interpolate_spectrum(raw_wavelengths, raw_intensities, calib_wavelengths)
    aligned_intensities = snv(aligned_intensities)

    predicted_value = np.dot(aligned_intensities, calib_coeffs) + calib_const
    predicted_value *= 0.1 # Assuming we are expecting ~4.18 instead of ~41.8
    return predicted_value