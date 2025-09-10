import sqlite3
import requests
import logging

# ---------------- Config ----------------
DB_FILE = "spectra.db"
API_URL = "https://rekehtm1f0.execute-api.us-east-1.amazonaws.com/dev/upload-spectrum/"  # <-- replace with your actual API endpoint
DEVICE_ID = "stream_testing"

# ---------------- Main ----------------
def fetch_spectra():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Get all spectra
    cur.execute("SELECT id, timestamp, device_id, accuracy_m, altitude_m, latitude, longitude FROM core_spectrum")
    spectra = cur.fetchall()

    for spectrum in spectra:
        spectrum_id, timestamp, device_id, accuracy_m, altitude_m, lat, lon = spectrum

        # Get associated datapoints
        cur.execute("""
            SELECT wavelength, intensity
            FROM core_spectrumdatapoint
            WHERE spectrum_id = ?
            ORDER BY id ASC
        """, (spectrum_id,))
        datapoints = cur.fetchall()

        yield {
            "id": spectrum_id,
            "timestamp": timestamp,
            "device_id": device_id or DEVICE_ID,
            "accuracy_m": accuracy_m,
            "altitude_m": altitude_m,
            "latitude": lat,
            "longitude": lon,
            "wavelengths": [w for w, _ in datapoints],
            "intensities": [i for _, i in datapoints],
        }

    conn.close()


def upload_spectrum(spectrum):
    payload = {
        "device_id": spectrum["device_id"],
        "wavelengths": spectrum["wavelengths"],
        "intensities": spectrum["intensities"],
    }

    # Optional fields
    if spectrum["latitude"] is not None and spectrum["longitude"] is not None:
        payload["latitude"] = spectrum["latitude"]
        payload["longitude"] = spectrum["longitude"]
    if spectrum["altitude_m"] is not None:
        payload["altitude_m"] = spectrum["altitude_m"]
    if spectrum["accuracy_m"] is not None:
        payload["accuracy_m"] = spectrum["accuracy_m"]

    try:
        resp = requests.post(API_URL, json=payload, timeout=30)
        if resp.status_code == 201:
            logging.info("Uploaded spectrum {} ({} points)".format(
                spectrum["id"], len(spectrum["wavelengths"])
            ))
        else:
            logging.error("Failed to upload {}: {} - {}".format(
                spectrum["id"], resp.status_code, resp.text
            ))
    except Exception as e:
        logging.error("Error uploading {}: {}".format(spectrum["id"], e))


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    for spectrum in fetch_spectra():
        upload_spectrum(spectrum)


if __name__ == "__main__":
    main()
