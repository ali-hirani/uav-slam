import socket
import time
import logging
import numpy as np
import matplotlib.pyplot as plt
import json
import csv
import math
from plot_data import DataPlot, RealtimePlot
import state
import EKF
import flightPlanner

#========== GLOBALS =============
# Drone/Node server
ip = '127.0.0.1'
port = 1337
socketToNode = None

runningCmdNum = 0
#start busy until you connect to drone
prevTimeStamp = 0

counter = 0

globalState = None


# connect to node server
# will block until connection confirmation received
def connectToNodeServer(ip, port):
    # connect to node server
    global socketToNode
    socketToNode = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)
    socketToNode.connect(server_address)

    while (socketToNode.recv(4096) != "connection confirmation"):
        pass

    globalState.busy = False
    print("Connected!")

# initialize state - basically just set up the sensors
def initState():
    global globalState
    s1 = state.Sensor([0.05,0.], 0)

    globalState = state.State(s1)
    globalState.busy = True


def writeData(data):
    # print(data)
    if (data["dataValid"] == True):
        pass
        f.writerow([data['timestamp'], data['controlState'],data['flyState'],data['accelerometers']['x'],data['accelerometers']['y'],data['accelerometers']['z'],data['gyroscopes']['x'],data['gyroscopes']['y'],data['gyroscopes']['z'],data['frontBackDegrees'],data['leftRightDegrees'],data['clockwiseDegrees'],data['xVelocity'],data['yVelocity'],data['zVelocity']])
        # Write to CSV file

# Working Flight Test and drone data recieve
def issueCommand(command):
    global runningCmdNum
    globalState.busy = True

    # while (runningCmdNum != 0 and getCmdNum(s.recv(4096)) != runningCmdNum):
    #     pass
    runningCmdNum+= 1
    print("issued :  " + command + "," + str(runningCmdNum))
    socketToNode.sendall(command + "," + str(runningCmdNum))


# ==== "MAIN" ====

# file writing stuff that we will need later so its still here
f = csv.writer(open("yolo.csv", "wb+"))
# f.writerow(['timestamp', 'ctrlState', 'flyState', 'a_x', 'a_y', 'a_z', 'g_x', 'g_y', 'g_z', 'front_back_deg', 'left_right_deg', 'clockwise_deg', 'x_v', 'y_v', 'z_v' ])
f.writerow(['fuck you', 'dt', 'vx', 'vy', 'yaw', 'dx', 'dy', 'x,' 'y'])


initState()

connectToNodeServer(ip, port)

while True:
    try:
        # blocking receive - if we dont have data and we already processed the last packet then we good
        raw = socketToNode.recv(4096)
        payloadJSON = json.loads(raw)
        # if its 'data'...
        if payloadJSON["command"] == "ra":
            #print(payloadJSON)
            # only count on good data
            counter += 1

            # update our idea of where we are and whats around us
            globalState = EKF.processData(payloadJSON, globalState)
            # use updated state to figure out what to do
            command = flightPlanner.planFlight(globalState, counter)

            # if we should then issue the command
            if command != -1 :
                issueCommand(command)

            # writeData(payloadJSON)
        else :
            #handle callbacks TODO: this is fragile as all hell
            if runningCmdNum == int(payloadJSON["num"]):
                print("received confirmation: " + runningCmdNum)
                globalState.busy = False

    except Exception as e:
        print("Main loop encountered a problem: " + e)
        pass


socketToNode.close()
