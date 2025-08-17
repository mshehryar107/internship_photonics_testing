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

#%% Filepath and Naming
data_path = "your_directory_path"
file_name = "your file_name"
title_plot_1 = "your plot 1 title"
title_plot_2 = "your plot 2 title"
name_fig_1 = "your figure 1 name"
name_fig_2 = "your figure 2 name"

#%%
#To check the device list conneceted
rm = visa.ResourceManager()
rm.list_resources()

#%%Connecting Power Meter PM100D for Output Optical Power Measurement
#To communicate with thorlabs power meter
ThorPM = rm.open_resource('USB0::0x1313::0x8078::P0032715::INSTR')
ThorPM.query('*IDN?')
ThorPM.write('SENS:POW:AUTO ON')
ThorPM.write('SENS:POW:UNIT W')
ThorPM.write('CORR:WAV 1550 nm')
P = float(ThorPM.query('READ?'))
print('Power (mW)',P*1e3)

#%% Connecting Power Meter PM100 for Back Reflected Optical Power Measurement
#To communicate with thorlabs power meter
ThorPM_in = rm.open_resource('USB0::0x1313::0x8072::1922312::INSTR')
ThorPM_in.query('*IDN?')
ThorPM_in.write('SENS:POW:AUTO ON')
ThorPM_in.write('SENS:POW:UNIT W')
ThorPM_in.write('CORR:WAV 1550 nm')
P_1 = float(ThorPM_in.query('READ?'))
print('Power (mW)',P_1*1e3)

#%% Setting Attenuation Range 
# Set the attenuation sweep parameters
start_attenuation = 0  # Starting attenuation in dB
end_attenuation = 25  # Ending attenuation in dB
step_size = 1        # Step size for attenuation sweep in dB
Attenuation_range=np.arange(start_attenuation, end_attenuation + step_size, step_size)
#to communicate to the VOA
attenuator = rm.open_resource('ASRL3::INSTR',)
attenuator.write('A'+str(Attenuation_range[0]))
time.sleep(10)

#%% Data Arrays
Out_OP = np.zeros(np.size(Attenuation_range))
Out_OP_dBm = np.zeros(np.size(Attenuation_range))

IN_OP_R = np.zeros(np.size(Attenuation_range))
IN_OP_R_dBm = np.zeros(np.size(Attenuation_range))

# Input the initial input power
IN_P_dBm = -5 - Attenuation_range

#%% Input Optical Power Attenuation Loop
for i in range(np.size(Attenuation_range)):
    print('Optical Attenuation '+str(Attenuation_range[i])+ ' dB')
    attenuator.write('A'+str(Attenuation_range[i]))
    time.sleep(2.5)
    IN_OP_R[i] = float(ThorPM_in.query('READ?'))*1e3
    print('Power meter (mW)',IN_OP_R[i])
    IN_OP_R_dBm[i]=np.log10(IN_OP_R[i])*10   
    print('Output Optical Power is '+str(IN_OP_R_dBm[i])+' dBm')
    Out_OP[i] = float(ThorPM.query('READ?'))*1e3
    print('Power meter (mW)',Out_OP[i])
    Out_OP_dBm[i]=np.log10(Out_OP[i])*10   
    print('Output Optical Power is '+str(Out_OP_dBm[i])+' dBm')
    time.sleep(0.5)

#%% Write_File
hf = h5py.File(f'{data_path}\{file_name}.h5', 'w')
hf.create_dataset('Att_range', data=Attenuation_range)
hf.create_dataset('opt_power',data=Out_OP)
hf.create_dataset('opt_power_dBm',data=Out_OP_dBm)
hf.create_dataset('ref_power',data=IN_OP_R)
hf.create_dataset('ref_power_dBm',data=IN_OP_R_dBm)
hf.create_dataset('inp_power_dBm', data=IN_P_dBm)
hf.close()

#%% Read_File
hfr = h5py.File(f'{data_path}\{file_name}.h5', 'r')
AR=np.array(hfr.get('Att_range'))
opt_pow = np.array(hfr.get('opt_power'))
opt_pow_dBm = np.array(hfr.get('opt_power_dBm'))
ref_pow = np.array(hfr.get('ref_power'))
ref_pow_dBm = np.array(hfr.get('ref_power_dBm'))
inp_pow_dBm = np.array(hfr.get('inp_power_dBm'))
hfr.close()

#%% Output Optical Power and Reflected Optical Power vs Input Optical Power Plot 
fig, ax = plt.subplots()
twin1 = ax.twinx()

# Offset the right spine of twin2.  The ticks and label have already been
# placed on the right by twinx above.
p1, = ax.plot(inp_pow_dBm, opt_pow_dBm, ":bo", label="Output Optical Power")
p2, = twin1.plot(inp_pow_dBm, ref_pow_dBm, ":ro", label="Reflected Optical Power")

# Set limits for the plot
#ax.set_xlim(-5, 185)
#ax.set_ylim(-60, 35)
#twin1.set_ylim(-60, 35)

ax.set_xlabel("Number of Measurements", fontsize = 14)
ax.set_ylabel("Output Optical Power (dBm)", fontsize = 14)
twin1.set_ylabel("Reflected Optical Power (dBm)", fontsize = 14)
ax.yaxis.label.set_color(p1.get_color())
twin1.yaxis.label.set_color(p2.get_color())

tkw = dict(size=4, width=1.5)
ax.tick_params(axis='y', colors=p1.get_color(), **tkw)
twin1.tick_params(axis='y', colors=p2.get_color(), **tkw)
ax.tick_params(axis='x', **tkw)
#ax.xaxis.set_minor_locator(MultipleLocator(10))
#ax.yaxis.set_minor_locator(MultipleLocator(5))
ax.minorticks_on()
ax.yaxis.grid(color = 'grey', which='major', linestyle = '-', linewidth = 0.5)
ax.xaxis.grid(color = 'grey', which='major', linestyle = '-', linewidth = 0.5)
ax.yaxis.grid(color = 'grey', which='minor', linestyle = '--', linewidth = 0.35)
ax.xaxis.grid(color = 'grey', which='minor', linestyle = '--', linewidth = 0.35)
#ax.grid(color = 'grey', which='minor', linestyle = '--', linewidth = 0.5)
ax.legend(handles=[p1, p2], bbox_to_anchor=(0.45,0.95))
ax.set_title(title_plot_1)
plt.savefig(name_fig_1+'.png',dpi=300)
plt.show()

#%% Gain Plot
gain = opt_pow_dBm-inp_pow_dBm
plt.plot(opt_pow_dBm, gain, ":bo")

# Set axis limits
#plt.xlim(-12,5)
#plt.ylim(11,13)

plt.title(title_plot_2)
plt.xlabel("Output Optical Power (dBm)", fontsize = 14)
plt.ylabel("Optical Gain (dB)", fontsize = 14)

plt.minorticks_on()
plt.gca().yaxis.label.set_color('b')
plt.grid(color='grey', which='major', linestyle='-', linewidth=0.5)
plt.grid(color='grey', which='minor', linestyle='--', linewidth=0.35)
tkw = dict(size=4, width=1.5)
plt.tick_params(axis='y', colors='b', **tkw)
plt.tick_params(axis='x', **tkw)
plt.savefig(name_fig_2+'.png',dpi=300)

plt.show()
#%% Close Connections
ThorPM.close()
ThorPM_in.close()
attenuator.close()

#%% End
