#%%
# Plot the data
import pandas as pd
import csv
import matplotlib.pyplot as plt
df = pd.read_csv('trace_data.csv')

# Display the contents
print(df)

#%%
frequencies = df['Frequency (Hz)']
amplitudes = df['Amplitude (dBm)']

plt.figure(figsize=(10, 6))
plt.plot(frequencies, amplitudes + 35.30 - 1, label="Trace Data")
plt.axhline(y=-3, color='r', linestyle = '--')
plt.title("Frequency vs Amplitude")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Amplitude (dBm)")
plt.xlim(1,50)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# %%
