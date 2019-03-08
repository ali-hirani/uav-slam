import socket
import time
import logging
import numpy as np
import matplotlib.pyplot as plt
import json
import csv
from plot_data import DataPlot, RealtimePlot


# Sensor Stuff
fig, axes = plt.subplots()
data = DataPlot()
dataplotter = RealtimePlot(axes)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.setblocking(0)
# sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

# Drone/Node server
ip = '127.0.0.1'
port = 1337

# connect to node server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (ip, port)
s.connect(server_address)
s.setblocking(0)

def udp_init(ip):
    UDP_IP = ip
    UDP_PORT = 5005
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((UDP_IP,UDP_PORT))

    # UDP_PORT1 = 2000
    # sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # sock1.bind((UDP_IP,UDP_PORT1))

def plot_setup(title):
    plt.title(title)
    plt.ylabel("Sensor Data in mm")

def plot_data(x, y, y2):
    x = float(x)
    y = float(y)
    y2 = float(y2)
    data.add(x,y,y2)
    dataplotter.plot(data)  
    plt.pause(0.0001)

def getCmdNum(raw):
    if (raw == ""):
        return -1

    # print("fuck luke", raw)
    payloadJSON = json.loads(raw)

    # if we are receiving IMU data
    if payloadJSON["command"] == "ra":
        writeData(payloadJSON)
        return -1
    else:
        return int(payloadJSON["num"])

def writeData(f, data):
    if (data["dataValid"] == True):
        f.writerow([data['timestamp'], data['controlState'], data['flyState'], data['accelerometers']['x'], data['accelerometers']['y'], data['accelerometers']['z'],
            data['gyroscopes']['x'], data['gyroscopes']['y'], data['gyroscopes']['z'], data['frontBackDegrees'], data['leftRightDegrees'], data['clockwiseDegrees']])
        print("unique", data)
        # Write to CSV file

# # Working Flight Test and drone data recieve 
def issueCommand(command):
    global runningCmdNum

    while (runningCmdNum != 0 and getCmdNum(s.recv(4096)) != runningCmdNum):
        pass
    runningCmdNum+= 1
    s.sendall(command + "," + str(runningCmdNum))


# Change to host laptop IP
# receive sensor data
# udp_init("10.42.0.25")
udp_init("1.2.3.1")
#plot_setup("VL6180x Sensor Data")

f = csv.writer(open("sensor_and_imu_data.csv", "wb+"))
f.writerow(['timestamp', 'ctrlState', 'flyState', 'a_x', 'a_y', 'a_z', 'g_x', 'g_y', 'g_z', 'front_back_deg', 'left_right_deg', 'clockwise_deg' ])

runningAvg = 0
iteration = 0
i = 0
while True:
    iteration += 1
    i += 1

    try:
        sensor_data_low, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print(sensor_data_low)
        f.writerow(["depth", time.time(),sensor_data_low])
        # sensor_data_high, addr = sock1.recvfrom(1024) # buffer size is 1024 bytes
    except Exception as e:
        pass

    try:
        raw = s.recv(4096)
        payloadJSON = json.loads(raw)
        if payloadJSON["command"] == "ra":
            writeData(f, payloadJSON)
    except Exception as e:
        pass
    

runningCmdNum = 0

# while (s.recv(4096) != "connection confirmation"):
#     pass
# print("Connected!")

# issueCommand("to")
# issueCommand("la")
# issueCommand("to")
# issueCommand("fo")
# issueCommand("fo")
# issueCommand("fo")
# issueCommand("la")


# data = s.recv(4096)
# print("1", data)

# time.sleep(5)
# s.sendall(b"fo-1")
# data = s.recv(4096)
# print("2", data)

# time.sleep(5)
# s.sendall(b"fo-1")
# data = s.recv(4096)
# print("3", data)

# time.sleep(5)
# s.sendall(b"fo-1")
# data = s.recv(4096)
# print("4", data)

# s.sendall(b"ra")
# data = s.recv(4096)
# print(data)

# time.sleep(5)
# s.sendall(b"la")

# data = s.recv(4096)
# print("5", data)

s.close()
