import socket
import logging
import time
import numpy as np
import matplotlib.pyplot as plt
from plot_data import DataPlot, RealtimePlot


fig, axes = plt.subplots()
data = DataPlot()
dataplotter = RealtimePlot(axes)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

def udp_init(ip):
    UDP_IP = ip
    UDP_PORT = 2000
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((UDP_IP,UDP_PORT))

def plot_setup(title):
    # style.use('fivethirtyeight')
    plt.title(title)
    plt.ylabel("Sensor Data in mm")

def plot_data(x, y, y2):
    x = float(x)
    y = float(y)
    y2 = float(y2)
    data.add(x,y,y2)
    dataplotter.plot(data)  
    plt.pause(0.0001)

    

#inits
# udp_init("192.168.0.104")
udp_init("10.42.0.143")
plot_setup("VL6180x Sensor Data")
i = 0 
while True:
        i += 1
        sensor_data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print sensor_data
        plot_data(i, sensor_data, 0)
