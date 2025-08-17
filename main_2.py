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
instrument_1 = rm.open_resource(thorlabs_devices[1])
instrument_2 = rm.open_resource(thorlabs_devices[0])

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

#%% Setting Attenuation Range 
# Set the attenuation sweep parameters
start_attenuation = 0  # Starting attenuation in dB
end_attenuation = 30  # Ending attenuation in dB
step_size = 1        # Step size for attenuation sweep in dB
Attenuation_range=np.arange(start_attenuation, end_attenuation + step_size, step_size)
Input_power_before_GC = 10 - Attenuation_range
Onchip_IN_P_dBm = Input_power_before_GC - 5
#GC = 5.05
#Attenuation_range = att_range + GC

#%%
#to communicate to the VOA
attenuator = rm.open_resource('ASRL5::INSTR',)
attenuator.write('A'+str(Attenuation_range[0]))
time.sleep(10)

#%% Connect to KeySight SMU
SMU = rm.open_resource('TCPIP0::K-B2912B-90408::inst0::INSTR')
print("SMU ID: " + SMU.query("*IDN?"))

#%% Connect to Temperature Controller (Thorlabs ITC4001)
# Initializing the temperature controller
ITC4001_addr = 'USB0::0x1313::0x804A::M00752785::INSTR'
ITC4001_dev = rm.open_resource(ITC4001_addr)
print('Temperature Controller: ' + str(ITC4001_dev.query('*IDN?')))

#%%
# Set initial temparature for ITC4001
#Ask for the temperature needs to be set, mimimum 20 degree C and maximum 80 degree C
Set_temp = input('Enter the temperature in degree C:')
time.sleep(1)
ITC4001_dev.write('SOUR2:TEMP '+str(Set_temp)) #temp is set at T_1_min
time.sleep(1)
ITC4001_dev.write('OUTP2 1') # Turn on the TEC, test.
print('Caution: Temperature of the Holder is ON')
#to check the set temprature value, wait for 5 minutes
time.sleep(10)
print('Temp is set at ' + ITC4001_dev.query('MEAS:TEMP?') + ' Degree C')

#%%
# Set current sweep range
smu_current = np.arange(0, 205E-3, 5E-3)
temp = [20]
#temp = np.arange(20,90,10)

# Data Arrays
smu_voltage = np.zeros(len(smu_current))
smu_measured_i = np.zeros(len(smu_current))
electrical_power = np.zeros(len(smu_current))

#GC = [5.05,5.24,7.175,11.205,17.465,22.675,25.205]
In_OP = np.zeros(len(Attenuation_range))
Out_OP = np.zeros(len(Attenuation_range))

Onchip_OUT_P_at_0_dBm = np.zeros(len(smu_current))

#%%
for k in range(np.size(temp)):
    
    ITC4001_dev.write('SOUR2:TEMP '+str(k))
    time.sleep(20)

    for i in range(np.size(smu_current)):
        
        SMU.write(':SOUR1:CURR '+str(smu_current[i]))
        time.sleep(0.5)
        smu_voltage[i] = (float(SMU.query(":MEAS:VOLT?")))
        print('Measured SMU voltage',smu_voltage[i])
        smu_measured_i[i] = (float(SMU.query(":MEAS:CURR?")))
        print('Measured SMU current',smu_measured_i[i])
        electrical_power[i] = smu_measured_i[i]*smu_voltage[i]
        print('Measured SMU Power',electrical_power[i])

        for j in range(np.size(Attenuation_range)):

            attenuator.write('A'+str(Attenuation_range[j]))
            time.sleep(5)

            In_OP[j] = float(instrument_1.query('MEAS:POW?'))
            #print('Power meter (dBm)',In_OPT)
            In_OP[j] = 10 * np.log10(10**(In_OPT/10) * 100)
            print('Power meter (dBm) INPUT ',In_OP[j])
            #Out_OPT = float(instrument_2.query('MEAS:POW?'))
            #print('Power meter (dBm)',Out_OPT)
            #Out_OP[j] = 10*np.log10(10^(Out_OPT/10)*10)
            Out_OP[j] = float(instrument_2.query('MEAS:POW?'))
            print('Power meter (dBm) OUTPUT ',Out_OP[j])

            if(Attenuation_range[j]==15):
                Onchip_OUT_P_at_0_dBm[i] = Out_OP[j] + 6

        Onchip_OUT_P_dBm = Out_OP + 6

        # Data saving to HDF5
        hf = h5py.File(f'OL_SOA_TS7018_{smu_current[i]*1E3}mA_{temp[k]}C.h5', 'w')
        hf.create_dataset('Pinput', data=In_OP)
        hf.create_dataset('Pinputonchip', data=Onchip_IN_P_dBm)
        hf.create_dataset('Poutput', data=Out_OP)
        hf.create_dataset('Poutputonchip', data=Onchip_OUT_P_dBm)
        hf.close()

        hfr = h5py.File(f'OL_SOA_TS7018_{smu_current[i]*1E3}mA_{temp[k]}C.h5', 'r')
        Input_power = np.array(hfr.get('Pinput'))
        Output_power = np.array(hfr.get('Poutput'))
        Input_power_onchip = np.array(hfr.get('Pinputonchip'))
        Output_power_onchip = np.array(hfr.get('Poutputonchip'))
        hfr.close()

        onchip_gain = Output_power_onchip - Input_power_onchip

        # ------------------ Plot 1: Output Optical Power and Gain ------------------
        fig, ax1 = plt.subplots()

        # Plot Output Optical Power vs Input Optical Power
        ax1.plot(Input_power_onchip, Output_power_onchip, "bo-", label="Output Power")
        ax1.set_xlabel("Input Optical Power (dBm)", fontsize=14)
        ax1.set_ylabel("Output Optical Power (dBm)", fontsize=14, color='b')
        ax1.tick_params(axis='y', colors='b', size=4, width=1.5)
        ax1.minorticks_on()  # Enable minor ticks

        # Create twin axis for Gain
        ax2 = ax1.twinx()
        ax2.plot(Input_power_onchip, onchip_gain, "ro-", label="Gain")  
        ax2.set_ylabel("Optical Gain (dB)", fontsize=14, color='r')
        ax2.tick_params(axis='y', colors='r', size=4, width=1.5)
        ax2.minorticks_on()  # Enable minor ticks

        # Title and Grid
        plt.title(f'OL SOA Output Optical Power & Gain at {smu_current[i]*1E3}mA and {temp[k]}°C')
        ax1.grid(color='grey', which='major', linestyle='-', linewidth=0.5)
        ax1.grid(color='grey', which='minor', linestyle='--', linewidth=0.35)

        plt.savefig(f'OL_SOA_Output_Output_Power_&_Gain_at_{smu_current[i]*1E3}mA_{temp[k]}C.png', dpi=300)
        # Show the plot
        plt.show()

        # ------------------ Plot 2: Gain Plot ------------------
        fig2, ax3 = plt.subplots()

        ax3.plot(Output_power_onchip, onchip_gain, "ro-", label="Gain")
        ax3.set_xlabel("Output Optical Power (dBm)", fontsize=14)
        ax3.set_ylabel("Gain (dB)", fontsize=14, color='r')
        ax3.tick_params(axis='y', colors='r', size=4, width=1.5)
        ax3.minorticks_on()

        # Title & Grid
        plt.title(f'OL SOA Gain at {smu_current[i]*1E3} mA and {temp[k]}°C')
        ax3.grid(color='grey', which='major', linestyle='-', linewidth=0.5)
        ax3.grid(color='grey', which='minor', linestyle='--', linewidth=0.35)

        # Save and Show
        plt.savefig(f'OL_SOA_Gain_{smu_current[i]*1E3}mA_{temp[k]}C.png', dpi=300)
        plt.show()


hf = h5py.File(f'OL_SOA_TS7018_IV_{temp[k]}C.h5', 'w')
hf.create_dataset('Temp', data=temp[k])
hf.create_dataset('ILaser', data=smu_current)
hf.create_dataset('volt', data=smu_voltage)
hf.create_dataset('Idrawn', data=smu_measured_i)
hf.create_dataset('Pdrawn', data=electrical_power)    
hf.create_dataset('OUTP', data=Onchip_OUT_P_at_0_dBm)
hf.close()  


hfr = h5py.File(f'OL_SOA_TS7018_IV_{temp[k]}C.h5', 'r')
Temperature = np.array(hfr.get('Temp'))
Current = np.array(hfr.get('ILaser')) * 1E3
voltage = np.array(hfr.get('volt'))
E_power = np.array(hfr.get('Pdrawn')) *1E3
Output_power_onchip_0dBm = np.array(hfr.get('OUTP'))
hfr.close()

# ------------------ Plot 1: IV Curve ------------------
fig1, ax1 = plt.subplots()
ax1.plot(Current, voltage, "-bo", label="Voltage")

ax1.set_xlabel("Current (mA)", fontsize=14)
ax1.set_ylabel("Voltage (V)", fontsize=14, color='b')
ax1.tick_params(axis='y', colors='b', size=4, width=1.5)
ax1.minorticks_on()
ax1.grid(color='grey', which='major', linestyle='-', linewidth=0.5)
ax1.grid(color='grey', which='minor', linestyle='--', linewidth=0.35)

plt.title(f'OL SOA IV Curve at {Temperature}°C')
plt.savefig(f'OL_SOA_IV_Curve_{Temperature}C.png', dpi=300)
plt.show()

# ------------------ Plot 2: Optical & Electrical Power ------------------
fig2, ax2 = plt.subplots()
twin2 = ax2.twinx()

ax2.plot(Current, E_power, "-ro", label="Electrical Power")
twin2.plot(Current, Output_power_onchip_0dBm, "-go", label="Output Optical Power")

ax2.set_xlabel("Current (mA)", fontsize=14)
ax2.set_ylabel("Electrical Power Consumption (mW)", fontsize=14, color='r')
twin2.set_ylabel("Output Optical Power (dBm)", fontsize=14, color='g')

ax2.tick_params(axis='y', colors='r', size=4, width=1.5)
twin2.tick_params(axis='y', colors='g', size=4, width=1.5)
ax2.minorticks_on()
twin2.minorticks_on()

ax2.grid(color='grey', which='major', linestyle='-', linewidth=0.5)
ax2.grid(color='grey', which='minor', linestyle='--', linewidth=0.35)

plt.title(f'OL SOA Optical & Electrical Power at {Temperature}°C')
plt.savefig(f'OL_SOA_Power_Curve_{Temperature}C.png', dpi=300)
plt.show()


# %%
instrument_1.close()
instrument_2.close()
SMU.close()
ITC4001_dev.close()

#%%

