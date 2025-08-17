import PyQt5

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QApplication

import serial

import qdarkstyle

class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("main.ui", self)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.RS_pow = None
        self.show()
        
    @pyqtSlot(bool)
    def on_connect_pb_toggled(self, value):
        if value:
            print("Connecting ...")
            self.connect_pb.setText("Disconnect")
            # # initializing power supply of EDFA
            comport = 3
            self.RS_pow = serial.Serial(port=f'COM{comport}', baudrate=9600,timeout=3)
            # RS_pow.read_termination = '\n'
            # RS_pow.write_termination = '\r\n'
            self.RS_pow.write(b'*IDN?\r\n')
            string=str(b''.join(self.RS_pow.readlines()))
            print('EDFA power supply: ' + string[2:-3])
        else:
            print("Disconnect ...")
            self.connect_pb.setText("Connect")
            self.RS_pow.close()
    
    @pyqtSlot(int)
    def on_comport_sb_valueChanged(self, value):
        print(f"COM set to {value}")

    @pyqtSlot(bool)
    def on_channel1_toggle_pb_toggled(self, value):
        if value:
            self.channel1_voltage_sb.setEnabled(False)
            self.channel1_current_sb.setEnabled(False)
            print("Got switched on ...")

            Channel_init = 1
            ch_bias = self.channel1_voltage_sb.value()
            ch_curr = self.channel1_current_sb.value()
            self.RS_pow.write(('INSTrument:NSELect ' + str(Channel_init) + "\r\n").encode()) # selecting the channel
            self.RS_pow.write(('SOURce:VOLTage ' + str(ch_bias) + "\r\n").encode()) # setting the voltage value
            print('Channel-' + str(Channel_init) + ' voltage is set at ' + str(ch_bias) + ' V')
            self.RS_pow.write(('SOURce:CURRent ' + str(ch_curr) + "\r\n").encode()) # setting the voltage value
            print('Channel-' + str(Channel_init) + ' current is set at ' + str(ch_curr) + ' Amp')


            #print('channel-1 voltage reading is ' + self.RS_pow.query('MEAS:VOLT?') + ' V') # actual voltage and current reading
            #print('channel-1 current reading is ' + self.RS_pow.query('MEAS:CURR?') + ' A')

            self.RS_pow.write(('OUTPut:SELect 1' + "\r\n").encode()) # This turn on the selected channel

        else:
            self.channel1_voltage_sb.setEnabled(True)
            self.channel1_current_sb.setEnabled(True)
            print("Got switched off ...")
            self.RS_pow.write(('OUTPut:SELect 0' + "\r\n").encode()) 
    
    @pyqtSlot(bool)
    def on_output_master_pb_toggled(self, value):
        if value:
            self.RS_pow.write(('OUTPut:GENeral 1' + "\r\n").encode())
            self.output_master_pb.setText("Output Master ON")
        else:
            self.RS_pow.write(('OUTPut:GENeral 0' + "\r\n").encode())
            self.output_master_pb.setText("Output Master OFF")

    @pyqtSlot(float)
    def on_channel1_voltage_sb_valueChanged(self, value):
        print(f"Voltage set to {value}")
    
    @pyqtSlot(float)
    def on_channel1_current_sb_valueChanged(self, value):
        print(f"Current set to {value}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    
    app.exec()