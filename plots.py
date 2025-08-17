#%%Libraries generally used
import matplotlib.pyplot as plt
import pyvisa as visa
import numpy as np
import h5py

#%%
hfr = h5py.File(f'WLT_AD09_200mA_Toptica_Wavelength_Sweep_FA_10Channel_24_03.h5', 'r')
Wavelength = np.array(hfr.get('Wlength'))
Input_power = np.array(hfr.get('Pinput'))
Output_power = np.array(hfr.get('Poutput'))
hfr.close()

GC_Loss = (10 * np.log10(10**(Input_power/10) * 0.01) - Output_power)/2

#%%
hfr = h5py.File(f'WLT_AD09_200mA_Toptica_Wavelength_Sweep_Input-1_I1_24_03.h5', 'r')
Wavelength = np.array(hfr.get('Wlength'))
Input_power_I1 = np.array(hfr.get('Pinput'))
Output_power_I1 = np.array(hfr.get('Poutput'))
hfr.close()

DL1 = (Input_power_I1 - Output_power_I1)
DL_I1 = DL1 - (2*GC_Loss)

#%%
hfr = h5py.File(f'WLT_AD09_200mA_Toptica_Wavelength_Sweep_Input-1_I2_24_03.h5', 'r')
Wavelength = np.array(hfr.get('Wlength'))
Input_power_I2 = np.array(hfr.get('Pinput'))
Output_power_I2 = np.array(hfr.get('Poutput'))
hfr.close()

DL2 = (Input_power_I2 - Output_power_I2)
DL_I2 = DL2 - (2*GC_Loss)

#%%
hfr = h5py.File(f'WLT_AD09_200mA_Toptica_Wavelength_Sweep_Input-1_Q1_24_03.h5', 'r')
Wavelength = np.array(hfr.get('Wlength'))
Input_power_Q1 = np.array(hfr.get('Pinput'))
Output_power_Q1 = np.array(hfr.get('Poutput'))
hfr.close()

DL3 = (Input_power_Q1 - Output_power_Q1)
DL_Q1 = DL3 - (2*GC_Loss)

#%%
hfr = h5py.File(f'WLT_AD09_200mA_Toptica_Wavelength_Sweep_Input-1_Q2_24_03.h5', 'r')
Wavelength = np.array(hfr.get('Wlength'))
Input_power_Q2 = np.array(hfr.get('Pinput'))
Output_power_Q2 = np.array(hfr.get('Poutput'))
hfr.close()

DL4 = (Input_power_Q2 - Output_power_Q2)
DL_Q2 = DL4 - (2*GC_Loss)