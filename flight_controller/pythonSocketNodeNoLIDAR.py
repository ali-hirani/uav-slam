import socket
import time
import logging
import numpy as np
import matplotlib.pyplot as plt
import json
import csv
import math
from plot_data import DataPlot, RealtimePlot


# Drone/Node server
ip = '127.0.0.1'
port = 1337

# connect to node server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (ip, port)
s.connect(server_address)

def getCmdNum(raw):
    if (raw == ""):
        return -1

    payloadJSON = json.loads(raw)

    # if we are receiving IMU data
    if payloadJSON["command"] == "ra":
        # writeData(payloadJSON)
        return -1
    else:
        return int(payloadJSON["num"])

def writeData(data):
    # print(data)
    if (data["dataValid"] == True):
        pass
        f.writerow([data['timestamp'], data['controlState'],data['flyState'],data['accelerometers']['x'],data['accelerometers']['y'],data['accelerometers']['z'],data['gyroscopes']['x'],data['gyroscopes']['y'],data['gyroscopes']['z'],data['frontBackDegrees'],data['leftRightDegrees'],data['clockwiseDegrees'],data['xVelocity'],data['yVelocity'],data['zVelocity']])
        # Write to CSV file

# Working Flight Test and drone data recieve 
def issueCommand(command):
    global runningCmdNum
    notBusy = False

    # while (runningCmdNum != 0 and getCmdNum(s.recv(4096)) != runningCmdNum):
    #     pass
    runningCmdNum+= 1
    s.sendall(command + "," + str(runningCmdNum))

def efkPredict(dt, vx, vy, yaw):
    global x, y
    dx = vx * dt
    print("dx", dx)
    dy = vy * dt
    print("dy", dy)
    x = x + dx * math.cos(yaw) - dy * math.sin(yaw)
    print("x", x)
    y = y + dx * math.sin(yaw) + dy * math.cos(yaw)
    print("y", y)

    f.writerow(['fuck you', dt, vx, vy, yaw, dx, dy, x, y])


def processData(json):
    global prevTimeStamp

    # extract usful data
    if prevTimeStamp <= 0:
        prevTimeStamp = float(json['timestamp']) / 1000
        return

    dt = (float(json['timestamp']) / 1000) - prevTimeStamp
    vx = float(json['xVelocity']) / 1000 # convert to m/s
    vy = float(json['yVelocity']) / 1000 # convert to m/s
    yaw = float(json['clockwiseDegrees']) *  math.pi / 180;

    efkPredict(dt, vx, vy, yaw)

    prevTimeStamp = float(json['timestamp']) / 1000

f = csv.writer(open("yolo.csv", "wb+"))
# f.writerow(['timestamp', 'ctrlState', 'flyState', 'a_x', 'a_y', 'a_z', 'g_x', 'g_y', 'g_z', 'front_back_deg', 'left_right_deg', 'clockwise_deg', 'x_v', 'y_v', 'z_v' ])
f.writerow(['fuck you', 'dt', 'vx', 'vy', 'yaw', 'dx', 'dy', 'x,' 'y'])

while (s.recv(4096) != "connection confirmation"):
    pass
print("Connected!")

runningCmdNum = 0
notBusy = False
x = 0
y = 0
prevTimeStamp = 0

# while (s.recv(4096) != "connection confirmation"):
#     pass
# print("Connected!")

issueCommand("to")
counter = 0

while True:
    counter += 1
    try:
        raw = s.recv(4096)
        payloadJSON = json.loads(raw)
        if payloadJSON["command"] == "ra":
            # print(payloadJSON)
            processData(payloadJSON)
            # writeData(payloadJSON)
        else :
            if runningCmdNum == int(payloadJSON["num"]):
                notBusy = True

    except Exception as e:
        pass

    if counter == 50:
        issueCommand("fo")

    if counter == 150:
        issueCommand("la")

s.close()
