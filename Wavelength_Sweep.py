#%%Libraries generally used
import matplotlib.pyplot as plt
import pyvisa as visa
import numpy as np
import time
import h5py
from toptica.lasersdk.dlcpro.v2_0_3 import DLCpro, NetworkConnection, DeviceNotFoundError
from toptica.lasersdk.utils.dlcpro import *
from pylablib.devices import OZOptics
#%% Resource Manager
rm = visa.ResourceManager()
print(rm.list_resources())

#%% Connect to power meters (Thorlabs)
# List all connected instruments
instruments = rm.list_resources()
print("Connected instruments:", instruments)

# Filter for Thorlabs PM100 and PM100D devices based on vendor ID (0x1313)
thorlabs_devices = [inst for inst in instruments if "USB0::0x1313" in inst]

if not thorlabs_devices:
    print("No Thorlabs PM100 or PM100D power meters detected.")
else:
    print("Thorlabs power meters detected:", thorlabs_devices)

# %%
instrument_1 = rm.open_resource(thorlabs_devices[2])
instrument_2 = rm.open_resource(thorlabs_devices[3])
instrument_3 = rm.open_resource(thorlabs_devices[4])

#%%
device_id = instrument_1.query("*IDN?")
print(f"Connected to {thorlabs_devices[2]}: {device_id}")

wavelength = 1550
# Configure the instrument (set power unit to dBm)
instrument_1.write("SENS:POW:UNIT DBM")
instrument_1.write(f"SENS:CORR:WAV {wavelength}")

# Measure power
power = float(instrument_1.query("MEAS:POW?"))
print(f"{thorlabs_devices[0]} - Power: {power} dBm\n")

time.sleep(1)

device_id = instrument_2.query("*IDN?")
print(f"Connected to {thorlabs_devices[1]}: {device_id}")

# Configure the instrument (set power unit to dBm)
instrument_2.write("SENS:POW:UNIT DBM")
instrument_2.write(f"SENS:CORR:WAV {wavelength}")

# Measure power
power = float(instrument_2.query("MEAS:POW?"))
print(f"{thorlabs_devices[1]} - Power: {power} dBm\n")

time.sleep(1)

device_id = instrument_3.query("*IDN?")
print(f"Connected to {thorlabs_devices[0]}: {device_id}")

# Configure the instrument (set power unit to dBm)
instrument_3.write("SENS:POW:UNIT DBM")
instrument_3.write(f"SENS:CORR:WAV {wavelength}")

# Measure power
power = float(instrument_3.query("MEAS:POW?"))
print(f"{thorlabs_devices[2]} - Power: {power} dBm")

#%%
# Toptica Laser init
print('>> Starting laser init')
CTL_IP = '192.168.2.59'  # TODO: Please check ip address on instrument
with DLCpro(NetworkConnection(CTL_IP)) as CTL:
    print('>> >> CTL system health:' + CTL.system_health_txt.get())
    print('>> >> CTL emission:' + str(CTL.emission.get()))
    print('>> >> CTL current:', str(CTL.laser1.dl.cc.current_set.get()))
    print('>> >> CTL wavelength act:', str(CTL.laser1.ctl.wavelength_act.get()))

    # This section for debugging only
    # wlen = 1540  # nm
    # print('>> >> CTL wavelength set:', str(wlen),' Returns', str(CTL.laser1.ctl.wavelength_set.set(wlen)))
    # time.sleep(10)
    # print('>> >> CTL wavelength act:', str(CTL.laser1.ctl.wavelength_act.get()))

    print('>> Laser init successful')

#%%
wlen_range = np.arange(1540,1570.25,0.25)
wavelength = wlen_range[0]
#Laser
with DLCpro(NetworkConnection(CTL_IP)) as CTL:
     CTL.laser1.ctl.wavelength_set.set(float(wavelength))
     time.sleep(5)
     print('>> >> CTL wavelength act:', str(CTL.laser1.ctl.wavelength_act.get()))
#powermeters
In_OP = np.zeros(len(wlen_range))
Out_OP_Q1 = np.zeros(len(wlen_range))
Out_OP_Q2 = np.zeros(len(wlen_range))

#%%
for i in range(np.size(wlen_range)):
    with DLCpro(NetworkConnection(CTL_IP)) as CTL:
     CTL.laser1.ctl.wavelength_set.set(float(wlen_range[i]))
     time.sleep(4)
     print('>> >> CTL wavelength act:', str(CTL.laser1.ctl.wavelength_act.get()))
    instrument_1.write(f"SENS:CORR:WAV {wlen_range[i]}")
    instrument_2.write(f"SENS:CORR:WAV {wlen_range[i]}")
    time.sleep(2)
    In_OPT = float(instrument_1.query('MEAS:POW?'))
    #print('Power meter (dBm)',In_OPT)
    In_OP[i] = 10 * np.log10(10**(In_OPT/10) * 99)
    print('Power meter (dBm) INPUT ',In_OP[i])
    Out_OP_Q1[i] = float(instrument_2.query('MEAS:POW?'))
    print('Power meter (dBm) OUTPUT ',Out_OP_Q1[i])
    Out_OP_Q2[i] = float(instrument_3.query('MEAS:POW?'))
    print('Power meter (dBm) OUTPUT ',Out_OP_Q2[i])
    


#%%
hf = h5py.File(f'WLT_AD09_200mA_Toptica_Wavelength_Sweep_Input_Port9&6_Q1&Q2_26_03.h5', 'w')
hf.create_dataset('Wlength', data=wlen_range)
hf.create_dataset('Pinput', data=In_OP)
hf.create_dataset('Poutput_Q1', data=Out_OP_Q1)
hf.create_dataset('Poutput_Q2', data=Out_OP_Q2)
hf.close()

#%%
hfr = h5py.File(f'WLT_AD09_200mA_Toptica_Wavelength_Sweep_Input_Port9&6_Q1&Q2_26_03.h5', 'r')
Wavelength = np.array(hfr.get('Wlength'))
Input_power = np.array(hfr.get('Pinput'))
Output_power_Q1 = np.array(hfr.get('Poutput_Q1'))
Output_power_Q2 = np.array(hfr.get('Poutput_Q2'))
hfr.close()

#GC_Loss = ((10 * np.log10(10**(Input_power/10) * 0.01)) - Output_power)/2
#%%
# ------------------ Plot 1: Output Optical Power and Gain ------------------
fig, ax1 = plt.subplots()

# Plot Output Optical Power vs Input Optical Power
ax1.plot(wlen_range, Output_power_I1, ":bo", label="Output Power Q1")
ax1.set_xlabel("Wavelength (nm)", fontsize=14)
ax1.set_ylabel("Output Optical Power (dBm) _ Q1", fontsize=14, color='b')
ax1.tick_params(axis='y', colors='b', size=4, width=1.5)
ax1.minorticks_on()  # Enable minor ticks

# Create twin axis for Gain
ax2 = ax1.twinx()
ax2.plot(wlen_range, Output_power_I2, ":ro", label="Output Power Q2")  
ax2.set_ylabel("Output Optical Power (dBm) _ Q2", fontsize=14, color='r')
ax2.tick_params(axis='y', colors='r', size=4, width=1.5)
ax2.minorticks_on()  # Enable minor ticks

# Title and Grid
plt.title(f'AD09 OH Design1.1 Input Port9&6 Q1&Q2')
ax1.grid(color='grey', which='major', linestyle='-', linewidth=0.5)
ax1.grid(color='grey', which='minor', linestyle='--', linewidth=0.35)

plt.savefig(f'WLT_AD09_200mA_Toptica_Wavelength_Sweep_Input_Port9&6_Q1&Q2_26_03.png', dpi=300)
# Show the plot
plt.show()









#%%
fig, ax1 = plt.subplots()

# Plot Output Optical Power vs Input Optical Power

ax1.plot(wlen_range, Input_power_onchip, ":bo", label="Output Power")
ax1.set_xlabel("Wavelength (nm)", fontsize=14)
ax1.set_ylabel("Input Optical Power (dBm)", fontsize=14, color='b')
ax1.tick_params(axis='y', colors='b', size=4, width=1.5)
ax1.minorticks_on()  # Enable minor ticks

# Create twin axis for Gain
ax2 = ax1.twinx()
ax2.plot(wlen_range, Output_power_onchip, ":ro", label="Gain")  
ax2.set_ylabel("Output Optical Power  (dBm)", fontsize=14, color='r')
ax2.tick_params(axis='y', colors='r', size=4, width=1.5)
ax2.minorticks_on()  # Enable minor ticks

# Title and Grid
plt.title(f'OL SOA TS7018 180mA 80°C')
ax1.grid(color='grey', which='major', linestyle='-', linewidth=0.5)
ax1.grid(color='grey', which='minor', linestyle='--', linewidth=0.35)

plt.savefig(f'OL_SOA_TS7018_180mA_80C_Wavelength_Sweep_3.png', dpi=300)
# Show the plot
plt.show()
#%%
fig, ax1 = plt.subplots()

# Plot Output Optical Power vs Input Optical Power
ax1.plot(wlen_range, OSA_SMSR, ":bo", label="SMSR")
ax1.set_xlabel("Wavelength (nm)", fontsize=14)
ax1.set_ylabel("Side Mode Supression Ratio (dB)", fontsize=14, color='b')
ax1.tick_params(axis='y', colors='b', size=4, width=1.5)
ax1.minorticks_on()  # Enable minor ticks

# Create twin axis for Gain
ax2 = ax1.twinx()
ax2.plot(wlen_range, onchip_gain, ":ro", label="Gain")  
ax2.set_ylabel("Optical Gain (dB)", fontsize=14, color='r')
ax2.tick_params(axis='y', colors='r', size=4, width=1.5)
ax2.minorticks_on()  # Enable minor ticks

# Title and Grid
plt.title(f'OL SOA TS7018 180mA 80°C')
ax1.grid(color='grey', which='major', linestyle='-', linewidth=0.5)
ax1.grid(color='grey', which='minor', linestyle='--', linewidth=0.35)

plt.savefig(f'OL_SOA_TS7018_180mA_80C_Wavelength_Sweep_3.png', dpi=300)
# Show the plot
plt.show()


# %%
instrument_1.close()
instrument_2.close()
# %%
