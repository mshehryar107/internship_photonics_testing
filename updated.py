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

# Ensure 'Wavelength(A)' and 'Level(A)' exist in the data
if 'Wavelength(A)' not in df.columns or 'Level(A)' not in df.columns:
    print("The required columns 'Wavelength(A)' or 'Level(A)' are not found in the data.")
    exit()

# Extract Wavelength and Level(A) data
wavelength = df['Wavelength(A)']
level_a = df['Level(A)']

# Convert Level(A) data from watts to dBm
try:
    level_a_dbm = 10 * np.log10(level_a / 10)
except Exception as e:
    print(f"Error processing 'Level(A)' column: {e}")
    exit()

# Plotting
plt.figure()
plt.plot(wavelength, level_a_dbm)

plt.title('Optical Spectrum', fontsize=14)
plt.xlabel('Wavelength (nm)', fontsize=14)
plt.ylabel('Optical Power (dBm)', fontsize=14)
plt.grid(True)

# Set axis limits if data is available
if not df.empty:
    plt.xlim(wavelength.iloc[0], wavelength.iloc[-1])

plt.minorticks_on()

plt.ylim(-100, 0)

plt.grid(color='grey', which='major', linestyle='-', linewidth=0.4)
plt.grid(color='grey', which='minor', linestyle='-', linewidth=0.25)
#plt.legend(loc="best")

# Save the plot
plt.savefig(save_address)
print(f"Plot saved successfully at {save_address}")

plt.show()
