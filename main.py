#%%
import pyvisa
import csv
import matplotlib.pyplot as plt
import h5py
import numpy as np

#%%
# Connect to the SSA3075X
rm = pyvisa.ResourceManager()
instr = rm.open_resource('TCPIP0::192.168.2.30::INSTR')  # Replace with your instrument's address

#%%
# Query sweep configuration
start_freq = float((instr.query(':FREQ:START?')))
stop_freq = float((instr.query(':FREQ:STOP?')))
points = int(instr.query(':SWE:POIN?'))

# Calculate frequencies manually
freq_step = (stop_freq - start_freq) / (points - 1)
frequencies = [(start_freq + i * freq_step)/ 1e6 for i in range(points)]

# Retrieve amplitude data
amplitudes = instr.query(':TRACE:DATA?').strip().split(',')
amplitudes = [float(amp) for amp in amplitudes]  # Convert to float

#%%
#Save to .h5 file
with h5py.File('ESA_Trace_1.h5', 'w') as hf:
    hf.create_dataset('freq', data=frequencies)
    hf.create_dataset('amp', data=amplitudes)

    hf.close()


#%%
# Read .h5 file
with h5py.File('ESA_Trace_1.h5', 'r') as hfr:
    F = np.array(hfr['freq'])
    A = np.array(hfr['amp'])

    hfr.close()

#%%
# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(F, A, label="Trace Data")
#plt.axhline(y=-37.30, color='r', linestyle = '--')
plt.title("Frequency vs Amplitude")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Amplitude (dBm)")
#plt.xlim(1,50)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


#%%
# Close the connection
instr.close()

#%% For envelope
from scipy.signal import hilbert, butter, filtfilt

signal = A
t = F
def lowpass_filter(data, cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

# Generate a sample signal
fs = 1000  # Sampling frequency (Hz)
t = np.linspace(0, 200, fs * 2, endpoint=False)  # Time array (200 seconds)
carrier = np.sin(2 * np.pi * 5 * t)  # Base sine wave
modulator = 1 + 0.5 * np.sin(2 * np.pi * 0.1 * t)  # Amplitude modulation
signal = carrier * modulator

# Remove DC component from the signal (optional)
signal = signal - np.mean(signal)

# Compute the Hilbert transform to get the analytic signal
analytic_signal = hilbert(signal)
envelope = np.abs(analytic_signal)

# Smooth the envelope using a low-pass filter
cutoff_frequency = 2  # Cutoff frequency for smoothing the envelope
smoothed_envelope = lowpass_filter(envelope, cutoff_frequency, fs)

# Normalize the envelope to match the signal's amplitude
normalized_envelope = smoothed_envelope * (np.max(signal) / np.max(smoothed_envelope))

# Plot the original signal and the envelope
plt.figure(figsize=(10, 6))
plt.plot(t, signal, label="Signal")
plt.plot(t, normalized_envelope, label="Smoothed Envelope", linestyle="--", color="orange")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.title("Signal and Corrected Envelope")
plt.legend()
plt.grid()
plt.show()











#%%
# Save to CSV
with open('trace_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Frequency (Hz)', 'Amplitude (dBm)'])
    for freq, amp in zip(frequencies, amplitudes):
        writer.writerow([freq, amp])