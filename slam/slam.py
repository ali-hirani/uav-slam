#from scipy import stats
import numpy as np
import math
import matplotlib.pyplot as plt
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
from filterpy.common import Saver
import csv

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
    #d.draw()
    #plt.show()

    reader = csv.reader(open('D:\\School\\fydp\\in_place_landed_test.csv'))
    result = {}
    count = 0
    xavg = 0
    yavg = 0
    xvals = []
    yvals = []
    zvals = []
    for row in reader:
        if count != 0:
            key = count
            result[key] = row[1:]
            xvals.append(float(row[4])/100)
            xavg += float(row[4])/100
            yvals.append(float(row[5])/100)
            yavg += float(row[5])/100
        count += 1
    #xavg = xavg/(count-2)
    xavg = 0.422342627952
    #print(result)
    for i in range(len(xvals)):
        xvals[i] = xvals[i]-xavg
    #variance = np.var(xvals)
    variance = 0.0012499780148043122
    print(variance)
    print(xavg)


    dt = 0.005

    f = KalmanFilter (dim_x=3, dim_z=1)
    #pos, vel, acc
    f.x = np.array([0., 0., 0.])
    f.F = np.array([[1.,dt, 0.5*dt**2],[0.,1., dt],[0.,0.,1.]])
    f.H = np.array([[0.,0., 1.]])
    f.P = [[0,    0,      0], [  0,  0,      0],[  0,    0,  variance]]
    f.R = np.array([[0.5]])
    f.Q = Q_discrete_white_noise(dim=3, dt=dt, var=variance)

    saver = Saver(f)
    for val in xvals:
        z = val
        f.predict()
        f.update(z)
        saver.save()

    time = []
    startTime = float(result[1][0])
    for key, value in result.iteritems():
        time.append((float(value[0]) - startTime) / 1000)


    idkWhatThisIs, axarr = plt.subplots(3, sharex=True)
    axarr[0].plot(time,  np.array(saver.x)[:,0])
    axarr[1].plot(time,  np.array(saver.x)[:,1])
    axarr[2].plot(time,  np.array(saver.x)[:,2], label="Estimated accX")
    axarr[2].plot(time,  xvals, label="measured accX")
    axarr[2].legend()

    plt.show()
    #landmarkExtraction()
main()
