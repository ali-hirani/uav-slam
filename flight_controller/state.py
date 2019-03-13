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
        self.landmarks = []

        # ==== metadata ====
        self.valid = False
        self.busy = False
        self.after_counter = 0
        # active command, etc?
        # coutner
        # csv file handle?
