import os
import psycopg2
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

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


def plot_spectrum(data, device_id):
    if not data:
        print("No data to plot.")
        return

    # Use seaborn styling
    sns.set_style('whitegrid')

    wavelengths, intensities = zip(*data)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(wavelengths, intensities, label='Raw Spectrum', linewidth=1.5)
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Intensity', fontsize=12)
    ax.set_title('Raw Spectrum Data', fontsize=14, weight='bold')
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.legend(fontsize=10)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    fig.tight_layout()
    spectrum_file = os.path.join(EXPORT_PATH, f"{device_id}_spectrum.png")
    fig.savefig(spectrum_file, dpi=300)
    plt.close(fig)

    # SNV corrected spectrum
    scaler = StandardScaler()
    snv_intensities = scaler.fit_transform(np.array(intensities).reshape(-1, 1)).flatten()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(wavelengths, snv_intensities, label='SNV Corrected Spectrum', color='orange', linewidth=1.5)
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('SNV Corrected Intensity', fontsize=12)
    ax.set_title('SNV Corrected Spectrum Data', fontsize=14, weight='bold')
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.legend(fontsize=10)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    fig.tight_layout()
    snv_file = os.path.join(EXPORT_PATH, f"{device_id}_snv_corrected_spectrum.png")
    fig.savefig(snv_file, dpi=300)
    plt.close(fig)

    print(f"Plots saved to:\n- {spectrum_file}\n- {snv_file}")


if __name__ == "__main__":
    device_id = "simulated-pi"  
    spectrum_id = "3778e431-b00d-404b-b06a-9244fff544db"
    # spectrum_id = None
    spectrum_data = fetch_spectrum_data(device_id, spectrum_id)
    plot_spectrum(spectrum_data, device_id)
