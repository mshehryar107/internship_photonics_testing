#%%
import pyvisa
import time

# Initialize the ResourceManager
rm = pyvisa.ResourceManager()

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
instrument_1 = rm.open_resource(thorlabs_devices[0])
instrument_2 = rm.open_resource(thorlabs_devices[1])

#%%
device_id = instrument_1.query("*IDN?")
print(f"Connected to {thorlabs_devices[0]}: {device_id}")

# Configure the instrument (set power unit to dBm)
instrument_1.write("SENS:POW:UNIT DBM")
            
# Measure power
power = float(instrument_1.query("MEAS:POW?"))
print(f"{thorlabs_devices[0]} - Power: {power} dBm\n")

time.sleep(1)

device_id = instrument_2.query("*IDN?")
print(f"Connected to {thorlabs_devices[1]}: {device_id}")

# Configure the instrument (set power unit to dBm)
instrument_2.write("SENS:POW:UNIT DBM")
            
# Measure power
power = float(instrument_2.query("MEAS:POW?"))
print(f"{thorlabs_devices[1]} - Power: {power} dBm")


# %%
instrument_1.close()
instrument_2.close()

# %%
