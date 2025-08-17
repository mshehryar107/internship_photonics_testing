#%%
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat

#%%
# Set global figure properties
plt.rcParams['figure.figsize'] = [10, 8]
plt.rcParams['figure.dpi'] = 100
plt.rcParams['axes.grid'] = True
plt.rcParams['axes.titlesize'] = 20
plt.rcParams['axes.labelsize'] = 18
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['lines.markersize'] = 8
plt.rcParams['legend.fontsize'] = 18
plt.rcParams['figure.facecolor'] = 'white'

#%%
# Naming and Path
file_path = 'Z:/07_Photonics Lab/11_Python_Scripts/Oscilloscope Plots/Test Data'
title_plot_1 = "DUT_Bias_Current_Sampling_Rate_Temperature_Mod_On" #For example:'TS7018 SOA Current Modulation Response (50 kHz), T = 60°C.'
title_plot_2 = "DUT_Bias_Current_Sampling_Rate_Temperature_Mod_Off"
name_fig_1 = "DUT_Bias_Current_Sampling_Rate_Temperature_Mod_On"
name_fig_2 = "DUT_Bias_Current_Sampling_Rate_Temperature_Mod_Off"

#%%
os.chdir(file_path)

# Get list of all files matching the pattern '*ch1*.mat', '*ch2*.mat', '*ch3*.mat'
list_names_ch1 = [f for f in os.listdir() if 'ch1' in f and f.endswith('.mat')]
list_names_ch2 = [f for f in os.listdir() if 'ch2' in f and f.endswith('.mat')]
list_names_ch3 = [f for f in os.listdir() if 'ch3' in f and f.endswith('.mat')]

#%%
# For plotting individual data files, put index (from list_names_ch..)

filename_ch1 = list_names_ch1[1]
filename_ch2 = list_names_ch2[1]
filename_ch3 = list_names_ch3[1]

# Import data from .mat files
data_ch1 = loadmat(filename_ch1)
data_ch2 = loadmat(filename_ch2)
data_ch3 = loadmat(filename_ch3)

# Extract relevant data
sample_interval = data_ch1['sampleInterval'][0][0]
Voltage_ch1 = np.ravel(data_ch1['data'])  # Flatten to 1D array
Voltage_ch2 = np.ravel(data_ch2['data'])
Voltage_ch3 = np.ravel(data_ch3['data'])

# Generate Time array based on the length of Voltage_ch1
record_length = len(Voltage_ch1)
Time = np.arange(0, record_length) * sample_interval

# Test parameter values
id = filename_ch1[:6]
T = 60

# Extract numeric part from the current value in the filename
I_str = re.findall(r'\d+', filename_ch1[21:24])
I = int(I_str[0]) if I_str else 0  # Default to 0 if no numeric part is found

# Extract modulation rate
modRate_str = re.findall(r'\d+', filename_ch1[14:17])
modRate = int(modRate_str[0]) if modRate_str else 0  # Default to 0 if no numeric part is found
modRateFreq = filename_ch1[17:20] if len(filename_ch1) >= 20 else ''  # Safely extract frequency substring

# Create a figure with 3 subplots (tiled layout)
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)

# Plot
ax1.plot(Time * 1e6, Voltage_ch1 * 1e3)
ax2.plot(Time * 1e6, Voltage_ch2 * 1e3)
ax3.plot(Time * 1e6, Voltage_ch3)
#ax1.set_xlim(0,100)

# Titles and labels
ax1.set_title(title_plot_1, fontsize=12)
ax2.set_title('Modulation signal profile at waveform generator', fontsize=12)
ax3.set_title('Modulation voltage at pads (mV)', fontsize=12)

ax1.set_ylabel('PD Voltage [mV]', fontsize=12)
ax2.set_ylabel('Modulation Signal [mV]', fontsize=12)
ax3.set_ylabel('Voltage @ pads [V]', fontsize=12)
ax3.set_xlabel('Time [µs]', fontsize=12)

# Save the figure
output_dir = 'Figures'
os.makedirs(output_dir, exist_ok=True)
fig.savefig(name_fig_1'.png', dpi=300)
#plt.close(fig)  # Close the figure to free memory
# %%