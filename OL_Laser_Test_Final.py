c#Laser test 'Openlight'
# -*- coding: utf-8 -*-
"""
Created on 22.04.2024
@author: Karanveer Singh
"""
#%%
#Importing all required modules
##If something is missing and needs to be added please add here##
import matplotlib.pyplot as plt
import pyvisa as visa
import numpy as np
import time
import math
import serial
from koheron import connect
from pyvisa import ResourceManager
from TLPM import TLPM
import h5py
from datetime import datetime
from ctypes import c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int16,c_double
import scipy.io
from drivers import Laser
#%%
#Select the laser device from the sample you are testing
OL = int(input('Enter the Openlight Laser 1550 nm : ')) 

####
#%%
#To check the device list conneceted
rm = visa.ResourceManager()
rm.list_resources()

#print('Identify the device and provide the correct address to communicate')

####
# %%
# initializing the thorlabs ITC4001 temperature controller
ITC4001_addr = 'USB0::0x1313::0x804A::M00752785::INSTR'
ITC4001_dev = rm.open_resource(ITC4001_addr)
print('Temperature controller : ' + str(ITC4001_dev.query('*IDN?')))
#PM100D_dev.write('SENS:AVER:COUN 10');   # making average with 10 samples (0.03s)


#%%
#To communicate with SMU and read the current and voltage
"""
MPD control with SMU
"""
#SMU = rm.open_resource('TCPIP0::172.16.30.67::inst0::INSTR')
SMU = rm.open_resource('TCPIP0::K-B2912B-90408::inst0::INSTR')
print("SMU ID: "+SMU.query("*IDN?"))
print("SMU current value: "+SMU.query(":MEAS:CURR?"))
print("SMU Voltage value: "+SMU.query(":MEAS:VOLT?"))


#%%
#To communicate with thorlabs power meter
ThorPM = rm.open_resource('USB0::0x1313::0x8078::P0032715::0::INSTR')
ThorPM.query('*IDN?')
ThorPM.write('SENS:POW:AUTO ON')
ThorPM.write('SENS:POW:UNIT W')
ThorPM.write('CORR:WAV 1550 nm')
P = float(ThorPM.query('READ?'))*1E+3
print('Power (mW)',P)

#%%
def waitCompletion(Dev_object):
    print('Waiting for completion...')
    Dev_object.write('*CLS')
    while int(Dev_object.query('ESR2?')) == 0:
        time.sleep(0.05)
    print('Complete\n')

#%%
#To coominicate the with OSA
OSA_addr = 'TCPIP0::OSA-R4NJQFJ06WB::inst0::INSTR'
OSA_dev_1 = rm.open_resource(OSA_addr)
strt_wlen = OSA_dev_1.query("STA?")
end_wlen = OSA_dev_1.query("STO?")

print('DEVICE NAME: ' + str(OSA_dev_1.query("*IDN?")))
print('Start wavelength: ' + strt_wlen)
print('Stop wavelength: ' + end_wlen)
print('Span: ' + str(OSA_dev_1.query('SPN?')))
print('Y data unit : ' + str(OSA_dev_1.query('LVS?'))) # LIN|LOG
print('Attenuation : ' + str(OSA_dev_1.query('ATT?'))) # ON|OFF
print('Automeasure : ' + str(OSA_dev_1.query('AUT?'))) # 0|1
print('Point average : ' + str(OSA_dev_1.query('AVT?'))) # 2|1000
print('Sweep average : ' + str(OSA_dev_1.query('AVS?'))) # 1|1000
print('Analysis method : ' + str(OSA_dev_1.query('ANA?'))) #

print('Resolution: ' + str(OSA_dev_1.query('RES?')))
# possible values[nm]: 0.03 | 0.05 | 0.07 | 0.1 | 0.2 | 0.5 | 1.0
OSA_dev_1.write('RES 0.03')
print('Resolution: ' + str(OSA_dev_1.query('RES?')))

print('VBW: ' + str(OSA_dev_1.query('VBW?')))
# possible values[Hz]: 10|100|200|1000|2000|10000|100000|1000000|200FAST|1000FAST
OSA_dev_1.write('VBW 1000')
print('VBW: ' + str(OSA_dev_1.query('VBW?')))

print('Sampling points: ' + str(OSA_dev_1.query('MPT?')))
# related to span and resolution : Num. pts >= Span/Res + 1
# possible values[arb]: 51|101|251|501|1001|2001|5001|10001|20001|50001
OSA_dev_1.write('MPT 1001')
num_samp_pts = OSA_dev_1.query('MPT?')
print('Sampling points: ' + num_samp_pts)

wlen_axis = np.linspace(float(strt_wlen),float(end_wlen),int(num_samp_pts))
tt = time.time()

OSA_dev_1.write('SSI')
waitCompletion(OSA_dev_1)

OSA_dev_1.write('PKS PEAK')
time.sleep(1)

#%%
#To communicate with Koheron Driver and set the gain medium current
Koheron_LD = serial.Serial(port='COM5',baudrate=115200,timeout=1)
Koheron_LD.write_termination='\r\n'
Koheron_LD.read_termination='\r\n'


#Koheron_LD.write(b'lason 1 0\r\n')
#print(Koheron_LD.readlines())
#Koheron_LD.write(b'rtact 1 \r\n')
#print(Koheron_LD.readlines())
#The optimum working point for the laser -1 (gain medium) is 100 mA

Koheron_LD.write(b'ilaser 2 100\r\n')
print(Koheron_LD.readlines())
Koheron_LD.write(b'vmon 2\r\n')
vv = str(b''.join(Koheron_LD.readlines()))
laser_2_voltage = float((vv[12:17]))
print(Koheron_LD.readlines())
print('Drawn laser volatge (V)',laser_2_voltage)


Koheron_LD.write(b'ilaser 5 0\r\n')
print(Koheron_LD.readlines())
Koheron_LD.write(b'vmon 5\r\n')
vv = str(b''.join(Koheron_LD.readlines()))
laser_5_voltage = float((vv[12:17]))
print(Koheron_LD.readlines())
print('Drawn laser volatge (V)',laser_5_voltage)


#%%
#To create a sweep for Ring-0 (Laser-2) and Ring-1 (Laser-1), and acquire 
#1 MPD Power
#Once percent output power
#2 OSA Spectrum (and save the plot)
#3 Peak wavelength

#Ring-0 and Ring-1 maximum power is 200 mW, optimum power is 50 mW.
#This power needs to be calcualted with ring0 (vmon2*imon2) and ring1(vmon3*imon3)

#Sweep parameters
#Ring-0, laser-2
iring0 = np.arange(0,41,1)
Koheron_LD.write(b'imon 3\r\n')
print(Koheron_LD.readlines())

#Ring-1, laser-3
iring1 = np.arange(0,41,1)
Koheron_LD.write(b'imon 4\r\n')
print(Koheron_LD.readlines())

#%%
Pring0 = np.arange(0,52.5*1E-3,2.5*1E-3)
Pring1 = np.arange(0,52.5*1E-3,2.5*1E-3)
res0 = 232
res1 = 203

iring0 = (Pring0/ res0)**0.5*1E+3
Koheron_LD.write(b'imon 3\r\n')
print(Koheron_LD.readlines())

iring1 = (Pring1/ res1)**0.5*1E+3
Koheron_LD.write(b'imon 4\r\n')
print(Koheron_LD.readlines())


#%%
N = 10001
Nn = 100001
Set_temp = 35
power_meter = np.zeros((np.size(iring0), np.size(iring1)))
ring_0_voltage = np.zeros(np.size(iring0))
ring_1_voltage = np.zeros(np.size(iring1))
ring_0_power = np.zeros(np.size(iring0))
ring_1_power = np.zeros(np.size(iring1))
MPD_power = np.zeros((np.size(iring0), np.size(iring1)))
OSA_Wavelength = np.zeros((np.size(iring0), np.size(iring1)))
SMSR = np.zeros((np.size(iring0), np.size(iring1)))
time.sleep(1)

#%%
for i in range(np.size(iring0)):
    #to set the sweep of laser 2 from 0 to 50 mA
    stringg = 'ilaser 3 '+str(iring0[i])+'\r\n'
    stringgby = stringg.encode('UTF-8')
    Koheron_LD.write(stringgby)
    time.sleep(0.25)
    Koheron_LD.write(b'ilaser 3\r\n')
    print(Koheron_LD.readlines())
    Koheron_LD.write(b'vmon 3\r\n')
    vv = str(b''.join(Koheron_LD.readlines()))
    ring_0_voltage[i] = float((vv[12:17]))
    #print(Koheron_LD.readlines())
    print('Drawn laser-3 volatge (V)',ring_0_voltage[i])
    ring_0_power[i] =  ring_0_voltage[i]*iring0[i]
    for j in range(np.size(iring1)):
        stringg_1 = 'ilaser 4 '+str(iring1[j])+'\r\n'
        stringgby_1 = stringg_1.encode('UTF-8')
        Koheron_LD.write(stringgby_1)
        time.sleep(0.25)
        Koheron_LD.write(b'ilaser 4\r\n')
        print(Koheron_LD.readlines())
        Koheron_LD.write(b'vmon 4\r\n')
        vv_1 = str(b''.join(Koheron_LD.readlines()))
        ring_1_voltage[j] = float((vv_1[12:17]))
        #print(Koheron_LD.readlines())
        print('Drawn laser-4 volatge (V)',ring_1_voltage[j])
        ring_1_power[j] =  ring_1_voltage[j]*iring1[j]
        #To acquire the power values 
        power_meter[(i,j)] = float(ThorPM.query('READ?'))*1E+3
        print('Power meter (mW)',power_meter[(i,j)])
        MPD_power[(i,j)] = (float(SMU.query(":MEAS:CURR?"))*-4.65)*94000/6
        print('Monitor PD Power (mW)',MPD_power[(i,j)])
        #Now the OSA spectrums
        time.sleep(0.10)
        OSA_dev_1.write('MPT 1001')
        num_samp_pts = OSA_dev_1.query('MPT?')
        #print('Sampling points: ' + num_samp_pts)

        wlen_axis = np.linspace(float(strt_wlen),float(end_wlen),int(num_samp_pts))
        tt = time.time()

        OSA_dev_1.write('SSI')
        waitCompletion(OSA_dev_1)

        OSA_dev_1.write('PKS PEAK')
        #time.sleep(0.5)
        mkr_xy_str = OSA_dev_1.query('TMK?')

        TempVar = mkr_xy_str.split(",")
        #SMSR[(i,j)] = float(OSA_dev_1.write(':CALCulate:CATegory SMSR'))
        #print('SMSR is '+str(SMSR[(i,j)]))
        mkr_wlen = round(float(TempVar[0]), 4)
        mkr_pow = round(float(TempVar[1].replace('DBM', '')), 3)
        y1 = OSA_dev_1.query(':TRAC:DATA:Y? TRA').replace(',\r\n','').split(",")
        #print(y1)
        y = [float(x) for x in y1]
        #print(type(y))
        plt.plot(wlen_axis,y)
        plt.plot(float(mkr_wlen),float(mkr_pow),'o')
        plt.savefig('Openlight_laser_Device_'+str(OL)+'_Temp_'+str(Set_temp)+'C_'+str(round(ring_0_power[i],1))+'mW'+str(round(ring_1_power[j],1))+'mW.png',dpi=300)
        plt.show()
        print('By max power:',np.amax(y))
        peak_indx = int(np.where(y==np.amax(y))[0])
        print('By max wlen:', wlen_axis[peak_indx])
        print('Wavelength mkr: ', str(mkr_wlen), 'nm')
        print('Power mkr: ', str(mkr_pow), 'dBm')
        OSA_Wavelength[(i,j)] = float(mkr_wlen)

        #This part is for calculating SMSR
        time.sleep(0.5)
        peak1_index = np.argmax(y)
        power1 = y[peak1_index]
        peak_range = np.arange(peak1_index-5,peak1_index+5,1)
        for k in peak_range:
            y[k] = -80  # Remove the first peak
        #plt.plot(wlen_axis,y)
        peak2_index = np.argmax(y)
        power2 = y[peak2_index]
        # Calculate the power difference between the two peaks
        power_difference = power1 - power2
        SMSR[i,j] = float(power_difference)
        print('SMSR is '+str(SMSR[(i,j)]))

        
        #(OSA_dev_1.write(':CALCulate:CATegory SMSR'))
        #smsr = OSA_dev_1.query(':CALC:DATA?')
        #SMSR[i,j] = float(smsr[18:23])*10
        #print('SMSR is '+str(SMSR[(i,j)]))
time.sleep(0.5)


print('Sweep is complete')
#%%
#To save all the data files
hf = h5py.File('OL_1550nm_laserDeviceNumber'+str(OL)+'Temp_'+str(Set_temp)+'C_R0R1_Fine_PS_Off_1.h5','w')
#hf = h5py.File('OpenlightlaserDeviceNumber'+str(OL)+'Temp_'+str(Set_temp)+'C.h5','w')
hf.create_dataset('Iring0',data=iring0)
hf.create_dataset('Iring1',data=iring1)
hf.create_dataset('volt0',data=ring_0_voltage)
hf.create_dataset('volt1',data=ring_1_voltage)
hf.create_dataset('Pring0',data=ring_0_power)
hf.create_dataset('Pring1',data=ring_1_power)
hf.create_dataset('PowThf',data=power_meter)
hf.create_dataset('MPDPower',data=MPD_power)
hf.create_dataset('Wavelength',data=OSA_Wavelength)
hf.create_dataset('Sidemode',data=SMSR)
hf.close()

#%%
Koheron_LD.write(b'ilaser 2 0\r\n')
print(Koheron_LD.readlines())
Koheron_LD.write(b'ilaser 3 0\r\n')
print(Koheron_LD.readlines())
Koheron_LD.write(b'ilaser 4 0\r\n')
print(Koheron_LD.readlines())
Koheron_LD.write(b'ilaser 5 0\r\n')
print(Koheron_LD.readlines())
Koheron_LD.close() #Close the connection for Koheron driver
#ThorPM.close()
#HMP4040_dev_1.write('OUTPut:GENeral 0')
#HMP4040_dev_1.close() #to terminate the connection

#%%
#To plot the recorded data
hfr = h5py.File('OL_1550nm_laserDeviceNumber'+str(OL)+'Temp_'+str(Set_temp)+'C_R0R1_Fine_PS_Off_1.h5','r')

Current_0 = np.array(hfr.get('Iring0'))
Current_1 = np.array(hfr.get('Iring1'))
Voltage_0 = np.array(hfr.get('ring_0_voltage'))
Voltage_1 = np.array(hfr.get('ring_1_voltage'))
R_Power_0 = np.array(hfr.get('Pring0'))
R_Power_1 = np.array(hfr.get('Pring1'))

power_onchip = np.array(hfr.get('MPDPower'))
power_out = np.array(hfr.get('power_meter'))
wavelength = np.array(hfr.get('Wavelength'))
smsr_1 = np.array(hfr.get('Sidemode'))

#To make the countour plot
#plt.contourf(R_Power_0, R_Power_1, wavelength, 20, cmap='RdGy')
plt.contourf(Current_0, Current_1, wavelength,100)
plt.colorbar()
plt.xlabel('Ring-0 Current (mA)')
plt.ylabel('Ring-1 Current (mA)')
plt.title('Operating wavelength (nm) Phase Tuner OFF')
plt.savefig('OL_Chirped_Laser_TS30'+str(OL)+'_Temp_'+str(Set_temp)+'C_Wavelength_OFF.png',dpi=300)
plt.show()

#plt.contourf(R_Power_0, R_Power_1, power_onchip, 20, cmap='RdGy')
plt.contourf(Current_0, Current_1, power_onchip,100)
plt.colorbar()
plt.xlabel('Ring-0 Current (mA)')
plt.ylabel('Ring-1 Current (mA)')
plt.title('On Chip Opitcal Power (mW) Phase Tuner OFF')
plt.savefig('OL_Chirped_Laser_TS30'+str(OL)+'_Temp_'+str(Set_temp)+'C_On_Chip_Power_OFF.png',dpi=300)
plt.show()

#plt.contourf(R_Power_0, R_Power_1, smsr_1, 20, cmap='RdGy')
plt.contourf(Current_0, Current_1, smsr_1, 100)
plt.colorbar()
plt.xlabel('Ring-0 Current (mA)')
plt.ylabel('Ring-1 Current (mA)')
plt.title('Side mode supression ratio (dB) Phase Tuner OFF')
plt.savefig('OL_Chirped_Laser_TS30'+str(OL)+'_Temp_'+str(Set_temp)+'C_SMSR_OFF.png',dpi=300)
plt.show()


#%%
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import axes3d

# Generate example data (replace with your own)

# Create a 3D contour plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.contour(Current_0, Current_1, power_onchip, cmap=cm.coolwarm)  # Plot contour curves

# Customize the plot (labels, title, etc.) as needed
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Contour Plot')

plt.show()

#%%
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d

# Generate example data (replace with your own)
X, Y, Z = axes3d.get_test_data(0.05)

# Create a 3D contour plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.contour(Current_0, Current_1, power_onchip, cmap= cm.coolwarm)   # Plot contour curves

# Clip along the z-axis (show only a specific range)
y_min, y_max = 9, 9
ax.set_ylim(y_min, y_max)

# Customize labels, title, etc. as needed
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Clipped 3D Contour Plot')

plt.show()

#%%
#To make the countour plot
#plt.contourf(R_Power_0, R_Power_1, wavelength, 20, cmap='RdGy')
plt.contourf(Pring0*1E+3, Pring1*1E+3, wavelength,25)
plt.colorbar()
plt.xlabel('Ring-0 Power Consumption (mW)')
plt.ylabel('Ring-1 Power Consumption (mW)')
plt.title('Operating wavelength (nm) Phase Tuner OFF')
#plt.savefig('OL_Chirped_Laser_TS30'+str(OL)+'_Temp_'+str(Set_temp)+'C_Wavelength_OFF.png',dpi=300)
plt.show()

#plt.contourf(R_Power_0, R_Power_1, power_onchip, 20, cmap='RdGy')
plt.contourf(Pring0*1E+3, Pring1*1E+3, power_onchip,25)
plt.colorbar()
plt.xlabel('Ring-0 Power Consumption (mW)')
plt.ylabel('Ring-1 Power Consumption (mW)')
plt.title('On Chip Opitcal Power (mW) Phase Tuner OFF')
#plt.savefig('OL_Chirped_Laser_TS30'+str(OL)+'_Temp_'+str(Set_temp)+'C_On_Chip_Power_OFF.png',dpi=300)
plt.show()

#plt.contourf(R_Power_0, R_Power_1, smsr_1, 20, cmap='RdGy')
plt.contourf(Pring0*1E+3, Pring1*1E+3, smsr_1, 25)
plt.colorbar()
plt.xlabel('Ring-0 Power Consumption (mW)')
plt.ylabel('Ring-1 Power Consumption (mW)')
plt.title('Side mode supression ratio (dB) Phase Tuner OFF')
#plt.savefig('OL_Chirped_Laser_TS30'+str(OL)+'_Temp_'+str(Set_temp)+'C_SMSR_OFF.png',dpi=300)
plt.show()

hfr.close()

#%%
lab = np.zeros(np.size(iring1))
plt.figure
for j in range(np.size(iring1)):
    lab[j] = str(float(round(R_Power_1[j],1)))
    plt.plot(R_Power_0, power_onchip[j], "-o", label = lab[j])
plt.xlabel("Ring-0 Drawn Power (mW)")
plt.ylabel("Monitor PD On-Chip Optical Power (mW)")
plt.legend(bbox_to_anchor=(1,1))
plt.title('Optical Power TS30'+str(OL)+' change with Ring heater power '+str(Set_temp)+' C_Ptuner_ON')
plt.savefig('OL_Chirped_Laser_TS30'+str(OL)+'_Temp_'+str(Set_temp)+'C_Ring_Power_Output_Power.png',dpi=300)
plt.show()

plt.figure
for j in range(np.size(iring1)):
    lab[j] = str(float(round(R_Power_1[j])))
    plt.plot(R_Power_0, wavelength[j], "-o", label = lab[j])
plt.xlabel("Ring-0 Drawn Power (mW)")
plt.ylabel("Wavelength (nm)")
plt.legend(bbox_to_anchor=(1,1))
plt.title('Wavelength TS30'+str(OL)+' change with Ring heater power '+str(Set_temp)+' C_Ptuner_ON')
plt.savefig('OL_Chirped_Laser_TS30'+str(OL)+'_Temp_'+str(Set_temp)+'C_Ring_Power_Wavelength.png',dpi=300)
plt.show()

hfr.close()





#%%
ThorPM.close()
OSA_dev_1.close()
SMU.close()
ITC4001_dev.close()
#HMP4040_dev_1.write('OUTPut:GENeral 0')
#HMP4040_dev_1.close() #to terminate the connection

































#%%
#To set the bias for the monitor photodiode
#MPD_Channel = 1
#MPD_bias = 4.65 # this is reverse biased please check pin configuration before turning it on
#MPD_current = 0.002  #Max current value

#HMP4040_dev_1.write('INSTrument:NSELect ' + str(MPD_Channel)) # selecting the channel
#HMP4040_dev_1.write('SOURce:VOLTage ' + str(MPD_bias)) # setting the voltage value
#print('Channel-' + str(MPD_Channel) + ' voltage is set at ' + str(MPD_bias) + ' V')
#HMP4040_dev_1.write('SOURce:CURRent ' + str(MPD_current)) # setting the current value
#print('Channel-' + str(MPD_Channel) + ' current is set at ' + str(MPD_current) + ' Amp')
#HMP4040_dev_1.write('OUTPut:SELect 1') # This turn on the selected channel

####
#%%

#HMP4040_dev_1.write('OUTPut:STATe 1')
#time.sleep(2)
#print('channel-1 voltage reading is ' + HMP4040_dev_1.query('MEAS:VOLT?') + ' V') # actual voltage and current reading
#print('channel-1 current reading is ' + HMP4040_dev_1.query('MEAS:CURR?') + ' A')

#HMP4040_dev_1.write('OUTPut:GENeral 0')



# %%
