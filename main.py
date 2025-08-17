#Libraries generally used
import matplotlib.pyplot as plt
import pyvisa as visa
import numpy as np
import time
import h5py

#%% Resource Manager
#To check the device list conneceted
rm = visa.ResourceManager()
rm.list_resources()
#%%
# Connect to the SSA3075X
ESA = rm.open_resource('TCPIP0::192.168.2.30::INSTR') 

ESA.write(":TRACe:MODE WRITe")  # Disable Max Hold and set to Write mode
print("Max Hold turned off, trace set to Write mode.")

# Query sweep configuration
start_freq = float((ESA.query(':FREQ:START?')))
stop_freq = float((ESA.query(':FREQ:STOP?')))
points = int(ESA.query(':SWE:POIN?'))

# Calculate frequencies manually
freq_step = (stop_freq - start_freq) / (points - 1)
frequencies = [(start_freq + i * freq_step)/ 1e9 for i in range(points)]

#%% Connect to Temperature Controller (Thorlabs ITC4001)
# Initializing the temperature controller
ITC4001_addr = 'USB0::0x1313::0x804A::M00752786::INSTR'
ITC4001_dev = rm.open_resource(ITC4001_addr)
print('Temperature Controller: ' + str(ITC4001_dev.query('*IDN?')))

#%%
AFG_addr = 'USB0::0x0699::0x0359::C010224::INSTR'
AFG_dev = rm.open_resource(AFG_addr)
print('Arbitraty Frequency Generator: ' + str(AFG_dev.query('*IDN?')))

#%%
Set_temp = np.arange(25, 75, 10)  # Temperature set points
Set_freq = [10, 100, 1E3, 10E3, 100E3, 500E3, 1E6]  # Frequency set points

#%% 
for i in range(np.size(Set_temp)):

    ITC4001_dev.write(f'SOUR2:TEMP {Set_temp[i]}')  # Set temperature to T_1_min
    time.sleep(1)
    ITC4001_dev.write('OUTP2 1')  # Turn on the TEC
    time.sleep(10)  # Wait for the temperature to stabilize
    print(f'Temp is set at {ITC4001_dev.query("MEAS:TEMP?")} Degree C')

    for j in range(np.size(Set_freq)):

        AFG_dev.write(f"SOUR1:FREQ {Set_freq[j]}")  # Set frequency
        time.sleep(1)
        print(f'Frequency is set at {AFG_dev.query("FREQ?")} Hz')

        AFG_dev.write(":TRACe1:INIT:IMM")  # Force an immediate initialization
        print("Trace 1 initialized.")
        time.sleep(2)  # Wait for a moment

        AFG_dev.write(":TRACe1:MODE MAXHold")  # Set trace mode to Max Hold
        print("Trace 1 set to Max Hold mode.")

        time.sleep(300)  # Wait for 5 minutes (300 seconds)

        # Retrieve amplitude data
        amplitudes = ESA.query(':TRACE:DATA?').strip().split(',')
        amplitudes = [float(amp) for amp in amplitudes]  # Convert to float

        # Save data to .h5 file
        filename = f'DRV800_Modgain0_Freq_Chirp_{Set_temp[i]}_80mA_650mVpp_{Set_freq[j]:.1f}.h5'
        with h5py.File(filename, 'w') as hf:
            hf.create_dataset('freq', data=Set_freq)  # Save frequency data
            hf.create_dataset('amp', data=amplitudes)  # Save amplitude data
        print(f'Data saved to {filename}')