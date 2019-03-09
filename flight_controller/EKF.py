import state
import math
import json

# acceept a json object and state, and return a new state object
def processData(jsonPayload, curState):

    # basically if state isnt valid it just means its the first run through and we dont have time
    if not curState.valid :
        curState.time = (float(jsonPayload['timestamp']) / 1000) # to seconds
        curState.vx = float(jsonPayload['xVelocity']) / 1000 # convert to m/s
        curState.vy = float(jsonPayload['yVelocity']) / 1000 # convert to m/s
        curState.yaw = float(jsonPayload['clockwiseDegrees']) *  math.pi / 180;
        curState.valid = True
        return curState


    # update measurment state:
    curState.dt = (float(jsonPayload['timestamp']) / 1000) - curState.time
    curState.time = (float(jsonPayload['timestamp']) / 1000) # to seconds
    curState.vx = float(jsonPayload['xVelocity']) / 1000 # convert to m/s
    curState.vy = float(jsonPayload['yVelocity']) / 1000 # convert to m/s
    curState.yaw = float(jsonPayload['clockwiseDegrees']) *  math.pi / 180;

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

    #f.writerow(['fuck you', dt, vx, vy, yaw, dx, dy, x, y])
    return state

def efkUpdate(state):
    pass
    return state
