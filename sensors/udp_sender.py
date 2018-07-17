import socket
from sensors import VL6180X 
import time
import sys
import serial


UDP_IP = sys.argv[1] 
UDP_PORT = 5005
sensor = VL6180X(1)

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP


while True:
    sock.sendto(str(sensor.read_distance()), (UDP_IP, UDP_PORT))
