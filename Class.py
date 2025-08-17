import pyvisa

# Initialize the VISA resource manager
rm = pyvisa.ResourceManager()

# Connect to the power supply (update the address as per your connection)
# The address can be something like 'USB0::0x0AAD::0x0054::123456::INSTR'
# Use rm.list_resources() to find the correct address if needed.
instrument = rm.open_resource('USB::0x0AAD::0x0117::102483::INSTR')

# Function to set voltage on a specified channel
def set_voltage(channel, voltage):
    command = f'VOLT {voltage},{channel}'
    instrument.write(command)
    print(f"Set voltage to {voltage} V on channel {channel}")

# Function to set current on a specified channel
def set_current(channel, current):
    command = f'CURR {current},{channel}'
    instrument.write(command)
    print(f"Set current limit to {current} A on channel {channel}")

# Function to turn output on or off for a specified channel
def output_control(channel, state):
    command = f'OUTP {state},{channel}'
    instrument.write(command)
    print(f"Output on channel {channel} turned {state}")

# Function to measure voltage on a specified channel
def measure_voltage(channel):
    command = f'MEAS:VOLT?,{channel}'
    voltage = instrument.query(command)
    print(f"Measured voltage on channel {channel}: {voltage} V")
    return float(voltage)

# Function to measure current on a specified channel
def measure_current(channel):
    command = f'MEAS:CURR?,{channel}'
    current = instrument.query(command)
    print(f"Measured current on channel {channel}: {current} A")
    return float(current)

# Function to set over-voltage protection
def set_ovp(channel, voltage):
    command = f'VOLT:PROT {voltage},{channel}'
    instrument.write(command)
    print(f"Set over-voltage protection to {voltage} V on channel {channel}")

# Function to reset the instrument
def reset_instrument():
    instrument.write('*RST')
    print("Instrument reset to default settings")

# Function to query the instrument's identity
def query_identity():
    idn = instrument.query('*IDN?')
    print(f"Instrument identification: {idn}")
    return idn

# Example usage of the functions
if __name__ == "__main__":
    # Query the instrument identity
    #query_identity()

    # Reset the instrument
    #reset_instrument()

    # Set voltage and current on channel 1
    set_voltage(channel=1, voltage=5)
    set_current(channel=1, current=3)

    # Turn on the output for channel 1
    output_control(channel=1, state='ON')

    # Measure voltage and current on channel 1
    measure_voltage(channel=1)
    measure_current(channel=1)

    # Set over-voltage protection
    set_ovp(channel=1, voltage=5.5)

    # Turn off the output for channel 1
    output_control(channel=1, state='OFF')

    # Close the connection to the instrument
    instrument.close()
