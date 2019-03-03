import slam2
import socket
import time
import logging



# Drone/Node server
ip = '127.0.0.1'
port = 1337

# connect to node server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (ip, port)
s.connect(server_address)
s.setblocking(0)

fig = plt.figure()
ax = fig.gca(projection='3d')
xs = []


iteration = 0
while True:
    iteration += 1
    i += 1
    try:
        raw = s.recv(4096)
        payloadJSON = json.loads(raw)
        if payloadJSON["command"] == "ra":
            acc = [float(payloadJSON['accelerometers']['x'])/100 , float(payloadJSON['accelerometers']['y'])/100, float(payloadJSON['accelerometers']['z'])/100]
            rot = [float(payloadJSON['leftRightDegrees'])*(math.pi/180), float(payloadJSON['frontBackDegrees'])*(math.pi/180), float(payloadJSON['clockwiseDegrees'])*(math.pi/180)]

            droneForward = [1,0,0]
            droneFCorr = correctForGrav(rot, droneForward)
            accCorr = correctForGrav(rot, acc)
            ax.clear()
            ax.quiver([0],[0],[0], [droneForward[0]],[droneForward[1]],[droneForward[2]], length=0.5, normalize=True )
            ax.quiver([0],[0],[0], [accCorr[0]],[accCorr[1]],[accCorr[2]], length=0.5, normalize=True )
            plt.show()
    except Exception as e:
        pass
