import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Update this variable with your file identifier (without the .csv extension)
file_identifier = str(input('Input the date and file number (YYYYMMDD_XXX): '))
print('\nYour input is '+str(file_identifier),"\n")

# Construct the filename and variable name
filename = f"WaveData{file_identifier}.csv"
print('Your filename is '+str(filename),"\n\n")

# Asking the user for the number of trace data the file contains
number_of_traces = int(input('Input the number of traces in this file: ')) 
print('\nPlotting for '+str(number_of_traces), 'number of traces,\n\n')

# Read the Excel file into a df
df = pd.read_csv(filename, skiprows = 3 + number_of_traces * 24 + 1)

# Number of columns in data file
num_columns = number_of_traces*2

# Initialize a list of empty lists for each column
columns = [[] for _ in range(number_of_traces)]

# Initialize a list to store Level data
Lvl = ['A','B','C','D','E','F','G','H','I','J','K','L']

# Loop for plotting the data
for i in range(number_of_traces):
    columns[i] = 10 * np.log10(df['Level(' + str(Lvl[i])+')']/10) # converion from watts into dBM
    plt.plot(df['Wavelength(A)'], columns[i],label = "SOA Trace "+str(i+1)) # plotting
    
plt.title('OL_SOA_Optical_Spectrum') 
plt.xlabel('Wavelength(nm)')
plt.ylabel('Optical Power(dBm)')
plt.grid(True)

x = df['Wavelength(A)']
y = len(x)
start = x[0]
stop = x[y-1]
plt.xlim(start,stop) # x-axis limit

plt.minorticks_on()
plt.grid(color = 'grey', which='major', linestyle = '-', linewidth = 0.4)
plt.grid(color = 'grey', which='minor', linestyle = '-', linewidth = 0.25)
plt.legend(loc="best")
plt.show()