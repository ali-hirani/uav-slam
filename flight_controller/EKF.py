import state
import math
import json

# acceept a json object and state, and return a new state object
def processData(jsonPayload, curState):
    #global prevTimeStamp

    # extract usful data
    # if prevTimeStamp <= 0:
    #     prevTimeStamp = float(json['timestamp']) / 1000
    #     return

    # unpack relevant vars
    dt = 0.1
    #dt = (float(jsonPayload['timestamp']) / 1000) - prevTimeStamp
    vx = float(jsonPayload['xVelocity']) / 1000 # convert to m/s
    vy = float(jsonPayload['yVelocity']) / 1000 # convert to m/s
    yaw = float(jsonPayload['clockwiseDegrees']) *  math.pi / 180;

    #state = ...
    efkPredict(dt, vx, vy, yaw)
    efkUpdate()

    #prevTimeStamp = float(json['timestamp']) / 1000

    #return state

def efkPredict(dt, vx, vy, yaw):
    #global x, y
    x = 0
    y = 0
    dx = vx * dt
    print("dx", dx)
    dy = vy * dt
    print("dy", dy)
    x = x + dx * math.cos(yaw) - dy * math.sin(yaw)
    print("x", x)
    y = y + dx * math.sin(yaw) + dy * math.cos(yaw)
    print("y", y)

    #f.writerow(['fuck you', dt, vx, vy, yaw, dx, dy, x, y])

def efkUpdate():
    pass
