import psycopg2
import matplotlib.pyplot as plt
import numpy as np

# Update with your AWS PostgreSQL connection details
DB_HOST = "database-1.cv6ic62me1li.us-east-1.rds.amazonaws.com"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "honours2025"


def fetch_spectrum_data():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()
        spectrum_id = "23af87d8-0668-45c2-b4e8-cfc3868ad88f"  
        cursor.execute("SELECT wavelength, intensity FROM core_spectrumdatapoint WHERE spectrum_id = %s;", (spectrum_id,))
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []


from sklearn.preprocessing import StandardScaler


def plot_spectrum(data):
    if not data:
        print("No data to plot.")
        return

    wavelengths, intensities = zip(*data)
    plt.figure(figsize=(10, 6))
    plt.plot(wavelengths, intensities, label='Spectrum')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Intensity')
    plt.title('Spectrum Data Plot')
    plt.grid()
    plt.legend()
        # Plot SNV corrected spectrum
    scaler = StandardScaler()
    snv_intensities = scaler.fit_transform(np.array(intensities).reshape(-1, 1)).flatten()

    plt.figure(figsize=(10, 6))
    plt.plot(wavelengths, snv_intensities, label='SNV Corrected Spectrum', color='orange')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('SNV Corrected Intensity')
    plt.title('SNV Corrected Spectrum Data Plot')
    plt.grid()
    plt.legend()
    plt.show()


if __name__ == "__main__":
    spectrum_data = fetch_spectrum_data()
    plot_spectrum(spectrum_data)
