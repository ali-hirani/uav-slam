import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import csv

"""
Pseudocode:

def kalman(currentState, acceleration, landmark):

def removeGravity(currentState, acceleration) -> returns x,y acceleration
def removeTilt(tilt, depths) -> returns depths corrected into xy plane

better flight

lines?
landmark recognition/asociation
    -see point, is it a part of a current wall or a new wall
    -update wall

landmakr ascosciation

navigation:
-converting landmarks to "usable data"
-making navigation desisions
-emergency stop

make it actually realtime
"""

def depthToPoint(drone, sensorIndex, depth):
    p1 = np.add(drone.sensors[sensorIndex].offset, [drone.pos[0], drone.pos[1]])
    p2 = [p1[0], p1[1]+depth]
    p2 = rotate(p1, p2, drone.sensors[sensorIndex].angle)
    #p1 = rotate([self.pos[0], self.pos[1]], p1, self.rot)
    p2 = rotate([drone.pos[0], drone.pos[1]], p2, drone.rot)
    return p2

"""
3/4 of a drone...
         ^
       front    -angle
         |     | /
     ___ | ___ |/
   /    \|/   \s
  |  X   |  X  |
   \     |    /
-------------------->
         |    \
     X   |  X  |
         |\___/
"""
class Sensor:
    def __init__(self, offset, angle):
        self.offset = offset
        self.angle = angle

class Drone:
    def __init__(self, sensors):
        self.sensors = sensors
        self.pos = [0,0,0]
        self.rot = 0
    def draw(self):
        #draw drone center
        plt.scatter(self.pos[0], self.pos[1], c='k')
        for i in range(0,4):
            p1 = np.add(self.sensors[i].offset, [self.pos[0], self.pos[1]])
            p1 = rotate([self.pos[0], self.pos[1]], p1, self.rot)
            p2 = depthToPoint(self, i, 0.05)
            plt.scatter(p1[0], p1[1], c='k')
            #plt.scatter(p2[0], p2[1], c='k')
            plt.plot([p1[0],p2[0]], [p1[1],p2[1]], c='k')

class TestRun:
    def __init__(self, time, acceleration, rotation, depth):
        self.time = time
        # each acceleration is [x,y,z]
        self.acceleration = acceleration
        #each rot is [rotation around x, rot round y, rot around z] in rads
        self.rotation = rotation
        #each depth is [d from s1, d from s2, ...] in m
        self.depth = depth

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

def rotateAroundZ(vector, rads):
    cos = math.cos(rads)
    sin = math.sin(rads)
    rotMat = np.array([[cos, sin, 0] , [-sin, cos, 0], [0,0,1]])
    return np.dot(rotMat, vector)

def rotateAroundY(vector, rads):
    cos = math.cos(rads)
    sin = math.sin(rads)
    rotMat = np.array([[cos, 0, -sin] , [0, 1, 0], [sin,0,cos]])
    return np.dot(rotMat, vector)

def rotateAroundX(vector, rads):
    cos = math.cos(rads)
    sin = math.sin(rads)
    rotMat = np.array([[1, 0, 0] , [0, cos, -sin], [0,sin,cos]])
    return np.dot(rotMat, vector)

def readFile(path):
    # top three cases need includecommandnun = 1
    #path = 'D:\\School\\fydp\\forward_flight_walk_test.csv'
    #path = 'D:\\School\\fydp\\backward_flight_walk_test.csv'
    #path = 'D:\\School\\fydp\\in_place_landed_test.csv'
    #path = 'D:\\School\\fydp\\walk_to_wall_foward.csv'
    #path = 'D:\\School\\fydp\\walk_backwards_from_wall.csv'
    path = 'D:\\School\\fydp\\rotate_on_wall.csv'
    #path = 'D:\\School\\fydp\\in_place_rotate_middle_of_square_room.csv'

    includeCommandNum = 0

    reader = csv.reader(open(path))

    #builds list of measurments
    count = 0
    depths = []
    accels = []
    rots = []
    times = []
    numDepths = 0
    curDepthAverage = 0

    for row in reader:
        #disregard the first row
        if count != 0:
            # keep track of depth
            if row[0] == "depth":
                curDepthAverage += float(row[2])/100
                numDepths += 1
            else:
                if(numDepths != 0):
                    depths.append(curDepthAverage/numDepths)
                else:
                    depths.append(-1)
                numDepths = 0
                curDepthAverage = 0

                times.append(float(row[includeCommandNum]))
                accels.append([float(row[3 + includeCommandNum])/100, float(row[4 + includeCommandNum])/100 ,float(row[5 + includeCommandNum])/100])
                #TODO is this the right way to do this?
                rots.append( [float(row[10+ includeCommandNum])*(math.pi/180), float(row[9+ includeCommandNum])*(math.pi/180), float(row[11+ includeCommandNum])*(math.pi/180)])
        count += 1
    return TestRun(times, accels, rots, depths)


def correctForGrav(rots, accel):
    newVec = rotateAroundY(accel, rots[1])
    newVec = rotateAroundX(newVec, rots[0])


    newVec = rotateAroundZ(newVec, rots[2])


    #newVec = newVec + [0,0,9.7]
    return newVec

def main():
    testRun = readFile("test")
    mags = []
    for a in testRun.acceleration:
        mag = math.sqrt(a[0]**2 + a[1]**2 + a[2]**2 )
        print(mag)
        mags.append(mag)

    newAccs = []
    for i in range(0, len(testRun.acceleration)):
        newAccs.append(correctForGrav(testRun.rotation[i], testRun.acceleration[i]))

    newMags = []
    for a in newAccs:
        mag = math.sqrt(a[0]**2 + a[1]**2 + a[2]**2 )
        print(mag)
        newMags.append(mag)
    fig, axarr = plt.subplots(2, sharex=True)


    droneForward = [1,0,0]
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.quiver([0],[0],[0], [testRun.acceleration[0][0]],[testRun.acceleration[0][1]],[testRun.acceleration[0][2]], length=0.5, normalize=True )
    ax.quiver([0],[0],[0], droneForward[0],droneForward[1] , droneForward[2], length=0.5, normalize=True )
    newVec = rotateAroundZ(testRun.acceleration[0], testRun.rotation[0][2])
    newVec = rotateAroundY(newVec, testRun.rotation[0][1])
    newVec = rotateAroundX(newVec, testRun.rotation[0][0])
    newVecF = rotateAroundZ(droneForward, testRun.rotation[0][2])
    newVecF = rotateAroundY(newVecF, testRun.rotation[0][1])
    newVecF = rotateAroundX(newVecF, testRun.rotation[0][0])
    newVec = newVec - [0,0,9.8]
    ax.quiver([0],[0],[0], [newVec[0]],[newVec[1]],[newVec[2]], length=0.5, normalize=True, color='green' )
    ax.quiver([0],[0],[0], [newVecF[0]],[newVecF[1]],[newVecF[2]], length=0.5, normalize=True, color='green' )

    # make simple, bare axis lines through space:
    xAxisLine = ((-1, 1), (0, 0), (0,0))
    ax.plot(xAxisLine[0], xAxisLine[1], xAxisLine[2], 'r')
    yAxisLine = ((0, 0), (-1, 1), (0,0))
    ax.plot(yAxisLine[0], yAxisLine[1], yAxisLine[2], 'r')
    zAxisLine = ((0, 0), (0,0), (-1, 1))
    ax.plot(zAxisLine[0], zAxisLine[1], zAxisLine[2], 'r')

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    plt.show()

#main()
