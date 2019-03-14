import numpy as np
import math
import EKF

class Sensor:
    def __init__(self, offset, angle):
        self.offset = offset
        self.angle = angle

class Drone:
    def __init__(self, sensors):
        #list of sensors
        self.sensors = sensors
        # xy
        self.pos = [0,0]
        #rot in rads
        self.rot = 0
        # vx,vy
        self.vel = [0,0]

class OccGrid:
    def __init__(self, cellSizeInM, mToCover):
        self.cellSizeInM = cellSizeInM
        self.mToCover = mToCover
        self.gridSize = int(round(mToCover/cellSizeInM))
        self.grid = np.full((self.gridSize, self.gridSize), 0.5)

    def getCell(self, point):
        x = int(round((point[0]+self.mToCover/2)/self.cellSizeInM))
        y = int(round((point[1]+self.mToCover/2)/self.cellSizeInM))
        return [x,y]

    def getPoint(self, indexes):
        y = (indexes[0] * self.cellSizeInM) - self.mToCover/2
        x = (indexes[1] * self.cellSizeInM) - self.mToCover/2
        return [x,y]
    def updateCell(self,cellIndex, value):
        if cellIndex[0] < 0 or cellIndex[0] >= self.gridSize:
            #print("fuck u x")
            return
        if cellIndex[1] < 0 or cellIndex[1] >= self.gridSize:
            #print("fuck u y")
            return
        self.grid[cellIndex[0]][cellIndex[1]] = np.clip(self.grid[cellIndex[0]][cellIndex[1]] + value, 0,1)

    def updateGrid(self, state, sensorIndex):
        curDepth = state.depths[sensorIndex]
        # we have a "hit"
        if curDepth < 12:
            p1 = [curDepth * math.cos(state.yaw + state.sensors[sensorIndex].angle), curDepth * math.sin(state.yaw + state.sensors[sensorIndex].angle)]
            p2 = [state.x + p1[0], state.y+ p1[1]]
            cell = self.getCell(p2)
            self.updateCell(cell, 0.02)
            curDepth -= self.cellSizeInM
        lastCell = None
        while curDepth > 0.3:
            p1 = [curDepth * math.cos(state.yaw + state.sensors[sensorIndex].angle), curDepth * math.sin(state.yaw + state.sensors[sensorIndex].angle)]
            p2 = [state.x + p1[0], state.y+ p1[1]]
            cell = self.getCell(p2)
            if lastCell != None and lastCell != cell:
                self.updateCell(cell, -0.005)

            lastCell = cell
            curDepth -= self.cellSizeInM



# its a line - how should we paramaterize it?
class Landmark:
    def __init__(self, xy):
        self.p1 = None
        self.p2 = None



class State:
    def __init__(self, sensors):
        # ==== static state ====
        self.sensors = sensors

        # ==== measurements ====
        self.time = 0
        self.dt = 0
        self.vx = 0;
        self.vy = 0
        self.yaw = 0
        # depths index should match up with index in sensors array
        self.depths = []

        # ==== predicted state ====
        self.x = 0
        self.y = 0
        # do we need this?
        self.predictedYaw = 0
        self.lines = []
        self.occGrid = OccGrid(0.1, 20)

        # ==== metadata ====
        self.valid = False
        self.busy = False
        self.after_counter = 0
        # active command, etc?
        # coutner
        # csv file handle?

        #EKF
        self.P = np.eye(3)*0.001
