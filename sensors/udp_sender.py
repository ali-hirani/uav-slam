import socket
from sensors import VL6180X, TF_MINI_LIDAR 
import time
import sys
import serial
import atexit


UDP_IP = sys.argv[1] 
sensor_type = sys.argv[2]
UDP_PORT = 5005

if sensor_type == "1":
    sensor = VL6180X(1)

if sensor_type == "2":
    sensor = TF_MINI_LIDAR()

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

while True:

    sock.sendto(str(sensor.read_distance()), (UDP_IP, UDP_PORT))
    #print sensor.read_distance()
