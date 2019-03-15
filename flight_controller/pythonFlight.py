import ps_drone as ARDrone
import socket
import threading
import struct
import time
from threading import Thread

#print "is drone flying: " + str(is_drone_flying)
#print "timestamp: " + str(drone.NavDataTimeStamp)
#print "included packages: " + str(drone.NavData.keys())
#print "state: " + str(drone.State)
#print "demo-data: " + str(drone.NavData["demo"])

def initDrone(drone):
    drone = ARDrone.Drone()
    drone.startup()
    drone.reset()
    time.sleep(1)
    drone.trim()
    drone.useDemoMode(True)
    drone.getNDpackage(["demo"])
    is_drone_flying = drone.NavData["demo"][0][2]

    return drone

#SOCKET FROM PI TO LAPTOP -- END
#DRONE CONTROL --- START
def package_drone_data():
    timeStamp = drone.NavDataTimeStampphysical_meas = drone.NavData["phys_measures"]
    velocity = drone.NavData["demo"][4]
    angles = drone.NavData["demo"][2]
    physical_meas = drone.NavData["phys_measures"]
    accs_temp = physical_meas[0]
    gyro_temp = physical_meas[1]
    phys_accs = physical_meas[2]
    x_accel = phys_accs[0]
    y_accel = phys_accs[1]
    z_accel = phys_accs[2]
    phys_gyros = physical_meas[3]
    x_gyros = phys_gyros[0]
    y_gyros = phys_gyros[1]
    z_gyros = phys_gyros[2]
    velocity_x = velocity[0]
    velocity_y = velocity[1]
    velocity_z = velocity[2]
    pitch = angles[0]
    roll = angles[1]
    yaw = angles[2]

def takeoff():
    global global_busy
    
    print("takeoff begin")
    global_busy = True
    print "doing trim + self rotation"
    drone.getSelfRotation(5)
    print("self-rotation_value:  " + str(drone.selfRotation))
    time.sleep(1)
    drone.setSpeed(0.1)
    time.sleep(0.1)
    print "prepare for takeoff"
    drone.takeoff()
    #wait till drone is actually flying
    time.sleep(5)

    global_busy = False
    print("takeoff end")

def do_square():
    counter = 1

    while counter <= 4:
        move_drone("front", 0.1, 1)
        move_drone("left", 0.1, 2)
        move_drone("back", 0.1, 1)
        move_drone("right", 0.1, 2)
        counter += 1

def do_square_angled():
    counter = 1
    while counter <= 4:
        drone.hover()
        time.sleep(0.5)
        drone.moveForward(0.1)
        time.sleep(1)
        drone.stop()
        time.sleep(0.5)
        drone.turnAngle(-90, 1, 10)
        time.sleep(0.5)
        drone.hover()
        time.sleep(2)
        counter += 1

def move_drone(direction,speed, period):
    global global_busy
    
    global_busy = True
    
    if direction == "front":
        print "moving forward"
        drone.moveForward(speed)
        time.sleep(period)
        drone.stop()
        time.sleep(2)


    elif direction == "back":
        print "moving backward"
        drone.moveBackward(speed)
        time.sleep(period)
        drone.stop()
        time.sleep(2)

    elif direction == "right":
        print "moving right"
        drone.moveRight(speed)
        time.sleep(period)
        drone.stop()
        time.sleep(2)

    elif direction == "left":
        print "moving left"
        drone.moveLeft(speed)
        time.sleep(period)
        drone.stop()
        time.sleep(2)

    global_busy = False
 

#do 360 deg rotation in 8 steps
def do_rotation():
    global global_busy

    global_busy = True
    counter = 1
    while counter <= 8:
        drone.hover()
        time.sleep(0.5)
        drone.turnAngle(-45, 1, 1)
        drone.hover()
        time.sleep(2)
        counter += 1
    global_busy = False

def helloWorld(arg):
    for x in xrange(1,100):
        print("fuck you" + str(arg))

# thread = Thread(target = takeoff)
# thread.start()

# while (global_busy) :
#     print("busy")
#     pass

# thread = Thread(target = drone.land())
# thread.start()


#move_drone("right", 0.1, 1)
#kjjjhhdo_rotation()
#do_square_angled()
#do_square()
# do_rotation()
# drone.land()

#(sensor_id, distance) = encoded_data
#print("sensor_id: ", sensor_id)
#print("distance: ", distance)
