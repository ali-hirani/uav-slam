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
import pythonFlight
from threading import Thread
import struct

#========== GLOBALS =============


#start busy until you connect to drone

drone = None
counter = 0
globalState = None
ReadFromFile = True
ReadFileName = "/Users/ali/4A/FYDP/uav-slam/flight_controller/data/test_run1552638067.09.csv"
ndc = -1
sockPi = None

#SOCKET FROM PI TO LAPTOP ----- START
TCP_IP = "192.168.43.61"
TCP_PORT = 5005

def connect():
    global sockPi
    global drone

    # Connect to pi
    sockPi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockPi.connect((TCP_IP, TCP_PORT))
    
    drone = pythonFlight.initDrone(drone)

    lidarThread = Thread(target = getLidar)
    lidarThread.start()

def collect_packet(size):
    global sockPi
    data = b''
    while len(data) < size:
        packet = sockPi.recv(size - len(data))
        if not packet:
            return None

        data = data + packet

    return data

def decode_data():
    global sockPi
    #first get the length of packet from first 4 bytes
    packet_length_bytes = collect_packet(4)
    if not packet_length_bytes:
        return None

    packet_length = struct.unpack('>I', packet_length_bytes)[0]

    encoded_data = collect_packet(packet_length)
    pair = (encoded_data[0], encoded_data[1:])

    return pair

# initialize state - basically just set up the sensors
def initState():
    global globalState
    s1 = state.Sensor([0.,0.], 0)
    s2 = state.Sensor([0.,0.], math.pi/2)
    s3 = state.Sensor([0.,0.], -math.pi/2)
    globalState = state.State([s1,s2,s3])
    globalState.busy = False

def writeData():
    global globalState
    f.writerow([globalState.dt, globalState.time, globalState.vx, globalState.vy, globalState.yaw, globalState.depths[0], globalState.depths[1], globalState.depths[2]])

# fixme
def issueCommand(command):
    globalState.busy = True

    if command == "takeoff":
        thread = Thread(target = takeoff)
        thread.start()
    elif command == "front":
        thread = Thread(target = move_drone, args = ["front", 0.1, 5])
        thread.start()
    elif command == "left":
        thread = Thread(target = move_drone, args = ["left", 0.1, 1])
        thread.start()
    elif command == "back":
        thread = Thread(target = move_drone, args = ["back", 0.1, 1])
        thread.start()
    elif command == "right":
        thread = Thread(target = move_drone, args = ["right", 0.1, 1])
        thread.start()
    elif command == "rotate_cw":
        thread = Thread(target = do_rotation)
        thread.start()
    elif command == "rotate_ccw":
        thread = Thread(target = do_rotation)
        thread.start()
    elif command == "land":
        thread = Thread(target = drone.land)
        thread.start()
    elif command == "square_angled":
        thread = Thread(target = do_square_angled)
        thread.start()

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

def getLidar():
    global globalState
    global sockPi

    while True :
        encoded_data = decode_data()
        lidarNum = int(encoded_data[0])
        lidarVal = float(encoded_data[1])
        globalState.depths[lidarNum] = lidarVal / 100

def takeoff():
    global globalState
    
    print("takeoff begin")
    globalState.busy = True
    print "doing trim + self rotation"
    drone.getSelfRotation(5)
    print("self-rotation_value:  " + str(drone.selfRotation))
    time.sleep(1)
    drone.setSpeed(0.1)
    time.sleep(0.1)
    print "prepare for takeoff"
    drone.takeoff()
    #wait till drone is actually flying
    time.sleep(5)

    globalState.busy = False
    print("takeoff end")

def move_drone(direction,speed, period):
    global globalState
    
    globalState.busy = True
    
    if direction == "front":
        print "moving forward"
        drone.moveForward(speed)
        time.sleep(period)
        drone.stop()
        time.sleep(2)


    elif direction == "back":
        print "moving backward"
        drone.moveBackward(speed)
        time.sleep(period)
        drone.stop()
        time.sleep(2)

    elif direction == "right":
        print "moving right"
        drone.moveRight(speed)
        time.sleep(period)
        drone.stop()
        time.sleep(2)

    elif direction == "left":
        print "moving left"
        drone.moveLeft(speed)
        time.sleep(period)
        drone.stop()
        time.sleep(2)

    globalState.busy = False
 

#do 360 deg rotation in 8 steps
def do_rotation():
    global globalState

    globalState.busy = True
    counter = 1
    while counter <= 8:
        drone.hover()
        time.sleep(0.5)
        drone.turnAngle(-45, 1, 1)
        drone.hover()
        time.sleep(2)
        counter += 1
    globalState.busy = False

def do_square_angled():
    global globalState
    
    globalState.busy = True
    counter = 1
    while counter <= 4:
        drone.hover()
        time.sleep(0.5)
        drone.moveForward(0.1)
        time.sleep(1)
        drone.stop()
        time.sleep(0.5)
        drone.turnAngle(-90, 1, 10)
        time.sleep(0.5)
        drone.hover()
        time.sleep(2)
        counter += 1
    drone.land()
    globalState.busy = False


# ==== "MAIN" ====

# file writing stuff that we will need later so its still here
fileName = "data/test_run" + str(time.time()) + ".csv"
f = csv.writer(open(fileName, "wb+"))

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

initState()
if ReadFromFile:
    reader = csv.reader(open(ReadFileName))
else:
    connect()

while True:
    try:
        if ReadFromFile:
            try:
                raw = reader.next()
            except Exception as e:
                break

            globalState.dt = float(raw[0])
            globalState.time = float(raw[1])
            globalState.vx = float(raw[2])
            globalState.vy = float(raw[3])
            globalState.yaw = float(raw[4])
            globalState.depths[0] = float(raw[5])
            globalState.depths[1] = float(raw[6])
            globalState.depths[2] = float(raw[7])

        else:
            while ndc == drone.NavDataCount:
                pass

            ndc = drone.NavDataCount
            velocity = drone.NavData["demo"][4]
            angles = drone.NavData["demo"][2]

            # basically if state isnt valid it just means its the first run through and we dont have time
            if not globalState.valid :
                globalState.time = float(drone.NavDataTimeStamp) / 1000 # to seconds

                globalState.vx = float(velocity[0]) / 1000 # convert to m/s
                globalState.vy = float(velocity[1]) / 1000 # convert to m/s
                globalState.yaw = float(angles[2]) *  math.pi / 180
                # globalState.yaw = wraptopi(globalState.yaw)

                globalState.valid = True
                continue

            # update measurment state:
            globalState.dt = (float(drone.NavDataTimeStamp) / 1000) - globalState.time
            globalState.time = float(drone.NavDataTimeStamp) / 1000 # to seconds
            globalState.vx = float(velocity[0]) / 1000 # convert to m/s
            globalState.vy = float(velocity[1]) / 1000 # convert to m/s
            globalState.yaw = float(angles[2]) *  math.pi / 180
        
        # print("dt" + str(globalState.dt))
        # print("time" + str(globalState.time))
        # print("vx" + str(globalState.vx))
        # print("vy" + str(globalState.vy))
        # print("yaw" + str(globalState.yaw))
        # print("yaw" + str(globalState.yaw))
        # print("depths" + str(globalState.depths))

        writeData()
        # only count on good data
        counter += 1
        print(counter)

        # update our idea of where we are and whats around us
        globalState = EKF.processData(globalState)
        # use updated state to figure out what to do
        command = flightPlanner.planFlight(globalState, counter)
        x.append(globalState.x)
        y.append(globalState.y)
        if counter%60 == 0:
            startx.append(globalState.x)
            starty.append(globalState.y)
            dirx.append(math.cos(globalState.yaw)*0.02)
            diry.append(math.sin(globalState.yaw)*0.02)

        p = depthToPoint(globalState, 0, globalState.depths[0])
        lidar1x.append(p[0])
        lidar1y.append(p[1])
        print("dt: "+str(globalState.dt))
        p = depthToPoint(globalState, 1, globalState.depths[1])
        lidar2x.append(p[0])
        lidar2y.append(p[1])
        p = depthToPoint(globalState, 2, globalState.depths[2])
        lidar3x.append(p[0])
        lidar3y.append(p[1])
        # if we should then issue the command
        if command != -1 and not ReadFromFile:
            print("FUCK LUKE",command)
            issueCommand(command)

    except Exception as e:
        print("Main loop encountered a problem: " + str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        pass

fig, axarr = plt.subplots(1, sharex=True)
axarr.plot(x,  y, label="posX")
for i in range(0, len(dirx)):
    axarr.arrow(startx[i], starty[i], dirx[i], diry[i],  head_width=0.005, head_length=0.01, fc='k', ec='k', width=0.0001)
axarr.plot(lidar1x,  lidar1y, color="red")
# axarr.plot(lidar2x,  lidar2y, color="red")
# axarr.plot(lidar3x,  lidar3y, color="red")

plt.show()
