#Libraries generally used
import matplotlib.pyplot as plt
import pyvisa as visa
import numpy as np
import time
import h5py

#%% Resource Manager
rm = visa.ResourceManager()
print(rm)

#%% Connect to KeySight SMU
SMU = rm.open_resource('TCPIP0::K-B2912B-90408::inst0::INSTR')
print("SMU ID: " + SMU.query("*IDN?"))

#%% Connect to Temperature Controller (Thorlabs ITC4001)
# Initializing the temperature controller
ITC4001_addr = 'USB0::0x1313::0x804A::M00752785::INSTR'
ITC4001_dev = rm.open_resource(ITC4001_addr)
print('Temperature Controller: ' + str(ITC4001_dev.query('*IDN?')))

#%% Connect to Thorlabs PM100 and PM100D Power Meters
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
tlPM1 = rm.open_resource(thorlabs_devices[0])
tlPM2 = rm.open_resource(thorlabs_devices[1])

#%%
device_id = tlPM1.query("*IDN?")
print(f"Connected to {thorlabs_devices[0]}: {device_id}")

# Configure the instrument (set power unit to dBm)
tlPM1.write("SENS:POW:UNIT DBM")
            
# Measure power
power = float(tlPM1.query("MEAS:POW?"))
print(f"{thorlabs_devices[0]} - Power: {power} dBm\n")

time.sleep(1)

device_id = tlPM2.query("*IDN?")
print(f"Connected to {thorlabs_devices[1]}: {device_id}")

# Configure the instrument (set power unit to dBm)
tlPM2.write("SENS:POW:UNIT DBM")
            
# Measure power
power = float(tlPM2.query("MEAS:POW?"))
print(f"{thorlabs_devices[1]} - Power: {power} dBm")


# Set current sweep range
smu_current = np.arange(0, 200E-3, 5E-3)

# Data Arrays
smu_voltage = np.zeros(len(smu_current))
smu_measured_i = np.zeros(len(smu_current))
electrical_power = np.zeros(len(smu_current))

In_OP = np.zeros(len(smu_current))


Out_OP = np.zeros(len(smu_current))

# For loop for current sweep
for i, current in enumerate(smu_current):
    SMU.write(f':SOUR1:CURR {current}')
    time.sleep(0.5)
    smu_voltage[i] = float(SMU.query(":MEAS:VOLT?"))
    smu_measured_i[i] = float(SMU.query(":MEAS:CURR?"))
    electrical_power[i] = smu_voltage[i] * smu_measured_i[i]
    In_OP[i] = float(tlPM1.query('READ?')) * 1e3  # Convert to mW
    Out_OP[i] = float(tlPM2.query('READ?')) * 1e3  # Convert to mW
    print(f'Current: {current} A, Voltage: {smu_voltage[i]} V, Power: {electrical_power[i]} W')

# Data saving to HDF5
hf = h5py.File('File_Name.h5', 'w')
hf.create_dataset('ILaser', data=smu_current)
hf.create_dataset('volt', data=smu_voltage)
hf.create_dataset('Idrawn', data=smu_measured_i)
hf.create_dataset('Pdrawn', data=electrical_power)
hf.create_dataset('Pinput', data=In_OP)
hf.create_dataset('Poutput', data=Out_OP)
hf.close()

#%%
hfr = h5py.File(f'OL_SOA_C_TS70{OL}_{wavelength}nm_Temp_{Set_temp}C.h5', 'r')
Current = np.array(hfr.get('ILaser')) * 1E3
voltage = np.array(hfr.get('volt'))
E_power = np.array(hfr.get('Pdrawn'))
Input_power = np.array(hfr.get('Pinput'))
Output_power = np.array(hfr.get('Poutput'))

# Plot IV Curve
fig, ax = plt.subplots()
twin1 = ax.twinx()

ax.plot(Current, voltage, "-bo", label="Voltage")
twin1.plot(Current, E_power, "-ro", label="Electrical Power")
twin1.plot(Current, Output_power, "-go", label="Output Optical Power")

ax.set_xlabel("Current (mA)")
ax.set_ylabel("Voltage (V)")
twin1.set_ylabel("Power (mW)")
plt.title(f'OL SOA IV Curve at {Set_temp}°C')
plt.legend()
plt.grid(True)
plt.show()

#%%
tlPM1.close()
tlPM2.close()
