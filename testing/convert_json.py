import csv
import json

input_csv_file = 'data.csv'
output_json_file = 'spectra_upload_payload.json'

spectrum_data_list = []

with open(input_csv_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    headers = reader.fieldnames

    # Identify where the numeric wavelength headers start
    wavelength_start_idx = headers.index("Wavelength") + 1

    # Extract the wavelength list from headers
    wavelengths = []
    for h in headers[wavelength_start_idx:]:
        try:
            h_clean = h.strip().split()[0]
            wavelengths.append(int(h_clean))
        except ValueError:
            print("Couldn’t parse header:", h)
            continue

    # Process each row
    for row in reader:
        intensities = []
        for h in headers[wavelength_start_idx:]:
            val = row[h].strip()

            # Handle "<" values
            if "<" in val:
                val = val.replace("<", "").strip()

            # Skip empty cells
            if val == "" or val.upper() == "NA":
                intensities.append(None)
                continue

            # Remove commas
            val = val.replace(",", "")

            try:
                intensities.append(float(val))
            except ValueError:
                print("Still can’t parse:", val)
                intensities.append(None)

        # Remove None values (if any)
        clean_wavelengths = [w for w, i in zip(wavelengths, intensities) if i is not None]
        clean_intensities = [i for i in intensities if i is not None]

        if clean_wavelengths and clean_intensities:
            spectrum_data = {
                "wavelengths": clean_wavelengths,
                "intensities": clean_intensities,
                "device_id": row.get("Device Name", "unknown")
            }
            spectrum_data_list.append(spectrum_data)

# Save as JSON
with open(output_json_file, 'w', encoding='utf-8') as f:
    json.dump(spectrum_data_list, f, ensure_ascii=False, indent=2)

print(f"✅ JSON file saved as '{output_json_file}' with {len(spectrum_data_list)} spectra.")
