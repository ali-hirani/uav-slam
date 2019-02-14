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
    s1 = Sensor([0.05,0.], 0)

    d = Drone([s1])
    #d.draw()
    #plt.show()

    # top three cases need includecommandnun = 1
    #path = 'D:\\School\\fydp\\forward_flight_walk_test.csv'
    #path = 'D:\\School\\fydp\\backward_flight_walk_test.csv'
    path = 'D:\\School\\fydp\\in_place_landed_test.csv'
    #path = 'D:\\School\\fydp\\walk_to_wall_foward.csv'
    #path = 'D:\\School\\fydp\\walk_backwards_from_wall.csv'
    #path = 'D:\\School\\fydp\\rotate_on_wall.csv'
    #path = 'D:\\School\\fydp\\in_place_rotate_middle_of_square_room.csv'


    includeCommandNum = 1

    reader = csv.reader(open(path))

    count = 0
    xavg = 0
    yavg = 0
    times = []
    xvals = []
    yvals = []
    zvals = []

    numDepths = 0
    depths = []
    curDepthAverage = 0

    rots = []
    rotsfb = []
    rotslr = []

    for row in reader:
        if count != 0:
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
                xvals.append(float(row[3 + includeCommandNum])/100)

                yvals.append(float(row[4 + includeCommandNum])/100)
                zvals.append(float(row[5 + includeCommandNum])/100)
                rots.append(float(row[11+ includeCommandNum])*(-math.pi/180))
                rotsfb.append(float(row[9+ includeCommandNum])*(math.pi/180))
                rotslr.append(float(row[10+ includeCommandNum])*(math.pi/180))

                xavg += float(row[3 + includeCommandNum ])/100
                yavg += float(row[4 + includeCommandNum])/100
        count += 1


    time = []
    startTime = times[0]
    for t  in times:
        time.append((t - startTime) / 1000)
    dtavg = 0
    for i in range(1, len(time)):
        dtavg += time[i]-time[i-1]
    dtavg = dtavg/len(time)
    xavg = xavg/len(xvals)
    yavg =  yavg/len(xvals)
    #xavg = 0.422342627952
    #yavg = -0.207504419885
    #print(result)
    #for i in range(len(xvals)):
    #    xvals[i] = xvals[i]-xavg
    #    yvals[i] = yvals[i]-yavg
    #xvariance = np.var(xvals)
    #yvariance = np.var(yvals)
    xvariance = 0.01
    yvariance = 0.01

    xProper = []
    yProper = []
    zProper = []
    xCAvg = 0
    yCAvg = 0


    for cw, fb, lr, x, y, z in zip(rots, rotsfb, rotslr, xvals, yvals, zvals):
        theta =lr
        beta = fb
        alpha = cw

        R = np.array(
            [[math.cos(alpha)*math.cos(beta) , math.cos(alpha)*math.sin(beta)*math.sin(theta) - math.sin(alpha)*math.cos(theta) , math.cos(alpha)*math.sin(beta)*math.cos(theta) + math.sin(alpha)*math.sin(theta)],
            [ math.sin(alpha)*math.cos(beta) , math.sin(alpha)*math.sin(beta)*math.sin(theta) + math.cos(alpha)*math.cos(theta) , math.sin(alpha)*math.sin(beta)*math.cos(theta) - math.cos(alpha)*math.sin(theta)],
            [-1* math.sin(beta) ,math.cos(beta) * math.sin(theta)  , math.cos(beta) * math.cos(theta) ]]
        )

        det =  R[0][0]*(R[1][1]*R[2][2]-R[1][2]*R[2][1]) -R[0][1]*(R[1][0]*R[2][2]-R[1][2]*R[2][0]) +R[0][2]*(R[1][0]*R[2][1]-R[1][1]*R[2][0])
        print("det" , det)
        xc = x*R[0][0] + y*R[0][1] + z*R[0][2]
        yc = x*R[1][0] + y*R[1][1] + z*R[1][2]
        zc = x*R[2][0] + y*R[2][1] + z*R[2][2]

        xg = -9.81*R[0][2]
        yg = -9.81*R[1][2]
        zg = -9.81*R[2][2]

        xc = xc - xg
        yc = yc - yg
        xc = zc - zg
        #yc = y * math.cos(+lr)- z * math.sin(+lr)
        #zc = z * math.cos()
        xProper.append(xc)
        yProper.append(yc)

        print("angle " , fb)
        print("x: ", x)
        print("z: ", z)
        print("x - xcomp", x* math.cos(-fb))
        print("z - xcomp", z * math.sin(-fb))
        print("XC: ", xc)
        print("--------")
        xCAvg += xc
        yCAvg += yc
    xCAvg = xCAvg/len(xProper)
    yCAvg = yCAvg/len(xProper)

    for i in range(len(xvals)):
        xProper[i] = xProper[i]-xCAvg
        yProper[i] = yProper[i]-yCAvg


    print(xvariance)
    print(yvariance)
    print(dtavg)
    print("x",xavg)
    print("y",yavg)
    print("correctedx: " , xCAvg)
    print("correctedy: " , yCAvg)


    dt = dtavg

    # x is 6 and we use 2 meaUSREMENTS
    f = KalmanFilter (dim_x=6, dim_z=2)
    #posxy, velxy, accxy
    f.x = np.array([0., 0., 0.,0., 0, 0])
    # x vector * F will give you the next state estimate - based on equations of motion
    f.F = np.array([[1., 0. , dt, 0., 0.5*dt**2 , 0.], [0., 1. , 0., dt, 0. , 0.5*dt**2] , [0., 0.,1., 0., dt, 0. ], [0., 0.,0., 1., 0., dt ],[0.,0., 0.,0.,1., 0.],[0.,0., 0.,0.,0., 1.]])
    #measurment vector, basically keep acceleration
    f.H = np.array([[0.,0.,0.,0.,1., 0.], [0.,0.,0.,0.,0., 1.]])
    f.P = [[0.,0.,0.,0.,0., 0.],[0.,0.,0.,0.,0., 0.],[0.,0.,0.,0.,0., 0.],[0.,0.,0.,0.,0., 0.],[0.,0.,0.,0.,xvariance, 0.],[0.,0.,0.,0.,0., yvariance]]
    f.R = np.array([[0.5, 0], [0, 0.5]])
    #q = Q_discrete_white_noise(dim=3, dt=dt, var=0.4**2)
    f.Q = np.identity(6) * 0.1
    nvar = 0.08
    #f.Q = np.concatenate( (np.concatenate((Q_discrete_white_noise(dim=3, dt=dt, var=nvar), Q_discrete_white_noise(dim=3, dt=dt, var=nvar))), np.concatenate((Q_discrete_white_noise(dim=3, dt=dt, var=nvar), Q_discrete_white_noise(dim=3, dt=dt, var=nvar)))),axis=1)

    saver = Saver(f)
    for xval, yval in zip(xProper, yProper):
        z = [xval,yval]
        f.predict()
        f.update(z)
        saver.save()

    wallPointsx = []
    wallPointsy = []
    for i in range(0, len(rots)):
        d.rot = rots[i]
        #d.pos[0] = np.array(saver.x)[i,0]
        #d.pos[1] = np.array(saver.x)[i,1]
        p = depthToPoint(d, 0, depths[i])
        wallPointsx.append(p[0])
        wallPointsy.append(p[1])


    fig, axarr = plt.subplots(2, sharex=True)
    axarr[0].plot(time,  np.array(saver.x)[:,0]*0.1, label="posX")
    axarr[0].set_title('pos')
    axarr[0].plot(time,  np.array(saver.x)[:,1]*0.1, label="posy")
    axarr[0].legend()
    axarr[1].plot(time,  np.array(saver.x)[:,4], label="Estimated accX")
    axarr[1].set_title('acc')
    axarr[1].plot(time,  xProper, label="measured accX")
    axarr[1].plot(time,  np.array(saver.x)[:,5], label="Estimated accy")
    axarr[1].plot(time,  yProper, label="measured accy")
    axarr[1].legend()
    # axarr[2].plot(time, depths)
    # axarr[2].set_title('depth')
    # axarr[3].plot(time, rots)

    #axarr.plot(wallPointsx, wallPointsy)
    #axarr.plot(np.array(saver.x)[:,0]*0.02, np.array(saver.x)[:,1]*0.03)
    # axarr.set_ylim([-8,8])
    # axarr.set_xlim([-8,8])
    # axarr.grid(True)
    #axarr[4].plot(time, wallPointsy)

    fig.suptitle(path, fontsize=16)

    plt.show()
    #landmarkExtraction()
main()
