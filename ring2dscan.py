#Laser test 'Openlight'
# -*- coding: utf-8 -*-

#%%
#Importing all required modules
##If something is missing and needs to be added please add here##
import matplotlib.pyplot as plt
import pyvisa as visa
import numpy as np
import time
import math
import serial
from pyvisa import ResourceManager
#from TLPM import TLPM
import h5py
from datetime import datetime
from ctypes import c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int16,c_double
import scipy.io
#from drivers import Laser

import os
import sys
from scipy import signal
from koheron import connect, command

#from plyer import notification
import requests


#%%
#To plot the recorded data
hfr = h5py.File('OL_TRL_019A_33C_80mA_Ring_Sweep_02_12_2024.h5','r')

Current_0 = np.array(hfr.get('Iring0'))
Current_1 = np.array(hfr.get('Iring1'))
Voltage_0 = np.array(hfr.get('ring_0_voltage'))
Voltage_1 = np.array(hfr.get('ring_1_voltage'))
R_Power_0 = np.array(hfr.get('Pring0'))
R_Power_1 = np.array(hfr.get('Pring1'))
power_onchip = np.array(hfr.get('MPDPower'))
power_out = np.array(hfr.get('PowThf'))
wavelength = np.array(hfr.get('Wavelength'))
smsr_1 = np.array(hfr.get('Sidemode'))
lw1 = np.array(hfr.get('Linewidth'))
hfr.close()

#To make the countour plot
#%%
#plt.contourf(R_Power_0, R_Power_1, wavelength, 20, cmap='RdGy')
plt.figure()
plt.contourf(R_Power_0, R_Power_1, wavelength,100)
plt.colorbar()
plt.xlabel('Ring-0 Heater Power (mW)')
plt.ylabel('Ring-1 Heater Power (mW)')
plt.title('OL TRL 020A 35C 80mA Operating Wavelength (nm)')
plt.savefig('OL_TRL_020A_35C_80mA_Operating_Wavelength.png',dpi=300)
#plt.show()

#%%
#plt.contourf(R_Power_0, R_Power_1, power_onchip, 20, cmap='RdGy')
plt.figure()
plt.contourf(R_Power_0, R_Power_1, power_out,100)
plt.colorbar()
plt.xlabel('Ring-0 Heater Power (mW)')
plt.ylabel('Ring-1 Heater Power (mW)')
plt.title('OL TRL 020A 35C 80mA Outout Opitcal Power (mW)')
plt.savefig('OL_TRL_020A_35C_80mA_Optical_Power.png',dpi=300)
#plt.show()

#%%
#plt.contourf(R_Power_0, R_Power_1, smsr_1, 20, cmap='RdGy')
plt.figure()
plt.contourf(R_Power_0, R_Power_1, smsr_1, 100)
plt.colorbar()
plt.xlabel('Ring-0 Heater Power (mW)')
plt.ylabel('Ring-1 Heater Power (mW)')
plt.title('OL TRL 35C 020A 80mA Side mode supression ratio (dB)')
plt.savefig('OL_TRL_020A_35C_80mA_SMSR.png',dpi=300)
#plt.show()

#plt.contourf(R_Power_0, R_Power_1, smsr_1, 20, cmap='RdGy')
plt.figure()
plt.contourf(R_Power_0, R_Power_1, lw1, 100)
plt.colorbar()
plt.xlabel('Ring-0 Heater Power (mW)')
plt.ylabel('Ring-1 Heater Power (mW)')
plt.title('OL TRL 25C 50mA Linewidth (kHz)')
#plt.savefig('OL_TRL_25C_50mA_Linewidth.png',dpi=300)
#plt.show()

#%%
# Plot the 2D contour
plt.figure()
plt.contourf(R_Power_0, R_Power_1, wavelength, 100)
plt.colorbar()
plt.xlabel('Ring-0 Heater Power (mW)')
plt.ylabel('Ring-1 Heater Power (mW)')
plt.title('OL TRL 020A 35C 80mA Operating Wavelength (nm)')
plt.savefig('OL_TRL_020A_35C_80mA_Operating_Wavelength.png', dpi=300)
#plt.show()

# Extract 1D data
# Along x-axis (y = constant)
y_idx = len(R_Power_1) // 2  # Middle index for y-axis
wavelength_x = wavelength[0, :]  # Fixed y, vary x

# Along y-axis (x = constant)
x_idx = len(R_Power_0) // 2  # Middle index for x-axis
wavelength_y = wavelength[:, 0]  # Fixed x, vary y

# Along diagonal (x = y)
diagonal_idx = np.arange(min(len(R_Power_0), len(R_Power_1)))  # Diagonal indices
wavelength_diag = wavelength[diagonal_idx, diagonal_idx]  # Values along the diagonal

# Plot the 1D slices
plt.figure(figsize=(12, 4))

# Plot along x-axis
plt.subplot(1, 3, 1)
plt.plot(R_Power_0, wavelength_x)
plt.xlabel('Ring-0 Heater Power (mW)')
plt.ylabel('Wavelength (nm)')
plt.title('Slice Along X-Axis')

# Plot along y-axis
plt.subplot(1, 3, 2)
plt.plot(R_Power_1, wavelength_y)
plt.xlabel('Ring-1 Heater Power (mW)')
plt.ylabel('Wavelength (nm)')
plt.title('Slice Along Y-Axis')

# Plot along diagonal
plt.subplot(1, 3, 3)
plt.plot(R_Power_0[diagonal_idx], wavelength_diag)
plt.xlabel('Ring-0 Heater Power = Ring-1 Heater Power (mW)')
plt.ylabel('Wavelength (nm)')
plt.title('Slice Along Diagonal')

plt.tight_layout()
#plt.show()
# %%
# Filter wavelengths between 1549 and 1551
lower_bound = 1549
upper_bound = 1551
mask = (wavelength >= lower_bound) & (wavelength <= upper_bound)

# Find corresponding indexes
indices = np.argwhere(mask)  # Get indices where the condition is True

# Extract the coordinates and wavelengths
filtered_coordinates = [(R_Power_0[i[1]], R_Power_1[i[0]]) for i in indices]
filtered_wavelengths = wavelength[mask]

# Output results
print("Filtered Wavelengths:")
print(filtered_wavelengths)
print("\nCorresponding Grid Points (R_Power_0, R_Power_1):")
print(filtered_coordinates)
print(indices)
# %%
# Filter wavelengths between 1549 and 1551
lower_bound = 1508
upper_bound = 1512
mask = (wavelength >= lower_bound) & (wavelength <= upper_bound)

# Find corresponding indexes
indices = np.argwhere(mask)  # Get row-column indices where condition is True

# Extract corresponding values for R_Power_0, R_Power_1, and other parameters
filtered_results = []
for idx in indices:
    row, col = idx
    result = {
        'R_Power_0': R_Power_0[col],  # x-coordinate
        'R_Power_1': R_Power_1[row],  # y-coordinate
        'Wavelength': wavelength[row, col],
        'Output Power': power_out[row, col],
        'SMSR': smsr_1[row, col],
        'Linewidth': lw1[row, col],
        'Ring Current 0': Current_0[col],  # Current for Ring-0
        'Ring Current 1': Current_1[row]  # Current for Ring-1
    }
    filtered_results.append(result)

# Display filtered results
for res in filtered_results:
    print(res)
# %%
# Initialize variables to track the maximum power
max_power = -np.inf
max_result = None

# Loop over the indices and extract corresponding values
for idx in indices:
    row, col = idx  # Get row and column indices
    R_Power_0_value = R_Power_0[col]  # x-coordinate
    R_Power_1_value = R_Power_1[row]  # y-coordinate
    wavelength_value = wavelength[row, col]
    power_out_value = power_out[row, col]
    smsr_value = smsr_1[row, col]
    linewidth_value = lw1[row, col]
    ring_current_0_value = Current_0[col]
    ring_current_1_value = Current_1[row]

    # Update max_result if current power_out_value is greater
    if power_out_value > max_power:
        max_power = power_out_value
        max_result = {
            'R_Power_0': R_Power_0_value,
            'R_Power_1': R_Power_1_value,
            'Wavelength': wavelength_value,
            'Output Power': power_out_value,
            'SMSR': smsr_value,
            'Linewidth': linewidth_value,
            'Ring Current 0': ring_current_0_value,
            'Ring Current 1': ring_current_1_value
        }

# Print the result with the maximum power
if max_result:
    print("Result with Maximum Power:")
    print(max_result)
else:
    print("No wavelengths found in the specified range.")
# %%
# Limit linewidth values to 0.200
lw1_limited = np.clip(lw1, None, 0.200)
# Plot the contour plot with the limited linewidth
plt.figure()
plt.contourf(R_Power_0, R_Power_1, lw1_limited*1e3, 100, cmap='viridis')  # You can customize the colormap
plt.colorbar(label='Linewidth (kHz)')
plt.xlabel('Ring-0 Heater Power (mW)')
plt.ylabel('Ring-1 Heater Power (mW)')
plt.title('OL TRL 25C 50mA Linewidth (kHz)')
# Uncomment the following line to save the figure
# plt.savefig('OL_TRL_25C_50mA_Linewidth.png', dpi=300)
plt.show()
# %%
