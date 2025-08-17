import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication,QMainWindow,QWidget, QPushButton, QComboBox, QLabel, QSpinBox, QDoubleSpinBox, QTextEdit, QLineEdit, QSizePolicy
from PyQt5.QtWidgets import QWidget, QApplication, QComboBox, QGridLayout, QVBoxLayout, QHBoxLayout
import serial.tools.list_ports
import pyvisa
import pyvisa as visa
import time

import qdarkstyle

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("HMP2020 Controller")
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        # Initialize Resource Manager and Connection Object
        self.rm = pyvisa.ResourceManager()
        self.instrument = None
        
        self.mo_check = False

        layout = QVBoxLayout() # Main Layout

        self.measurement_timer = QTimer()
        self.measurement_timer.timeout.connect(self.measure_current)

        ### Connect Device

        layout_serial = QHBoxLayout() # Serial Communication Ports Setup
        pb_connect = QPushButton("Connect") # Connect Button
        pb_connect.clicked.connect(self.the_pb_connect_was_clicked)

        pb_connect.setStyleSheet("""
            QPushButton {
                background-color: #3498db;   /* Button background color */
                color: white;                /* Text color */
                border-radius: 6px;         /* Rounded corners */
                font-size: 12px;             /* Font size */
                font-weight: bold;           /* Bold text */
            }
            QPushButton:hover {
                background-color: #2980b9;   /* Color on hover */
            }
        """)

        self.db_serial = QComboBox() # DropBox for Serial Communication Sources
        self.populate_serial_ports()  # Populate with available serial ports
        self.db_serial.currentIndexChanged.connect(self.the_serial_port_selected)
        

        layout_serial.addWidget(pb_connect)
        layout_serial.addWidget(self.db_serial)

        layout.addLayout(layout_serial)

        layout_disconnect = QVBoxLayout()
        pb_disconnect = QPushButton("Disconnect")
        pb_disconnect.clicked.connect(self.the_pb_disconnect_was_clicked)

        pb_disconnect.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;   /* Button background color (red) */
                color: white;                /* Text color */
                border-radius: 6px;         /* Rounded corners */
                font-size: 12px;             /* Font size */
                font-weight: bold;           /* Bold text */
            }
            QPushButton:hover {
                background-color: #c0392b;   /* Darker shade of red on hover */
            }
        """)

        layout_disconnect.addWidget(pb_disconnect)
        layout.addLayout(layout_disconnect)

        layout_connection_display = QVBoxLayout()
        self.connection_status = QTextEdit()
        self.connection_status.setAlignment(Qt.AlignCenter)
        self.connection_status.setReadOnly(True)

        # Remove fixed size and set dynamic sizing
        self.connection_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.connection_status.setMinimumHeight(35)  # Minimum height for single-line content
        self.connection_status.setMaximumHeight(100)  # Max height for multi-line content

        layout_connection_display.addWidget(self.connection_status)
        layout.addLayout(layout_connection_display)


        ### Control Voltage and Current for Channel 1

        layout_channel_1 = QHBoxLayout()

        label_channel_1 = QLabel("Channel 1")
        
        self.voltage_channel_1 = QDoubleSpinBox()
        self.voltage_channel_1.setDecimals(3)
        self.voltage_channel_1.setRange(0, 32.050) # Voltage in Volts
        self.voltage_channel_1.setSuffix(" V")
        self.voltage_channel_1.valueChanged.connect(self.update_channel_1_settings)

        self.current_channel_1 = QDoubleSpinBox() 
        self.current_channel_1.setDecimals(3)
        self.current_channel_1.setRange(0.001, 5.010) #Current in Amperes
        self.current_channel_1.setSuffix(" A")
        self.current_channel_1.valueChanged.connect(self.update_channel_1_settings)

        self.output_channel_1 = QPushButton("Output")
        self.output_channel_1.setCheckable(True)
        self.ch1 = True
        self.output_channel_1.clicked.connect(self.update_channel_1_settings)

        layout_channel_1.addWidget(label_channel_1)
        layout_channel_1.addWidget(self.voltage_channel_1)
        layout_channel_1.addWidget(self.current_channel_1)
        layout_channel_1.addWidget(self.output_channel_1)
        layout.addLayout(layout_channel_1)

        layout_channel_1_display = QHBoxLayout()
        self.channel_1_status = QLineEdit()
        #self.channel_1_status.setFixedSize(500, 70)  # Width: 400, Height: 200
        #self.connection_status.setAlignment(Qt.AlignCenter)
        self.channel_1_status.setReadOnly(True)
        measured_ch_1 = QLabel("Measured value: ")
        layout_channel_1_display.addWidget(measured_ch_1)
        layout_channel_1_display.addWidget(self.channel_1_status)
        layout.addLayout(layout_channel_1_display)


        

        ### Control Voltage and Current for Channel 2

        layout_channel_2 = QHBoxLayout()

        label_channel_2 = QLabel("Channel 2")
        
        self.voltage_channel_2 = QDoubleSpinBox()
        self.voltage_channel_2.setDecimals(3)
        self.voltage_channel_2.setRange(0, 32.050) # Voltage in Volts
        self.voltage_channel_2.setSuffix(" V")
        self.voltage_channel_2.valueChanged.connect(self.update_channel_2_settings)

        self.current_channel_2 = QDoubleSpinBox() 
        self.current_channel_2.setDecimals(3)
        self.current_channel_2.setRange(0.0005, 2.510) #Current in Amperes
        self.current_channel_2.setSuffix(" A")
        self.current_channel_2.valueChanged.connect(self.update_channel_2_settings)

        self.output_channel_2 = QPushButton("Output")
        self.output_channel_2.setCheckable(True)
        self.ch2 = True
        self.output_channel_2.clicked.connect(self.update_channel_2_settings)

        layout_channel_2.addWidget(label_channel_2)
        layout_channel_2.addWidget(self.voltage_channel_2)
        layout_channel_2.addWidget(self.current_channel_2)
        layout_channel_2.addWidget(self.output_channel_2)
        layout.addLayout(layout_channel_2)

        layout_channel_2_display = QHBoxLayout()
        self.channel_2_status = QLineEdit()
        #self.channel_1_status.setFixedSize(500, 70)  # Width: 400, Height: 200
        #self.connection_status.setAlignment(Qt.AlignCenter)
        self.channel_2_status.setReadOnly(True)
        measured_ch_2 = QLabel("Measured value: ")
        layout_channel_2_display.addWidget(measured_ch_2)
        layout_channel_2_display.addWidget(self.channel_2_status)
        layout.addLayout(layout_channel_2_display)

        ### Master Switch

        pb_master_output = QPushButton("Master Output")
        pb_master_output.setCheckable(True)
        pb_master_output.clicked.connect(self.the_pb_master_output_was_clicked)

        pb_master_output.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;   /* Button background color (green) */
                color: white;                /* Text color */
                border-radius: 10px;         /* Rounded corners */
                font-size: 18px;             /* Font size */
                font-weight: bold;           /* Bold text */
            }
            QPushButton:hover {
                background-color: #27ae60;   /* Darker shade of green on hover */
            }
        """)
        

        layout.addWidget(pb_master_output)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    ############################################################################################################################################

    def populate_serial_ports(self):
        """Populates the serial port combo box with available VISA resources."""
        resources = self.rm.list_resources()
        self.db_serial.clear()  # Clear existing items
        if resources:
            self.db_serial.addItems(resources)  # Add each VISA resource to the combo box
        else:
            self.db_serial.addItem("No resources found")  # Add a placeholder if no resources are available

    def append_message(self, message):
        """Helper function to append text to the log display."""
        self.connection_status.append(message)


    def the_serial_port_selected(self, index):
        selected_resource = self.db_serial.itemText(index)
        print(f"Resource selected: {selected_resource}")

    def the_pb_connect_was_clicked(self):
        """Attempts to connect to the selected device."""
        selected_resource = self.db_serial.currentText()
        if selected_resource and selected_resource != "No resources found":
            try:
                # Attempt to open the connection
                self.instrument = self.rm.open_resource(selected_resource)
                device = self.instrument
                device.write('OUTP:GEN OFF')
                device.write(f'INST:NSEL 1')
                device.write('OUTP OFF, (@1)')
                device.write(f'INST:NSEL 2')
                device.write('OUTP OFF, (@2)')
                # Print success message and/or handle UI updates
                print(f"Successfully connected to: {selected_resource}")
                i=0
                for i in range(2):
                    device_1 = device.query('*IDN?')
                    if i == 1:
                        print(f"The Connected Device IDN Check: {device_1}")
                        self.append_message(f"Successfully connected to: {selected_resource}\nDevice ID: {device_1}")
                i=i+1
                
                
            except Exception as e:
                # Handle connection error
                print(f"Failed to connect to {selected_resource}: {e}")
                self.append_message(f"Failed to connect to {selected_resource}: {e}")
        else:
            print("No available resources to connect.")
            self.append_message("No available resources to connect")

    def the_pb_disconnect_was_clicked(self):
        if self.instrument is not None:  # Check if the instrument is connected
            try:
                # Turn off outputs and close the connection
                device = self.instrument
                device.write('OUTP:GEN OFF')
                device.write('INST:NSEL 1')
                device.write('OUTP OFF, (@1)')
                device.write('INST:NSEL 2')
                device.write('OUTP OFF, (@2)')
                device.close()

                print(f"The Device {self.instrument} was Disconnected Successfully!")
                self.append_message(f"The Device {self.instrument} was Disconnected Successfully!\n")
            
            except Exception as e:
                print(f"Error disconnecting: {e}")
                self.append_message(f"Error disconnecting: {e}\n")
            
            finally:
                self.instrument = None  # Clear the instrument reference after disconnecting

        else:
            print("No device to disconnect.")
            self.append_message("No device to disconnect.\n")

    ##########################################################################################################################################

    def update_channel_1_settings(self):
        """Updates and prints the current settings for Channel 1, including voltage, current, and output status."""
        device = self.instrument
        command = f'INST:NSEL 1'
        device.write(command)
        i=0
        for i in range(2):
            chnl_1 = device.query('INST:NSEL?')
            if i == 1:
                print(f"Channel Selected: {chnl_1}")
        i=i+1

        voltage_ch1 = self.voltage_channel_1.value()
        current_ch1 = self.current_channel_1.value()
        

        # Set the voltage and current for Channel 1 regardless of output status
        if self.output_channel_1:
            if self.mo_check:
                device.write(f':SOUR1:VOLT {voltage_ch1}')
                device.write(f':SOUR1:CURR {current_ch1}')
                time.sleep(0.25)
            else:
                device.write('OUTP:GEN OFF')
                device.write(f':SOUR1:VOLT {voltage_ch1}')
                device.write(f':SOUR1:CURR {current_ch1}')
                device.write('OUTP:GEN OFF')
                time.sleep(0.25)
        else:
            device.write(f':SOUR1:VOLT {voltage_ch1}')
            device.write(f':SOUR1:CURR {current_ch1}')
            time.sleep(0.25)

        #meas_curr_ch1 = device.query('MEAS:CURR? (@1)')


        output_status_ch1 = "ON" if self.output_channel_1.isChecked() else "OFF"

        # Turn Channel 1 on or off based on the output status of the button
        if self.output_channel_1.isChecked():
            if self.ch1:
                #device.write('OUTP:GEN OFF')
                device.write('OUTP ON, (@1)')
                device.write('OUTP:GEN OFF')
                print(f"Channel 1 - Voltage: {voltage_ch1} V, Current: {current_ch1} A, Output: ON")
                self.ch1 = False
            else: 
                #device.write('OUTP:GEN OFF')
                device.write('OUTP ON, (@1)')
                #device.write('OUTP:GEN OFF')
                print(f"Channel 1 - Voltage: {voltage_ch1} V, Current: {current_ch1} A, Output: ON")
        else:
            device.write('OUTP OFF, (@1)')
            print(f"Channel 1 - Voltage: {voltage_ch1} V, Current: {current_ch1} A, Output: OFF")
            self.ch1 = True

        

        

    #########################################################################################################################################

    def update_channel_2_settings(self):
        #"""Updates and prints the current settings for Channel 2, including voltage, current, and output status."""
        device_2 = self.instrument
        command = f'INST:NSEL 2'
        device_2.write(command)
        i=0
        for i in range(2):
            chnl_2 = device_2.query('INST:NSEL?')
            if i == 1:
                print(f"Channel Selected: {chnl_2}")
        i=i+1
        
        voltage_ch2 = self.voltage_channel_2.value()
        current_ch2 = self.current_channel_2.value()
        
        # Set the voltage and current for Channel 2 regardless of output status
        device_2.write(f':SOUR2:VOLT {voltage_ch2}')
        device_2.write(f':SOUR2:CURR {current_ch2}')
        time.sleep(0.25)
        
        output_status_ch2 = "ON" if self.output_channel_2.isChecked() else "OFF"

        # Turn Channel 2 on or off based on the output status of the button
        if self.output_channel_2.isChecked():
            if self.ch2:
                #device_2.write('OUTP:GEN OFF')
                device_2.write('OUTP ON, (@2)')
                device_2.write('OUTP:GEN OFF')
                print(f"Channel 2 - Voltage: {voltage_ch2} V, Current: {current_ch2} A, Output: ON")
                self.ch2 = False
            else:
                #device_2.write('OUTP:GEN OFF')
                device_2.write('OUTP ON, (@2)')
                #device_2.write('OUTP:GEN OFF')
                print(f"Channel 2 - Voltage: {voltage_ch2} V, Current: {current_ch2} A, Output: ON")
        else:
            device_2.write('OUTP OFF, (@2)')
            print(f"Channel 2 - Voltage: {voltage_ch2} V, Current: {current_ch2} A, Output: OFF")
            self.ch2 = True
    
    def the_pb_master_output_was_clicked(self, checked):

        device = self.instrument
        if checked:
            device.write('OUTP:GEN ON')
            self.mo_check = True
            print('Output activated!')
            self.measurement_timer.start(100)  # Measure every 1/10 second

            # Change color to active state (e.g., bright green)
            self.sender().setStyleSheet("""
                QPushButton {
                    background-color: #1abc9c;   /* Lighter green to indicate ON */
                    color: white;
                    border-radius: 10px;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #16a085;   /* Darker green on hover when ON */
                }
            """)
        else:
            device.write('OUTP:GEN OFF')
            self.mo_check = False
            print('Output disconnected!')
            self.measurement_timer.stop()  # Stop measurement

            # Revert color to default state (original green color)
            self.sender().setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;   /* Default green color */
                    color: white;
                    border-radius: 10px;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #27ae60;   /* Darker green on hover when OFF */
                }
            """) 

    def measure_current(self):
        """Measure and update the current for Channel 1 and Channel 2 if master output is on."""
        device = self.instrument
        try:
            # Measure current for Channel 1
            i=0
            for i in range(2):
                device.write(f'INST:NSEL 1')
                measured_current = device.query('MEAS:CURR? (@1)')
                if i == 1:
                    print(measured_current)
                    self.channel_1_status.setText(f'{measured_current} A')
            i=i+1


            # Measure current for Channel 2
            j=0
            for j in range(2):
                device.write(f'INST:NSEL 2')
                measured_current_ch2 = device.query('MEAS:CURR? (@2)')
                if j == 1:
                    print(measured_current_ch2)
                    self.channel_2_status.setText(f'{measured_current_ch2} A')
            j=j+1

        except Exception as e:
            print(f"Error measuring current: {e}")


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()