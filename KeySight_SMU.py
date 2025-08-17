#%% Import Modules

import pyvisa
import matplotlib.pyplot as plt
import pyvisa as visa
import numpy as np
import time
import math
import serial
from koheron import connect
from pyvisa import ResourceManager
#from TLPM import TLPM
import h5py
from datetime import datetime
from ctypes import c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int16,c_double
import scipy.io
#from drivers import Laser

#%% SMU initializing

rm = visa.ResourceManager()
rm.list_resources()

#%% To communicate with SMU and read the current and voltage
"""
Connection with SMU
"""
SMU = rm.open_resource('TCPIP0::K-B2912B-90408::inst0::INSTR')
print("SMU ID: "+SMU.query("*IDN?"))
print("SMU current value: "+SMU.query(":MEAS:CURR? (@1)"))
print("SMU Voltage value: "+SMU.query(":MEAS:VOLT? (@1)"))
print("SMU current value: "+SMU.query(":MEAS:CURR? (@2)"))
print("SMU Voltage value: "+SMU.query(":MEAS:VOLT? (@2)"))

#%% 2D Bias using Channel 1 and Channel 2
# Channel 1 for ring0
# Channel 2 for ring1

Applied_power_iring0 = np.arange(0,50E-3,1E-3)
iring0 = np.zeros(np.size(Applied_power_iring0))
Resistance = 41
iring0 = np.sqrt(Applied_power_iring0 / Resistance)

Applied_power_iring1 = np.arange(0,50E-3,1E-3)
iring1 = np.zeros(np.size(Applied_power_iring1))
Resistance = 41
iring1 = np.sqrt(Applied_power_iring1 / Resistance)

#iring0 = np.arange(0,10.5E-3,0.5E-3)
#print("SMU current value for ring0: "+SMU.query(":MEAS:CURR? (@1)"))
#print("SMU Voltage value for ring0: "+SMU.query(":MEAS:VOLT? (@1)"))

#iring1 = np.arange(0,10.5E-3,0.5E-3)
#print("SMU current value for ring1: "+SMU.query(":MEAS:CURR? (@2)"))
#print("SMU Voltage value for ring1: "+SMU.query(":MEAS:VOLT? (@2)"))

#%% Declaration of data arrays

ring_0_current = np.zeros(np.size(iring0))
ring_1_current = np.zeros(np.size(iring1))
ring_0_voltage = np.zeros(np.size(iring0))
ring_1_voltage = np.zeros(np.size(iring1))
ring_0_power = np.zeros(np.size(iring0))
ring_1_power = np.zeros(np.size(iring1))
#PMD_power = np.zeros((np.size(iring0), np.size(iring1)))

#%% Running a 2D Sweep

for i in range(np.size(iring0)):
    SMU.write(':SOUR1:CURR '+str(iring0[i]))
    time.sleep(0.25)
    ring_0_current[i] = (float(SMU.query(":MEAS:CURR? (@1)")))
    ring_0_voltage[i] = (float(SMU.query(":MEAS:VOLT? (@1)")))
    ring_0_power[i] = ring_0_current[i]*ring_0_voltage[i]
    print("Ring0, Drawn voltage(V): " + str(ring_0_voltage[i]) + " , current(A): " + str(ring_0_current[i]) + " and power (W): " + str(ring_0_power[i]))
    for j in range(np.size(iring1)):
        SMU.write(':SOUR2:CURR '+str(iring1[j]))
        time.sleep(0.25)
        ring_1_current[j] = (float(SMU.query(":MEAS:CURR? (@2)")))
        ring_1_voltage[j] = (float(SMU.query(":MEAS:VOLT? (@2)")))
        ring_1_power[j] = ring_1_current[j]*ring_1_voltage[j]
        print("Ring1, Drawn voltage(V): " + str(ring_1_voltage[j]) + " , current(A): " + str(ring_1_current[j]) + " and power (W): " + str(ring_1_power[j]))
        #PMD_power[(i,j)] = (float(SMU.query(":MEAS:CURR?"))*-4.65)*94000/6
        #print('Monitor PMD Power (W): ' + PMD_power[(i,j)])

# %%

#plt.figure
#plt.plot(ring_0_power)

plt.figure
plt.plot(ring_1_power)

#%%

SMU.close()

# %%
