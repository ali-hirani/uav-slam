import state
import math
import json
import numpy as np
from filterpy.kalman import ExtendedKalmanFilter as ekf
import sympy as sp
import sys
import os

def landMarkIntersect(x,y,theta,p1x,p1y,p2x,p2y, range):

    # print(x+range*np.cos(theta))
    # print(y+range*np.sin(theta))

    #how long past the ends of the line can we be and still have this count
    lengthThresh = 0.2
    #how far off the surface of the line can we be and still have this count
    depthThresh = 0.1
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
def processData(curState):
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
    r = 0.01
    R = np.eye(3)*r
    state.P = F*state.P*FT + E*R*ET
    #print(state.P)
    #f.writerow(['fuck you', dt, vx, vy, yaw, dx, dy, x, y])
    return state

def efkUpdate(state):
    try:
        if type(state.lines) is np.ndarray:
            for line in state.lines:
                # print(line)
                x1= line[0]
                y1= line[1]
                x2= line[2]
                y2 = line[3]
                for i in range(len(state.sensors)):
                    sensorAngle = state.sensors[i].angle
                    if landMarkIntersect(state.x, state.y, state.yaw, x1, y1, x2, y2, state.yaw+sensorAngle ):

                        #p1x,p1y,p2x,p2y = line[0]
                        x,y,yaw = sp.symbols('x y yaw')
                        k = (y-y1+(x1-x)*sp.tan(yaw+sensorAngle))/(y2-y1-(x2-x1)*sp.tan(yaw+sensorAngle))
                        H = sp.Matrix([sp.sqrt((x1+k*(x2-x1))**2+(y1+k*(y2-y1))**2)])
                        sta = sp.Matrix([x,y,yaw])
                        HJ = H.jacobian(sta)
                        HJ = HJ.subs(x, state.x)
                        HJ = HJ.subs(y, state.y)
                        HJ = HJ.subs(yaw, state.yaw)
                        HJ = np.array(HJ)


                        HJ = np.array(HJ).astype(np.float64)
                        print(HJ)
                        Q = np.array([0.001]).astype(np.float64)
                        thing = np.linalg.inv((HJ*state.P*np.transpose(HJ)  + Q))
                        #print(thing)
                        K = state.P*np.transpose(HJ)* thing
                        print(K)
                        H = H.subs(x, state.x)
                        H = H.subs(y, state.y)
                        H = H.subs(yaw, state.yaw)
                        H = np.array(H).astype(np.float64)
                        print(H)
                        print(state.depths[i])
                        thing2 = K * (state.depths[i]- H)
                        print(thing2)
                        state.x = state.x + thing2[0][0]
                        state.y = state.y +thing2[1][1]
    except Exception as e:
        print("fuck yourself: " + str(e))

        exc_type, exc_obj, exc_tb = sys.exc_info()
    	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    	print(exc_type, fname, exc_tb.tb_lineno)



    return state

def wraptopi(x):
    if x > math.pi:
        x = x - (np.floor(x / (2 * np.pi)) + 1) * 2 * math.pi
    elif x < -np.pi:
        x = x + (np.floor(x / (-2 * np.pi)) + 1) * 2 * math.pi
    return x
