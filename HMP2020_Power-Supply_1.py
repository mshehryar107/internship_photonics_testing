import PyQt5

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QApplication

import serial

import qdarkstyle

class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("HMP2020_Power-Supply_1.ui", self)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.RS_pow = None
        self.show()
        
    @pyqtSlot(bool)
    def on_connect_pb_toggled(self, value):
        if value:
            print("Connecting ...")
            self.connect_pb.setText("Disconnect")
            # # initializing power supply of EDFA
            comport = 5
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
    #Channel-1
    from PyQt5.QtCore import pyqtSlot

class PowerSupplyControl:
    def __init__(self, RS_pow, channel1_voltage_sb, channel1_current_sb, channel2_voltage_sb, channel2_current_sb):
        self.RS_pow = RS_pow
        self.channel1_voltage_sb = channel1_voltage_sb
        self.channel1_current_sb = channel1_current_sb
        self.channel2_voltage_sb = channel2_voltage_sb
        self.channel2_current_sb = channel2_current_sb

    @pyqtSlot(bool)
    def on_channel1_toggle_pb_toggled(self, value):
        self.toggle_channel(value, 1, self.channel1_voltage_sb, self.channel1_current_sb)

    @pyqtSlot(bool)
    def on_channel2_toggle_pb_toggled(self, value):
        self.toggle_channel(value, 2, self.channel2_voltage_sb, self.channel2_current_sb)

    def toggle_channel(self, value, channel, voltage_sb, current_sb):
        if value:
            voltage_sb.setEnabled(False)
            current_sb.setEnabled(False)
            print(f"Channel {channel} switched on ...")

            ch_bias = voltage_sb.value()
            ch_curr = current_sb.value()
            self.RS_pow.write((f'INSTrument:NSELect {channel}\r\n').encode())  # selecting the channel
            self.RS_pow.write((f'SOURce:VOLTage {ch_bias}\r\n').encode())  # setting the voltage value
            print(f'Channel-{channel} voltage is set at {ch_bias} V')
            self.RS_pow.write((f'SOURce:CURRent {ch_curr}\r\n').encode())  # setting the current value
            print(f'Channel-{channel} current is set at {ch_curr} Amp')

            self.RS_pow.write((f'OUTPut:SELect {channel}\r\n').encode())  # This turns on the selected channel
        else:
            voltage_sb.setEnabled(True)
            current_sb.setEnabled(True)
            print(f"Channel {channel} switched off ...")
            self.RS_pow.write((f'OUTPut:SELect 0\r\n').encode())

    @pyqtSlot(float)
    def on_channel1_voltage_sb_valueChanged(self, value):
        print(f"Channel 1 voltage set to {value}")

    @pyqtSlot(float)
    def on_channel1_current_sb_valueChanged(self, value):
        print(f"Channel 1 current set to {value}")

    @pyqtSlot(float)
    def on_channel2_voltage_sb_valueChanged(self, value):
        print(f"Channel 2 voltage set to {value}")

    @pyqtSlot(float)
    def on_channel2_current_sb_valueChanged(self, value):
        print(f"Channel 2 current set to {value}")


    @pyqtSlot(bool)
    def on_output_master_pb_toggled(self, value):
        if value:
            self.RS_pow.write(('OUTPut:GENeral 1' + "\r\n").encode())
            self.output_master_pb.setText("Output Master ON")
        else:
            self.RS_pow.write(('OUTPut:GENeral 0' + "\r\n").encode())
            self.output_master_pb.setText("Output Master OFF")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    
    app.exec()