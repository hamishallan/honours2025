import psycopg2
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

DB_HOST = "database-1.cv6ic62me1li.us-east-1.rds.amazonaws.com"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "honours2025"
EXPORT_PATH = "/Users/hamish/Documents/UNI 2025/Honours/Plots"


def fetch_spectrum_data(device_id, spectrum_id=None):
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()

        if spectrum_id:
            cursor.execute("""
                SELECT d.wavelength, d.intensity
                FROM core_spectrumdatapoint d
                JOIN core_spectrum s ON d.spectrum_id = s.id
                WHERE s.device_id = %s AND s.id = %s;
            """, (device_id, spectrum_id))
        else:
            cursor.execute("""
                SELECT d.wavelength, d.intensity
                FROM core_spectrumdatapoint d
                JOIN core_spectrum s ON d.spectrum_id = s.id
                WHERE s.device_id = %s;
            """, (device_id,))

        data = cursor.fetchall()
        cursor.close()
        connection.close()
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []


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


def apply_calibrated_model(raw_spectrum, calib_path):
    raw_wavelengths, raw_intensities = zip(*raw_spectrum)
    raw_wavelengths = np.array(raw_wavelengths)
    raw_intensities = np.array(raw_intensities)

    calib_wavelengths, calib_coeffs, calib_const = load_calibration_csv(calib_path)
    aligned_intensities = interpolate_spectrum(raw_wavelengths, raw_intensities, calib_wavelengths)
    
    predicted_value = np.dot(aligned_intensities, calib_coeffs) + calib_const
    return predicted_value


if __name__ == "__main__":
    device_id = "simulated-pi"  
    spectrum_id = "3778e431-b00d-404b-b06a-9244fff544db"
    calib_path = "calibration_coeffs.csv"
    spectrum = fetch_spectrum_data(device_id, spectrum_id)
    predicted_soc = apply_calibrated_model(spectrum, calib_path)

    print("Predicted SOC:", predicted_soc)
