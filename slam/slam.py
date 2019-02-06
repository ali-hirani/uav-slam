#from scipy import stats
import numpy as np
import math
import matplotlib.pyplot as plt

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

def main():
    s1 = Sensor([0.05,0.1], -0.1*math.pi)
    s2 = Sensor([0.1,0.1],  -0.2*math.pi)
    s3 = Sensor([-0.05,0.1],  0.1*math.pi)
    s4 = Sensor([-0.1,0.1],  0.2*math.pi)
    d = Drone([s1,s2,s3,s4])
    d.rot = math.pi/2
    d.draw()
    plt.show()
    #landmarkExtraction()
main()
