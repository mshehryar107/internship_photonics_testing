#Laser test 'Openlight'
# -*- coding: utf-8 -*-


#%%
#Importing all required modules
##If something is missing and needs to be added please add here##
import matplotlib.pyplot as plt
import pyvisa as visa
import numpy as np
import time
import math
import serial
from pyvisa import ResourceManager
from TLPM import TLPM
import h5py
from datetime import datetime
from ctypes import c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int16,c_double
import scipy.io
#from drivers import Laser

import os
import sys
from scipy import signal
from koheron import connect, command

#from plyer import notification
import requests

#%%
#To check the device list conneceted
rm = visa.ResourceManager()
rm.list_resources()

#%%
#The function defined for Phase Noise
def PhaseNoise():
    class PhaseNoiseAnalyzer(object):
        def __init__(self, client):
            self.client = client
            self.calib_factor = 4.196
            self.npts = 200000
    
        @command(classname="Dds")
        def set_dds_freq(self, channel, freq):
            pass
    
        @command(classname="ClockGenerator")
        def set_reference_clock(self, val):
            pass
    
        @command()
        def set_cic_rate(self, rate):
            self.fs = 200E6 / (2.0 * rate)
    
        @command()
        def set_channel(self, channel):
            pass
    
        @command()
        def get_carrier_power(self, navg):
            return self.client.recv_float()
    
        @command()
        def get_data(self):
            return self.client.recv_array(self.npts, dtype='int32')
    
        @command()
        def get_phase(self):
            return self.client.recv_array(self.npts, dtype='float32')
    
        def phase_noise(self, navg=1, window='hann', verbose=False):
            win = signal.get_window(window, Nx=self.npts)
            f = np.arange((self.npts // 2 + 1)) * self.fs / self.npts
            psd = np.zeros(f.size)
    
            power = 0
    
            for i in range(navg):
                # if verbose:
                    # print("Acquiring sample {}/{}".format(i + 1, navg))
    
                phase = self.get_phase()
                psd += 2.0 * np.abs(np.fft.rfft(win * (phase - np.mean(phase)))) ** 2
                power += self.get_carrier_power(40)
    
            print(power / navg)
    
            psd /= navg
            psd /= (self.fs * np.sum(win ** 2)) # rad^2/Hz
    
            # Divide by 2 because phase noise in dBc/Hz is defined as L = S_phi / 2 
            # https://en.wikipedia.org/wiki/Phase_noise
            psd_dB = 10.0 * np.log10(psd / 2.0) # dBc/Hz
            return f, psd_dB
    
    
        def frequency_noise(self, navg=1, window='hann', verbose=False):
            f, psd_dB = self.phase_noise(navg, window, verbose)
            psd_freq = psd_dB + 3.0 + 20.0 * np.log10(f)
            return f, psd_freq
    
    host = os.getenv('HOST','192.168.2.200')
    freq = 80e6
    cic_rate = 20
    channel = 0
    
    driver = PhaseNoiseAnalyzer(connect(host, 'phase-noise-analyzer'))
    driver.set_reference_clock(0)
    driver.set_dds_freq(channel, freq)
    driver.set_cic_rate(cic_rate)
    driver.set_channel(channel)
    
    # f, psd_freq = driver.phase_noise(navg=100, verbose=True)
    
    f, psd_freq = driver.phase_noise(navg=100, verbose=True)
    # dataw = np.transpose([f,psd_freq])
    return np.transpose(f), np.transpose(psd_freq) 
    # fname = 'test_24102023'#20230927_80MHz_nolocking_Eblana_PI200_P4I6_0mVLO_2'
    # np.savetxt(fname+'.txt',np.transpose([f,psd_freq]),delimiter='\t')


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
OSA_dev_1.write('MPT 2001')
num_samp_pts = OSA_dev_1.query('MPT?')
print('Sampling points: ' + num_samp_pts)

wlen_axis = np.linspace(float(strt_wlen),float(end_wlen),int(num_samp_pts))
tt = time.time()

OSA_dev_1.write('SSI')
waitCompletion(OSA_dev_1)

OSA_dev_1.write('PKS PEAK')
time.sleep(1)

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
ThorPM = rm.open_resource('USB0::0x1313::0x807B::220920309::INSTR')
ThorPM.query('*IDN?')
ThorPM.write('SENS:POW:AUTO ON')
ThorPM.write('SENS:POW:UNIT W')
ThorPM.write('CORR:WAV 1550 nm')
P = float(ThorPM.query('READ?'))*1E+3
print('Power (mW)',P)
#%%
#To communicate with Koheron Driver and set the gain medium current
Koheron_LD = serial.Serial(port='COM8',baudrate=115200,timeout=1)
Koheron_LD.write_termination='\r\n'
Koheron_LD.read_termination='\r\n'

#%%
Koheron_LD.write(b'ilaser 1 80\r\n')
print(Koheron_LD.readlines())
Koheron_LD.write(b'vmon 1\r\n')
vv = str(b''.join(Koheron_LD.readlines()))
laser_1_voltage = float((vv[12:17]))
print(Koheron_LD.readlines())
print('Drawn laser volatge (V)',laser_1_voltage)

Koheron_LD.write(b'ilaser 2 0\r\n')
print(Koheron_LD.readlines())
Koheron_LD.write(b'vmon 2\r\n')
vv = str(b''.join(Koheron_LD.readlines()))
laser_2_voltage = float((vv[12:17]))
print(Koheron_LD.readlines())
print('Drawn laser volatge (V)',laser_2_voltage)

Koheron_LD.write(b'ilaser 3 0\r\n')
print(Koheron_LD.readlines())
Koheron_LD.write(b'vmon 3\r\n')
vv = str(b''.join(Koheron_LD.readlines()))
laser_3_voltage = float((vv[12:17]))
print(Koheron_LD.readlines())
print('Drawn laser volatge (V)',laser_3_voltage)


Koheron_LD.write(b'ilaser 4 0\r\n')
print(Koheron_LD.readlines())
Koheron_LD.write(b'vmon 4\r\n')
vv = str(b''.join(Koheron_LD.readlines()))
laser_4_voltage = float((vv[12:17]))
print(Koheron_LD.readlines())
print('Drawn laser volatge (V)',laser_4_voltage)

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
# iring0 = np.arange(0,50.1,0.25)
# Koheron_LD.write(b'imon 3\r\n')
# print(Koheron_LD.readlines())

# #Ring-1, laser-3
# iring1 = np.arange(0,50,0.25)
# Koheron_LD.write(b'imon 4\r\n')
# print(Koheron_LD.readlines())

#%%
#%% Connect to Temperature Controller (Thorlabs ITC4001)
# Initializing the temperature controller
ITC4001_addr = 'USB0::0x1313::0x804A::M00752785::INSTR'
ITC4001_dev = rm.open_resource(ITC4001_addr)
print('Temperature Controller: ' + str(ITC4001_dev.query('*IDN?')))

# Set temperature
Set_temp = 20 #Enter the temperature in degree C (20-80): '))
ITC4001_dev.write('SOUR2:TEMP ' + str(Set_temp))
ITC4001_dev.write('OUTP2 1')  # Turn on TEC
print('Temperature set. Please wait...')
time.sleep(10)
print('Current temperature: ' + ITC4001_dev.query('MEAS:TEMP?') + ' °C')

#%%
Set_temp_range = [25,35,40,50,60]

#%%
Pring0 = np.arange(0,102.5*1E-3,2.5*1E-3)
Pring1 = np.arange(0,102.5*1E-3,2.5*1E-3)

res0 = 37.5
res1 = 35.6

iring0 = (Pring0/ res0)**0.5*1E+3
Koheron_LD.write(b'imon 3\r\n')
print(Koheron_LD.readlines())

iring1 = (Pring1/ res1)**0.5*1E+3
Koheron_LD.write(b'imon 4\r\n')
print(Koheron_LD.readlines())

#%%
iring0 = np.arange(0,50,2.5)
iring1 = np.arange(0,50,2.5)

#%%
N = 10001
Nn = 100001
#Set_temp = 35 #Enter the temperature you want to set initially
Devn = 16
OL = Devn
ilas = 100
f0 = 20.020E6 # First minima
tau = 1/f0
c = 299792458
n = 1.45
L = c*tau/n
# tau = L*n/c
print('Delay (m)',L)

power_meter = np.zeros((np.size(iring0), np.size(iring1)))
ring_0_voltage = np.zeros(np.size(iring0))
ring_1_voltage = np.zeros(np.size(iring1))
ring_0_power = np.zeros(np.size(iring0))
ring_1_power = np.zeros(np.size(iring1))
MPD_power = np.zeros((np.size(iring0), np.size(iring1)))
OSA_Wavelength = np.zeros((np.size(iring0), np.size(iring1)))
SMSR = np.zeros((np.size(iring0), np.size(iring1)))
spectrum = np.zeros((np.size(iring0), np.size(iring1)))
Pnoised = np.zeros((Nn,np.size(iring0),np.size(iring1)))
lw = np.zeros((np.size(iring0), np.size(iring1)))
White_Noise = np.zeros((np.size(iring0), np.size(iring1)))
time.sleep(1)


#%%
for j in range(np.size(Set_temp_range)):

    ITC4001_dev.write('SOUR2:TEMP ' + str(Set_temp_range[j]))
    print('Temperature set. Please wait...')
    time.sleep(120)
    print('Current temperature: ' + ITC4001_dev.query('MEAS:TEMP?') + ' °C')

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
            MPD_power[(i,j)] = (float(SMU.query(":MEAS:CURR?"))*-1)*94000/6
            print('Monitor PD Power (mW)',MPD_power[(i,j)])
            #Now the OSA spectrums
            time.sleep(0.10)
            OSA_dev_1.write('MPT 2001')
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
            print('Wavelength mkr: ', str(mkr_wlen), 'nm')
            print('Power mkr: ', str(mkr_pow), 'dBm')
            OSA_Wavelength[(i,j)] = float(mkr_wlen)
            time.sleep(0.25)
            OSA_dev_1.write(':CALCulate:CATegory SMSR')
            smsr = OSA_dev_1.query(':CALC:DATA?')
            SMSR[(i,j)] = float(smsr[18:23])*10
            print('SMSR is '+str(SMSR[(i,j)]))
            #Pnoisef, Pnoised[:,i,j] = PhaseNoise()
            #linewidth measurement part
            # freq = Pnoisef
            # psd_dBc = Pnoised[:,i,j] #- 20.0*np.log10(2.0*np.sin(np.pi*f*tau))
            # fact = 1#((8192.0/(4.196*np.pi))**2)
            # psd_phase = 2*np.power(10,psd_dBc*0.1)*fact
            # SFf = np.power(freq,2)*psd_phase*np.pi/((2*np.sin(np.pi*freq*tau))**2)
            # White_Noise[(i,j)] = np.mean(SFf[50000:60000])
            # lw[(i,j)] = np.mean(SFf[50000:60000])/1E+6
            # print('The linewidth is '+str(lw[(i,j)]*1E+3)+' kHz')
            # time.sleep(0.25)
    time.sleep(0.25)
    print(f'Sweep at {Set_temp_range[j]} is complete')

    # Saving data at each set temperature
    hf = h5py.File(f'OL_TRL_019A_{Set_temp_range[j]}C_80mA_Ring_Sweep_02_12_2024.h5','w')
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
    # hf.create_dataset('Pnoised',data=Pnoised)
    # hf.create_dataset('Pnoisef',data=Pnoisef)
    hf.create_dataset('SP',data=spectrum)
    # hf.create_dataset('Linewidth',data=lw)
    hf.close()



#%%
#To save all the data files
OL=16
Sweep=1
hf = h5py.File('OL_TRL_020A_35C_80mA_Ring_Sweep_19_11_2024.h5','w')
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
# hf.create_dataset('Pnoised',data=Pnoised)
# hf.create_dataset('Pnoisef',data=Pnoisef)
hf.create_dataset('SP',data=spectrum)
# hf.create_dataset('Linewidth',data=lw)
hf.close()

#%%
Koheron_LD.write(b'ilaser 1 0\r\n')
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
hfr = h5py.File('OL_TRL_020A_35C_80mA_Ring_Sweep_19_11_2024.h5','r')

Current_0 = np.array(hfr.get('Iring0'))
Current_1 = np.array(hfr.get('Iring1'))
Voltage_0 = np.array(hfr.get('ring_0_voltage'))
Voltage_1 = np.array(hfr.get('ring_1_voltage'))
R_Power_0 = np.array(hfr.get('Pring0'))
R_Power_1 = np.array(hfr.get('Pring1'))
power_onchip = np.array(hfr.get('MPDPower'))
power_out = np.array(hfr.get('PowThf'))
wavelength = np.array(hfr.get('Wavelength'))
smsr_1 = np.array(hfr.get('Sidemode'))
# lw1 = np.array(hfr.get('Linewidth'))
hfr.close()

#To make the countour plot
#%%
#plt.contourf(R_Power_0, R_Power_1, wavelength, 20, cmap='RdGy')
plt.figure()
plt.contourf(R_Power_0, R_Power_1, wavelength,100)
plt.colorbar()
plt.xlabel('Ring-0 Heater Power (mW)')
plt.ylabel('Ring-1 Heater Power (mW)')
plt.title('OL TRL 020A 35C 80mA Operating Wavelength (nm)')
plt.savefig('OL_TRL_020A_35C_80mA_Operating_Wavelength.png',dpi=300)
plt.show()

#%%
#plt.contourf(R_Power_0, R_Power_1, power_onchip, 20, cmap='RdGy')
plt.figure()
plt.contourf(R_Power_0, R_Power_1, power_out,100)
plt.colorbar()
plt.xlabel('Ring-0 Heater Power (mW)')
plt.ylabel('Ring-1 Heater Power (mW)')
plt.title('OL TRL 020A 35C 80mA Outout Opitcal Power (mW)')
plt.savefig('OL_TRL_020A_35C_80mA_Optical_Power.png',dpi=300)
plt.show()

#%%
#plt.contourf(R_Power_0, R_Power_1, smsr_1, 20, cmap='RdGy')
plt.figure()
plt.contourf(R_Power_0, R_Power_1, smsr_1, 100)
plt.colorbar()
plt.xlabel('Ring-0 Heater Power (mW)')
plt.ylabel('Ring-1 Heater Power (mW)')
plt.title('OL TRL 35C 020A 80mA Side mode supression ratio (dB)')
plt.savefig('OL_TRL_020A_35C_80mA_SMSR.png',dpi=300)
plt.show()

#plt.contourf(R_Power_0, R_Power_1, smsr_1, 20, cmap='RdGy')
# plt.figure()
# plt.contourf(R_Power_0, R_Power_1, lw1, 100)
# plt.colorbar()
# plt.xlabel('Ring-0 Heater Power (mW)')
# plt.ylabel('Ring-1 Heater Power (mW)')
# plt.title('OL TRL 25C 50mA Linewidth (kHz)')
# #plt.savefig('OL_TRL_25C_50mA_Linewidth.png',dpi=300)
# plt.show()

