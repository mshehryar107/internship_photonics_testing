#%%
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import AutoMinorLocator

#%%
# Load the CSV file
file_path = 'Z:/07_Photonics Lab/11_Python_Scripts/Oscilloscope Plots/Test Data'
title_plot_1 = "DUT_Bias_Current_Sampling_Rate_Temperature_Mod_On"
title_plot_2 = "DUT_Bias_Current_Sampling_Rate_Temperature_Mod_Off"
name_fig_1 = "DUT_Bias_Current_Sampling_Rate_Temperature_Mod_On"
name_fig_2 = "DUT_Bias_Current_Sampling_Rate_Temperature_Mod_Off"

#%%
os.chdir(file_path)

files_mod_on =  [f for f in os.listdir(file_path) if 'Mod_On' in f and f.endswith('.csv')]
files_mod_off =  [f for f in os.listdir(file_path) if 'Mod_Off' in f and f.endswith('.csv')]

if not files_mod_on or not files_mod_off:
    raise FileNotFoundError("No files matching 'Mod_On' or 'Mod_Off' criteria were found in the directory.")

#%% For plotting individual data files, put index (from files_mod_on and files_mod_off) 
filename_mod_on = files_mod_on[0]
filename_mod_off = files_mod_off[1]

#%%
# Read the file with Modulation On data
file_to_read_mod_on = os.path.join(file_path, filename_mod_on)  # Use full path for reading
with open(file_to_read_mod_on, 'r') as file:
    raw_data_mod_on = file.readlines()

# Identify the start of the data section
data_start_index_mod_on = None
for i, line in enumerate(raw_data_mod_on):
    if "TIME" in line and "CH" in line:  # Adjust based on file content
        data_start_index_mod_on = i
        break

if data_start_index_mod_on is None:
    raise ValueError("Could not find data header containing 'TIME' and 'CH'.")

# Read the file with Modulation Off data
file_to_read_mod_off = os.path.join(file_path, filename_mod_off)  # Use full path for reading
with open(file_to_read_mod_off, 'r') as file:
    raw_data_mod_off = file.readlines()

# Identify the start of the data section
data_start_index_mod_off = None
for i, line in enumerate(raw_data_mod_off):
    if "TIME" in line and "CH" in line:  # Adjust based on file content
        data_start_index_mod_off = i
        break

if data_start_index_mod_off is None:
    raise ValueError("Could not find data header containing 'TIME' and 'CH'.")

#%% Read Data 
data_mod_on = pd.read_csv(file_to_read_mod_on, skiprows=data_start_index_mod_on)

CH1_mod_on = data_mod_on['CH1'] * 1e3 #Voltage in mV
CH2_mod_on = data_mod_on['CH2'] * 1e3 #Voltage in mV
CH3_mod_on = data_mod_on['CH3'] #Voltage already in mV
TIME_mod_on = data_mod_on['TIME']

step_size_mod_on = abs(TIME_mod_on[0] - TIME_mod_on[1])
record_length_mod_on = len(TIME_mod_on)
TIME_mod_on = np.arange(0, record_length_mod_on) * step_size_mod_on * 1e6 #Time in us

data_mod_off = pd.read_csv(file_to_read_mod_off, skiprows=data_start_index_mod_off)

CH1_mod_off = data_mod_off['CH1'] * 1e3 #Voltage in mV
CH2_mod_off = data_mod_off['CH2'] * 1e3 #Voltage in mV
CH3_mod_off = data_mod_off['CH3'] #Voltage already in mV
TIME_mod_off = data_mod_off['TIME']

step_size_mod_off = abs(TIME_mod_off[0] - TIME_mod_off[1])
record_length_mod_off = len(TIME_mod_off)
TIME_mod_off = np.arange(0, record_length_mod_off) * step_size_mod_off * 1e6 #Time in us

#%% Plots for Modulation On

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(8, 10))  # Create subplots directly

# Plot
ax1.plot(TIME_mod_on, CH1_mod_on)
ax2.plot(TIME_mod_on, CH2_mod_on)
ax3.plot(TIME_mod_on, CH3_mod_on)

# Titles and labels
ax1.set_title(title_plot_1, fontsize=12)
ax2.set_title('Modulation signal profile at waveform generator', fontsize=12)
ax3.set_title('Gain Current (mA)', fontsize=12)

ax1.set_ylabel('PD Voltage [mV]', fontsize=12, labelpad=20)  # Add padding for y-axis title
ax2.set_ylabel('Modulation Signal [mV]', fontsize=12, labelpad=20)
ax3.set_ylabel('Gain Current [mA]', fontsize=12, labelpad=20)
ax3.set_xlabel('Time [µs]', fontsize=12, labelpad=15)  # Add padding for x-axis

# Adding minor grids
for ax in [ax1, ax2, ax3]:
    ax.grid(visible=True, which='both', linestyle='--', linewidth=0.5)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

# Adjust layout to avoid overlapping
plt.tight_layout()

# Uncomment to save the figure
plt.savefig(name_fig_1+'.png', dpi=300)

plt.show()

#%% Plots for Modulation Off

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(8, 10))  # Create subplots directly

# Plot
ax1.plot(TIME_mod_off, CH1_mod_off)
ax2.plot(TIME_mod_off, CH2_mod_off)
ax3.plot(TIME_mod_off, CH3_mod_off)

# Titles and labels
ax1.set_title(title_plot_2, fontsize=12)
ax2.set_title('Modulation signal profile at waveform generator', fontsize=12)
ax3.set_title('Gain Current (mA)', fontsize=12)

ax1.set_ylabel('PD Voltage [mV]', fontsize=12, labelpad=20)  # Add padding for y-axis title
ax2.set_ylabel('Modulation Signal [mV]', fontsize=12, labelpad=20)
ax3.set_ylabel('Gain Current [mA]', fontsize=12, labelpad=20)
ax3.set_xlabel('Time [µs]', fontsize=12, labelpad=15)  # Add padding for x-axis

# Adding minor grids
for ax in [ax1, ax2, ax3]:
    ax.grid(visible=True, which='both', linestyle='--', linewidth=0.5)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

# Adjust layout to avoid overlapping
plt.tight_layout()

# Uncomment to save the figure
plt.savefig(name_fig_2+'.png', dpi=300)

plt.show()

# %%
