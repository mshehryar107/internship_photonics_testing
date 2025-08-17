import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# Ask the user for the input file path and the output file path for saving the plot
data_address = input("Enter the full path for your data file (e.g., /path/to/WaveData.csv): ").strip()
if not os.path.isfile(data_address):
    print(f"Invalid file path: {data_address}. Please provide a valid file.")
    exit()

save_address = input("Enter the full path where you want to save the plot (e.g., /path/to/output_plot.png): ").strip()

# Read the data file dynamically to identify the header row containing 'Wavelength(A)'
with open(data_address, 'r') as file:
    lines = file.readlines()
skiprows = next((i for i, line in enumerate(lines) if 'Wavelength(A)' in line), 0)

# Load data using pandas
df = pd.read_csv(data_address, skiprows=skiprows)

# Display the columns for verification
print("Available columns in the data:")
print(df.columns)

# Automatically detect 'Level' columns
level_columns = [col for col in df.columns if col.startswith('Level(') and col.endswith(')')]
print(f"Detected level columns: {level_columns}")

# Plotting for detected traces
columns = []

for col_name in level_columns:
    try:
        # Conversion from watts to dBm (assuming valid data)
        columns.append(10 * np.log10(df[col_name] / 10))
    except Exception as e:
        print(f"Error processing column '{col_name}': {e}")
        columns.append(None)

# Plotting
plt.figure()
for i, col_data in enumerate(columns):
    if col_data is not None:
        plt.plot(df['Wavelength(A)'], col_data, label=f"Trace {i + 1}")

plt.title('OL_SOA_Back_Reflected_Optical_Spectrum', fontsize=14)
plt.xlabel('Wavelength(nm)', fontsize=14)
plt.ylabel('Optical Power(dBm)', fontsize=14)
plt.grid(True)

# Set axis limits if data is available
if not df.empty:
    plt.xlim(df['Wavelength(A)'].iloc[0], df['Wavelength(A)'].iloc[-1])
#plt.ylim(-100, -20)
plt.minorticks_on()
plt.grid(color='grey', which='major', linestyle='-', linewidth=0.4)
plt.grid(color='grey', which='minor', linestyle='-', linewidth=0.25)
plt.legend(loc="best")

# Save the plot
plt.savefig(save_address)
print(f"Plot saved successfully at {save_address}")

plt.show()