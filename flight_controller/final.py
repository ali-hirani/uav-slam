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
import sys
import os
import cv2

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

WriteToFile = False
ReadFromFile = True
ReadFileName = "D:\\School\\fydp\\fresh_run1.csv"

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
    print("Connected to Node!")

# initialize state - basically just set up the sensors
def initState():
    global globalState
    s1 = state.Sensor([0.,0.],3 * math.pi/2)
    s2 = state.Sensor([0.,0.], math.pi)
    s3 = state.Sensor([0.,0.], math.pi/2)
    globalState = state.State([s1,s2,s3])
    globalState.busy = True


def writeData(data):
    f.writerow([data])

    # print(data)
    # if (data["dataValid"] == True):
    #     pass
    #     f.writerow([data['timestamp'], data['controlState'],data['flyState'],data['accelerometers']['x'],data['accelerometers']['y'],data['accelerometers']['z'],data['gyroscopes']['x'],data['gyroscopes']['y'],data['gyroscopes']['z'],data['frontBackDegrees'],data['leftRightDegrees'],data['clockwiseDegrees'],data['xVelocity'],data['yVelocity'],data['zVelocity']])

# Working Flight Test and drone data recieve
def issueCommand(command):
    global runningCmdNum
    globalState.busy = False

    # while (runningCmdNum != 0 and getCmdNum(s.recv(4096)) != runningCmdNum):
    #     pass
    runningCmdNum = 10
    print("issued :  " + command + "," + str(runningCmdNum))
    socketToNode.sendall(command + "," + str(runningCmdNum))




def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return [qx, qy]

def depthToPoint(drone, sensorIndex, depth):
    # p1 = np.add(drone.sensors[sensorIndex].offset, [drone.x, drone.y])
    # p2 = [p1[0], p1[1]+depth]
    # p2 = rotate(p1, p2, drone.sensors[sensorIndex].angle)
    # #p1 = rotate([self.pos[0], self.pos[1]], p1, self.rot)
    # p2 = rotate([drone.x, drone.y], p2, drone.yaw)
    # return p2

    # ignore sensor offset
    theta = drone.sensors[sensorIndex].angle + drone.yaw
    theta = EKF.wraptopi(theta)
    p1 = [depth * math.cos(theta), depth * math.sin(theta)]
    p2 = [drone.x + p1[0], drone.y+ p1[1]]
    return p2

# ==== "MAIN" ====

# file writing stuff that we will need later so its still here
f = csv.writer(open("yolo.csv", "wb+"))
# f.writerow(['timestamp', 'ctrlState', 'flyState', 'a_x', 'a_y', 'a_z', 'g_x', 'g_y', 'g_z', 'front_back_deg', 'left_right_deg', 'clockwise_deg', 'x_v', 'y_v', 'z_v' ])
f.writerow(['fuck you', 'dt', 'vx', 'vy', 'yaw', 'dx', 'dy', 'x,' 'y'])


initState()

x = []
y = []

startx = []
starty = []
dirx = []
diry = []

lidar1x = []
lidar1y = []
lidar2x = []
lidar2y = []
lidar3x = []
lidar3y = []

if ReadFromFile:
    reader = csv.reader(open(ReadFileName))
else:
    connectToNodeServer(ip, port)
#plt.ion() # enable real-time plotting
plt.figure(1) # create a plot
while True:
    try:
        if ReadFromFile:
            try:
                raw = reader.next()[0]
            except Exception as e:
                break

        else:
            # blocking receive - if we dont have data and we already processed the last packet then we good
            raw = socketToNode.recv(4096)
        payloadJSON = json.loads(raw)
        # if its 'data'...
        if payloadJSON["command"] == "ra":
            #print(payloadJSON)
            writeData(raw)
            # only count on good data
            counter += 1

            # update our idea of where we are and whats around us
            globalState = EKF.processData(payloadJSON, globalState)
            # use updated state to figure out what to do
            command = flightPlanner.planFlight(globalState, counter)
            x.append(globalState.x)
            y.append(globalState.y)
            if counter%200 == 0:
                startx.append(globalState.x)
                starty.append(globalState.y)
                dirx.append(math.cos(globalState.yaw)*0.05)
                diry.append(math.sin(globalState.yaw)*0.05)

            #print("dt: "+str(globalState.dt))
            if globalState.depths[0] < 12:
                p = depthToPoint(globalState, 0, globalState.depths[0])
                lidar1x.append(p[0])
                lidar1y.append(p[1])
            else:
                lidar1x.append(0)
                lidar1y.append(0)
            if globalState.depths[1] < 12:
                p = depthToPoint(globalState, 1, globalState.depths[1])
                lidar2x.append(p[0])
                lidar2y.append(p[1])
            else:
                lidar2x.append(0)
                lidar2y.append(0)
            if globalState.depths[2] < 12:
                p = depthToPoint(globalState, 2, globalState.depths[2])
                lidar3x.append(p[0])
                lidar3y.append(p[1])
            else:
                lidar3x.append(0)
                lidar3y.append(0)
            globalState.occGrid.updateGrid(globalState, 0)
            globalState.occGrid.updateGrid(globalState, 1)
            globalState.occGrid.updateGrid(globalState, 2)

            img = np.array(globalState.occGrid.grid * 255, dtype = np.uint8)
            #cv2.imshow("image1", img);
            ret,thresh1 = cv2.threshold(img,220,255,cv2.THRESH_BINARY)

            ret,thresh2 = cv2.threshold(img,255,255,cv2.THRESH_BINARY)
            minLineLength = 3
            maxLineGap = 2
            lines = cv2.HoughLinesP(thresh1,1,np.pi/180,10, minLineLength=minLineLength, maxLineGap = maxLineGap)

            linesToAdd = []
            if type(lines) is np.ndarray:
                #print(len(lines))
                #print(lines)
                for line in lines:

                    x1, y1, x2, y2 = line[0]
                    p1 = globalState.occGrid.getPoint([x1,y1])
                    p2  = globalState.occGrid.getPoint([x2,y2])

                    linesToAdd.append([p1[0], p1[1], p2[0], p2[1]])
                    cv2.line(thresh2,(x1,y1),(x2,y2),(255,0,0),1)
            globalState.lines = np.array(linesToAdd)

            if counter %200 == 0:
                plt.clf()
                #plot1
                plt.subplot(221)
                plt.plot(x,  y, label="posX")
                for i in range(0, len(startx)):
                    plt.arrow(startx[i], starty[i], dirx[i], diry[i],  head_width=0.05, head_length=0.01, fc='k', ec='k', width=0.0001)
                plt.scatter(lidar1x[counter-10:],  lidar1y[counter-10:], color="red", s = 0.001)
                plt.scatter(lidar2x[counter-10:],  lidar2y[counter-10:], color="green", s = 0.001)
                plt.scatter(lidar3x[counter-10:],  lidar3y[counter-10:], color="blue", s = 0.001)
                for line in globalState.lines:
                    plt.plot([line[0],line[2]], [line[1], line[3]])
                plt.grid()

                #plt2
                plt.subplot(222)
                plt.imshow(globalState.occGrid.grid, 'Greys')

                #plt3
                plt.subplot(223)
                plt.imshow(thresh1)
                #plt4
                plt.subplot(224)
                plt.imshow(thresh2)

                plt.pause(0.1)
            #if we should then issue the command
            if command != -1:
                issueCommand(command)
        else :
            #handle callbacks TODO: this is fragile as all hell
            if runningCmdNum == int(payloadJSON["num"]):
                print("received confirmation: " + str(runningCmdNum))
                globalState.busy = False
                globalState.after_counter = counter


    except Exception as e:
        print("Main loop encountered a problem: " + str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
    	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    	print(exc_type, fname, exc_tb.tb_lineno)
        print(raw)
        pass
plt.show()

# plt.show()
# plt.ion() # enable real-time plotting
# plt.figure(1) # create a plot
# for j in range(0, len(dirx)):
#     plt.clf()
#     plt.plot(x[:j*200],  y[:j*200], label="posX")
#     for i in range(0, j):
#         plt.arrow(startx[i], starty[i], dirx[i], diry[i],  head_width=0.05, head_length=0.01, fc='k', ec='k', width=0.0001)
#     plt.scatter(lidar1x[:j*200],  lidar1y[:j*200], color="red", s = 0.001)
#     plt.scatter(lidar2x[:j*200],  lidar2y[:j*200], color="green", s = 0.001)
#     plt.scatter(lidar3x[:j*200],  lidar3y[:j*200], color="blue", s = 0.001)
#
#     plt.grid()
#     plt.pause(1)


if not ReadFromFile:
    socketToNode.close()
