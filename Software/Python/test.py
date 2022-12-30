# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 16:02:10 2021
@author: Vojtech Vrba (vrba.vojtech@gmail.com)

Test script for FLUKE 189 True RMS Multimeter UART communication.

Python lib dependency: pyserial
Install in command line with: pip install pyserial-3.5-py2.py3-none-any.whl
"""

from fluke189 import Fluke189
from datetime import datetime

if __name__ == "__main__":
    fluke = Fluke189("COM9")
    fluke.connect()
    
    print("Identification:", fluke.identification())
    
    data = list()
    
    while True:
        #print("Measurement no.", i, ":", fluke.query_measurement())
        ts = datetime.now().timestamp()
        m = fluke.query_measurement()
        print(ts, m)
        data.append((ts, m))
        #time.sleep(0.5)
        
    fluke.disconnect()
    