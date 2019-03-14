import state
import math
import json
import numpy as np
from filterpy.kalman import ExtendedKalmanFilter as ekf
from sympy import *

def landMarkIntersect(x,y,theta,p1x,p1y,p2x,p2y, range):
    #how long past the ends of the line can we be and still have this count
    lengthThresh = 0.1
    #how far off the surface of the line can we be and still have this count
    depthThresh = 0.05
    k = (y + (p1x-x) * np.tan(theta) - p1y)/(p2y-p1y-(p2x-p1x)*np.tan(theta))
    #note this is biased by line length fuck it
    if k < 0-lengthThresh or k > 1+lengthThresh:
        return False
    t = (p1x + k*(p2x-p1x)-x)/np.cos(theta)
    if t < range-depthThresh or k > range+depthThresh:
        return False
    #if we made it here its a valid landmark
    print("repeat landmark")
    return True

# acceept a json object and state, and return a new state object
def processData(jsonPayload, curState):

    # basically if state isnt valid it just means its the first run through and we dont have time
    if not curState.valid :
        curState.time = (float(jsonPayload['timestamp']) / 1000) # to seconds
        curState.vx = float(jsonPayload['xVelocity']) / 1000 # convert to m/s
        curState.vy = float(jsonPayload['yVelocity']) / 1000 # convert to m/s
        curState.yaw = float(jsonPayload['clockwiseDegrees']) *  math.pi / 180
        curState.yaw = wraptopi(curState.yaw)


        curState.depths = [float(jsonPayload['lidar0'])/100, float(jsonPayload['lidar1'])/100, float(jsonPayload['lidar2'])/100, float(jsonPayload['lidar3'])/100]

        curState.valid = True
        return curState


    # update measurment state:
    curState.dt = (float(jsonPayload['timestamp']) / 1000) - curState.time
    curState.time = (float(jsonPayload['timestamp']) / 1000) # to seconds
    curState.vx = float(jsonPayload['xVelocity']) / 1000 # convert to m/s
    curState.vy = float(jsonPayload['yVelocity']) / 1000 # convert to m/s
    curState.yaw = float(jsonPayload['clockwiseDegrees']) *  math.pi / 180;
    curState.depths = [float(jsonPayload['lidar0'])/100, float(jsonPayload['lidar1'])/100, float(jsonPayload['lidar2'])/100, float(jsonPayload['lidar3'])/100]


    #state = ...
    curState = efkPredict(curState)
    curState = efkUpdate(curState)

    return curState


def efkPredict(state):
    dx = state.vx * state.dt
    #print("dx", dx)
    dy = state.vy * state.dt
    #print("dy", dy)
    state.x = state.x + dx * math.cos(state.yaw) - dy * math.sin(state.yaw)
    #print("x", x)
    state.y = state.y + dx * math.sin(state.yaw) + dy * math.cos(state.yaw)
    #print("y", y)
    F = [[state.dt*np.cos(state.yaw), 0 , -state.vx*state.dt*np.sin(state.yaw)],
    [0, state.dt*np.sin(state.yaw), state.vy*state.dt*np.cos(state.yaw)],
    [0,0,1]]
    FT = np.transpose(F)
    E = np.ones((1,3))
    ET = np.ones((3,1))
    # model disturbance variance
    r = 0.1
    R = np.eye(3)*r
    state.P = F*state.P*FT + E*R*ET
    #print(state.P)
    #f.writerow(['fuck you', dt, vx, vy, yaw, dx, dy, x, y])
    return state

def efkUpdate(state):

    if type(state.lines) is np.ndarray:
        for line in state.lines:
            x1, y1, x2, y2 = line[0]
            for i in range(len(state.sensors)):
                sensorAngle = state.sensors[i].angle
                if landMarkIntersect(state.x, state.y, state.yaw, x1, y1, x2, y2, state.yaw+sensorAngle ):

                    p1x,p1y,p2x,p2y = line[0]
                    x,y,yaw = symbols('x y yaw')
                    k = (y-p1y+(p1x-x)*tan(yaw+sensorAngle))/(p2y-p1y-(p2x-p1x)*tan(yaw+sensorAngle))
                    H = Matrix([sqrt((p1x+k*(p2x-p1x))**2+(p1y+k*(p2y-p1y))**2)])
                    sta = Matrix([x,y,yaw])
                    HJ = H.jacobian(sta)
                    HJ = HJ.subs(x, state.x)
                    HJ = HJ.subs(y, state.y)
                    HJ = HJ.subs(yaw, state.yaw)
                    HJ = np.array(HJ)
                    print(HJ)
                    Q = 0.1
                    thing = np.linalg.inv((HJ*state.P*np.transpose(HJ)  + Q))
                    print(thing)
                    K = state.P*np.transpose(HJ)* thing
                    print(K)
                    print(HJ)

    return state

def wraptopi(x):
    if x > math.pi:
        x = x - (np.floor(x / (2 * np.pi)) + 1) * 2 * math.pi
    elif x < -np.pi:
        x = x + (np.floor(x / (-2 * np.pi)) + 1) * 2 * math.pi
    return x
