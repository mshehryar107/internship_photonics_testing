#%%Libraries generally used
import matplotlib.pyplot as plt
import pyvisa as visa
import numpy as np
import time
import h5py

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
instrument_2 = rm.open_resource(thorlabs_devices[1])

#%%
device_id = instrument_1.query("*IDN?")
print(f"Connected to {thorlabs_devices[0]}: {device_id}")

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
power = 10 * np.log10(10**(power/10) * 99)
print(f"{thorlabs_devices[1]} - Power: {power} dBm")

#%% File name for HDF5 storage
filename = "GC_Loss_Wavelength_Sweep_Fiber_Array.h5"
total_seconds = 600  # 10 minutes
time_data = np.arange(0, total_seconds) / 60.0  # Convert seconds to minutes
input_power_data = []
output_power_data = []

# Start measurements
start_time = time.time()
for elapsed_time in range(total_seconds):
    input_power = 10 * np.log10(10**(float(instrument_2.query("MEAS:POW?"))/10) * 99)
    output_power = float(instrument_1.query("MEAS:POW?"))

    # Store data
    input_power_data.append(input_power)
    output_power_data.append(output_power)

    print(f"Time: {elapsed_time}s ({elapsed_time/60:.2f} min) | Input Power: {input_power}W | Output Power: {output_power}W")
    
    time.sleep(1)  # Wait for 1 second

# Save data in HDF5 format
with h5py.File(filename, "w") as h5f:
    h5f.create_dataset("time_minutes", data=time_data)
    h5f.create_dataset("input_power", data=input_power_data)
    h5f.create_dataset("output_power", data=output_power_data)
    h5f.close()

print(f"Data collection complete. Saved to {filename}")


#%% Load data from HDF5 and plot
with h5py.File(filename, "r") as h5r:
    time_minutes = h5r["time_minutes"][:]
    input_power = h5r["input_power"][:]
    output_power = h5r["output_power"][:]
    h5r.close()

#%% Plot settings
fig, ax1 = plt.subplots(figsize=(10, 5))

#ax1.plot(time_minutes, input_power, label="Input Power (W)", color="blue")
ax1.plot(time_minutes, output_power, label="Output Power (W)", color="red", linestyle="dashed")

ax1.set_xlabel("Time (minutes)", fontsize=14)
ax1.set_ylabel("Power (dBm)", fontsize=14)
ax1.set_title("Power Measurements Over Time")
ax1.legend()
ax1.grid(True)
plt.savefig(f'{filename}.png', dpi=300)

plt.show()
# %%
instrument_1.close()
instrument_2.close()
# %%
