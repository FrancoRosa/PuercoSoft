#!/usr/bin/python3
from redisworks import Root
from time import sleep, time
import serial

device_baudrate = 921600
device_port = "/dev/ttyUSB0"
device_timeout = 0.1
buffer_size = 663  #fs = 3315Hz, then 663 samples every 200ms

buffer_data_ch1 = [0]*buffer_size
buffer_data_ch2 = [0]*buffer_size

root = Root()
device = serial.Serial(port=device_port,
                        baudrate=device_baudrate,
                        timeout = device_timeout)
maxADC = 4096
maxVin = 3.3
adcFactor = maxVin/maxADC

while True:
    try:
        i = 0
        sleep(.05)
        for k in range(buffer_size):
            data_raw = device.readline()
            if len(data_raw)==7:
                data_ch1 = int(data_raw[:3],16)*adcFactor
                data_ch2 = int(data_raw[3:-1],16)*adcFactor
                buffer_data_ch1[k]=data_ch1
                buffer_data_ch2[k]=data_ch2
                i = i + 1
            if i >= buffer_size:
                root.data_ch1 = buffer_data_ch1;
                root.data_ch2 = buffer_data_ch2;
                root.timestamp = time()
                i = 0
        print("sample: %2.3f %2.3f"%(data_ch1,data_ch2))
    except:
        pass
