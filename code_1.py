import pyvisa

def query_voltage(instrument, channel):
    """Query the voltage of the specified channel on the HMP2020."""
    command = f"INST:{channel}:VOLT?"
    try:
        voltage = instrument.query(command)
        return voltage.strip()  # Remove any extraneous whitespace
    except pyvisa.VisaIOError as e:
        print(f"Error querying voltage: {e}")
        return None

def main():
    rm = pyvisa.ResourceManager()
    try:
        # Replace 'GPIB0::10::INSTR' with your instrument's VISA address
        instrument = rm.open_resource('USB::0x0AAD::0x0117::102483::INSTR')

        # Query the voltage of channel 1
        voltage = query_voltage(instrument, 'CH1')
        if voltage is not None:
            print(f"Channel 1 Voltage: {voltage} V")
        else:
            print("Failed to query voltage.")

    except pyvisa.VisaIOError as e:
        print(f"Error communicating with the instrument: {e}")

    finally:
        if 'instrument' in locals():
            instrument.close()

if __name__ == "__main__":
    main()

