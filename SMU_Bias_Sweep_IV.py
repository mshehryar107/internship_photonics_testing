#%%
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

#%% SMU init
rm = visa.ResourceManager()
rm.list_resources()

#%%
#To communicate with SMU and read the current and voltage
"""
Connection with SMU
"""
#SMU = rm.open_resource('TCPIP0::172.16.30.1::inst0::INSTR')
SMU = rm.open_resource('TCPIP0::K-B2912B-90408::inst0::INSTR')
print("SMU ID: "+SMU.query("*IDN?"))
print("SMU current value: "+SMU.query(":MEAS:CURR?"))
print("SMU Voltage value: "+SMU.query(":MEAS:VOLT?"))


#%%
#To set the current sweep range
smu_voltage = np.arange(0,10.5E-3,0.5E-3)

#make sure that the connection is reverse biased 
#That is anode connected to the negative
#%%
N = 10001
Nn = 100001
smu_current = np.zeros(np.size(smu_voltage))
smu_measured_v = np.zeros(np.size(smu_voltage))
#time.sleep(1)
for i in range(np.size(smu_current)):
    #stringg = str(smu_voltage[i])
    #stringgby = stringg.encode('UTF-8')
    #SMU.write(':SOUR1:VOLT 0.1')
    SMU.write(':SOUR1:VOLT '+str(smu_voltage[i]))
    smu_measured_v[i] = (float(SMU.query(":MEAS:VOLT?")))
    time.sleep(0.1)
    print('Measured SMU voltage',smu_measured_v[i])
    smu_current[i] = (float(SMU.query(":MEAS:CURR?")))
    print('Measured SMU current',smu_current[i])
    time.sleep(0.5)

#%%
#to save the data files
PD_tile = 'D4'
Set_temp = 20
Sweep = 1
hf = h5py.File('Tower_PD_'+str(PD_tile)+'_Temp_'+str(Set_temp)+'C_IV_'+str(Sweep)+'.h5','w')
#hf = h5py.File('OpenlightlaserDeviceNumber'+str(OL)+'Temp_'+str(Set_temp)+'C.h5','w')
hf.create_dataset('V_SMU',data=smu_voltage)
hf.create_dataset('Vmeasured_SMU',data=smu_measured_v)
hf.create_dataset('I_SMU',data=smu_current)
hf.close()

#%%
hfr = h5py.File('Tower_PD_B4_final_Temp_20C_IV_1.h5','r')

Current = np.array(hfr.get('I_SMU'))
Voltage = np.array(hfr.get('V_SMU'))
Measured_Voltage = np.array(hfr.get('Vmeasured_SMU'))

s = Measured_Voltage[41]/Current[41]
S_10 =round(s, 2)
shunt = Measured_Voltage/Current
shunt_r = np.average(shunt)
print('At 10mV shunt resistance is '+ str(S_10))
print('Slope shunt resistance is '+ str(shunt_r))

titl = 'Voltage vs Current'
plt.figure
plt.plot(np.array(Voltage)*1E+3,np.array(Current)*1E+6,'-bo')
plt.xlabel('Applied Voltage (mV)')
plt.ylabel('Dark Current (uA)')
plt.tight_layout()
plt.title('Voltage vs Dark Current')
#plt.savefig('Tower_PD_'+str(PD_tile)+'_Temp_'+str(Set_temp)+'C_Applied_Voltage_Dark_Current_'+str(Sweep)+'.png',dpi=300)
plt.show()

titl = 'Measured Voltage vs Current'
plt.figure
plt.plot(np.array(Measured_Voltage)*1E+3,np.array(Current)*1E+6,'-ro')
plt.xlabel('Measured Voltage (mV)')
plt.ylabel('Dark Current (uA)')
plt.tight_layout()
plt.title('Measured Voltage vs Dark Current')
#plt.text(0, 9, 'Shunt resistance is '+ str(S_10)+' Ohm')
#plt.savefig('Tower_PD_'+str(PD_tile)+'_Temp_'+str(Set_temp)+'C_Measured_Voltage_Dark_Current_'+str(Sweep)+'.png',dpi=300)
plt.show()


hfr.close()
#%%
SMU.write(":OUTP1 0")
SMU.close()
# %%
