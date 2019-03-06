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

class Landmark:
    def __init__(self, xy):
        self.xy = xy

class State:
    def __init__(self, drone):
        self.drone = drone
        self.landmarks = []
