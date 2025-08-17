#%% Importing the required libraries and initiating a connection
import time
import tables
import pyvisa
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Initialize the VISA resource manager
rm = pyvisa.ResourceManager()

# Open a connection to the device
instrument = rm.open_resource('USB::0x0AAD::0x0117::102483::INSTR')

# Check the connectivity
i=0
for i in range(2):
    device = instrument.query('*IDN?')
    if i == 1:
        print(f"Device Connected: {device}")
    i=i+1

file_number = 1

#%% Set the channel

channel = int(input('Input the channel you want to use: '))
command = f'INST:NSEL {channel}'
instrument.write(command)
i=0
for i in range(2):
    chnl = instrument.query('INST:NSEL?')
    if i == 1:
        print(f"Channel Selected: {chnl}")
    i=i+1

#%% Set the maximum current

crnt = float(input('Input the maximum allowable current: '))
print(f'The maximum current you inserted is: {crnt} A')

#%% Start the biasing

V_applied = [] 
I_measured = []
P_calculated = []

steps = float(input('Input the step size between each voltage: '))
i = 0
for i in np.arange(0,31,steps):
    instrument.write(f'VOLT {i}')
    j=0
    k=0
    for j in range(2):
        voltage = instrument.query('VOLT?').strip()
        if j == 1:
            print(f"Applied voltage on channel: {voltage} V")
            #V_applied.append(voltage)
        
    for k in range(2):
        current = instrument.query('CURR?').strip()
        if k == 1:
            print(f"Measured current on channel: {current} A")
            #I_measured.append(current)

    voltage = float(voltage)
    V_applied.append(voltage)
    current = float(current)
    I_measured.append(current)
    power = voltage * current
    print(f"Power = {power} W")
    P_calculated.append(power)
        
    i=i+steps

#%%

df = pd.DataFrame({
    'V_applied': V_applied,
    'I_measured': I_measured,
    'P_calculated': P_calculated
})

current_date = datetime.datetime.now().strftime('%Y%m%d')
# Specify the filename
filename = f'Data_{current_date}_{file_number}.h5'

# Save the DataFrame to an HDF5 file
df.to_hdf(filename, key='data', mode='w')

file_number += 1

print(f"Data saved to {filename}")

#%% Saving the data

# Create a DataFrame from the arrays
df = pd.DataFrame({
    'V_applied': V_applied,
    'I_measured': I_measured,
    'P_calculated': P_calculated
})

current_date = datetime.datetime.now().strftime('%Y%m%d')
# Specify the filename
filename = f'Data{current_date}_{file_number}.csv'

# Save the DataFrame to a CSV file
df.to_csv(filename, index=False)

file_number = file_number + 1

print(f"Data saved to {filename}")

#%% Controlling the channel output

#channel = 1
#state='OFF'
#command = f'OUTP:SEL {state},{channel}'
#instrument.write(command)
#print(f"Output on channel {channel} turned {state}")

#%% Controlling the master output

#channel=1
#state='OFF'
#command = f'OUTP {state},{channel}'
#instrument.write(command)
#print(f"Output on channel {channel} turned {state}")


#%% Terminating the connection

instrument.close()