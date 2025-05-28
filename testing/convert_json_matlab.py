import pandas as pd
import json

# Load the CSV file
csv_file = '12-13-2022 13-31-02.csv'
df = pd.read_csv(csv_file, header=None, names=['wavelength', 'intensity'])

# Build the dictionary
data = {
    'wavelengths': df['wavelength'].tolist(),
    'intensities': df['intensity'].tolist(),
    'device_id': 'previous-project-10cm'  # Update if needed
}

# Save to JSON
output_file = 'matlab_payload.json'
with open(output_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f'Data written to {output_file}')
