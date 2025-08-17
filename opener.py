import pandas as pd

# Specify the filename
filename = 'Data_20240912_1.h5'

# Read the HDF5 file into a DataFrame
df = pd.read_hdf(filename, key='data')

# Display the DataFrame
print(df)