import time
import ps_drone as ARDrone

drone = ARDrone.Drone()
drone.startup()
drone.reset()
time.sleep(1)
print "Battery: "+str(drone.getBattery()[0])+"%  "+str(drone.getBattery()[1])
