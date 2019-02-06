import socket
import time
import logging
import numpy as np
import matplotlib.pyplot as plt
from plot_data import DataPlot, RealtimePlot


# Sensor Stuff
# fig, axes = plt.subplots()
# data = DataPlot()
# dataplotter = RealtimePlot(axes)
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
# sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

# Drone/Node server
ip = '127.0.0.1'
port = 1337

# connect to node server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (ip, port)
s.connect(server_address)

# def udp_init(ip):
#     UDP_IP = ip
#     UDP_PORT = 5005
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     sock.bind((UDP_IP,UDP_PORT))

#     UDP_PORT1 = 2000
#     sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     sock1.bind((UDP_IP,UDP_PORT1))

# def plot_setup(title):
#     plt.title(title)
#     plt.ylabel("Sensor Data in mm")

# def plot_data(x, y, y2):
#     x = float(x)
#     y = float(y)
#     y2 = float(y2)
#     data.add(x,y,y2)
#     dataplotter.plot(data)  
#     plt.pause(0.0001)


# Change to host laptop IP
# receive sensor data
# udp_init("10.42.0.143")
# plot_setup("VL6180x Sensor Data")

# runningAvg = 0
# iteration = 0
# i = 0
# while True:
# 	iteration += 1
# 	i += 1
# 	sensor_data_low, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
# 	# sensor_data_high, addr = sock1.recvfrom(1024) # buffer size is 1024 bytes

# 	runningAvg += int(sensor_data_low)

# 	plot_data(i, sensor_data_low, 0)

# 	if (iteration == 5) :
# 		runningAvg = runningAvg / iteration
# 		iteration = 0

# 		print(runningAvg)

# 		# take off when sensor is really close
# 		if (runningAvg < 40) :
# 			s.sendall(b"to")
# 		elif (runningAvg > 200) :
# 			s.sendall(b"la")

# 		runningAvg = 0

# Working Flight Test and drone data recieve 
time.sleep(1)
s.sendall(b"to")

data = s.recv(4096)
print(data)

time.sleep(5)
s.sendall(b"fo-1")
data = s.recv(4096)
print(data)

s.sendall(b"ra")
data = s.recv(4096)
print(data)

time.sleep(5)
s.sendall(b"la")

data = s.recv(4096)
print(data)

s.close()
