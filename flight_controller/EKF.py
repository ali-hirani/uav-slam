import state
import math
import json
import numpy as np

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

    #f.writerow(['fuck you', dt, vx, vy, yaw, dx, dy, x, y])
    return state

def efkUpdate(state):
    pass
    return state

def wraptopi(x):
    if x > math.pi:
        x = x - (np.floor(x / (2 * np.pi)) + 1) * 2 * math.pi
    elif x < -np.pi:
        x = x + (np.floor(x / (-2 * np.pi)) + 1) * 2 * math.pi
    return x
