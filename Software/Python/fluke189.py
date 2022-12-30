# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 15:06:14 2021
@author: Vojtech Vrba (vrba.vojtech@gmail.com)

USB-UART-IR Commands for FLUKE 189 True RMS Multimeter
Required python dependency: pyserial
Working baudrate: 9600 bps

Working commands:
    - DS (Default Setup)
    - ID (Identification) - response: FLUKE 189, V2.02,0084750006<\r>
    - PS (Program Setup) - ???
    - QM (Query Measurement) - responds with current measurement
    - QS (Query Setup) - responds with setup?
    - RI (Reset Instrument) - resets instrument
"""

import serial

class Fluke189:
    def __init__(self, port):
        self.port = port
        self.com = None
    
    def connect(self):
        if not self.com:
            try:
                self.com = serial.Serial(self.port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
                print("Success: Connected to serial COM port", self.com.name)
            except serial.SerialException as e:
                print("Error:", e)
        else:
            print("Error: Serial COM port already connected")
    
    def disconnect(self):
        if self.com:
            self.com.close()
            self.com = None
            print("Success: Serial COM port disconnected")
        else:
            print("Error: Serial COM port already disconnected")
            
    def send_command(self, cmd):
        if self.com:
            self.com.write(str.encode(cmd) + b'\r')
            parts = self.com.readline().decode().split("\r")
            if parts[0] != cmd:
                print("Error: No echo on RX, maybe the adapter is not connected to the multimeter?")
                return
            if len(parts[1]) == 0:
                print("Error: No status response, maybe multimeter is offline?")
                return
            if int(parts[1]) == 0:
                if len(parts[2]) > 0:
                    return parts[2]
                else:
                    return
            else:
                print("Error: Unknown command", cmd)
                return
        else:
            print("Error: Serial COM port is disconnected")
    
    def reset_instrument(self):
        self.send_command("RI")
    
    def identification(self):
        return self.send_command("ID")
    
    def query_measurement(self):
        """
        Query measurement from the multimeter.
        When wrong mode is selected or error occurs, then returns None.

        Returns triplet
        -------
        quant : str
            Symbol representing measured quantity (R, U, I, T, G, C; where U, I with AC/DC/AC+DC).
        val : float
            Value of the quantity in base units or +-INF when Out of Range occurs.
        units : str
            Base unit of the measured quantity (Ohm, V, A, Deg C/Deg F, S, F).

        """
        r = self.send_command("QM")
        if r is None:
            return None
        try:
            r.index("- OFF -")
            return
        except ValueError:
            pass
        p1 = r.split(",", 1)
        try:
            oor = p1[1].index("Out of range.")
            units = p1[1][oor+14:].strip()
            if units[0] in "kMmun":
                units = units[1:]
            val = float('inf') if p1[1][0] == "+" else float('-inf')
        except ValueError:
            p2 = p1[1].split(" ", 1)
            val = float(p2[0])
            units = p2[1].strip()
            if units[0] == "k":
                val *= 1e3
            elif units[0] == "M":
                val *= 1e6
            elif units[0] == "m":
                val *= 1e-3
            elif units[0] == "u":
                val *= 1e-6
            elif units[0] == "n":
                val *= 1e-9
            if units[0] in "kMmun":
                units = units[1:]
                
        if units == "Ohms":
            quant = "R"
            units = "Ohm"
        elif units == "S":
            quant = "G"
        elif units[:3] == "Deg":
            quant = "T"
        elif units[0] == "V":
            quant = "U" + units[1:]
            units = units[0]
        elif units[0] == "A":
            quant = "I" + units[1:]
            units = units[0]
        elif units == "Farads":
            units = "F"
            quant = "C"
        elif units == "dBV":
            units = "dB"
            quant = "U"
            
        return quant, val, units
