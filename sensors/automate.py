import sys
import telnetlib
from wireless import Wireless

def drone_connect():
        
    print "connecting to drone..."
    wireless = Wireless()
    res = wireless.connect(ssid='ardrone2_047592', password='')
    if not res:
        print "error connecting..."
        return

    print "connected. starting telnet"

    HOST = "192.168.1.1"
    tn = telnetlib.Telnet(HOST)
    command = 'killall udhcpd; iwconfig ath0 mode managed essid "Ashwin"; ifconfig ath0 192.168.43.50 netmask 255.255.255.0 up;'
    tn.write(command)
    tn.write("exit\n")

def network_connect():
    print "connecting to ssid: Ashwin"
    wireless = Wireless()
    res = wireless.connect(ssid='Ashwin', password='')
    if not res:
        print "error connecting..."

    print "connected. continue..."
def raspi_telnet():
    
    print "telnetting into raspi...."
    HOST="192.168.43.61"
    tn = telnetlib.Telnet(HOST)
    user = "pi"
    password = "testing123"

    tn.read_until("login: ")
    tn.write(user + "\n")
    if password:
        tn.read_until("Password: ")
        tn.write(password + "\n")

    print "running pigpiod..."
    tn.write("sudo pigpiod\n")
    tn.write("killall -KILL python\n")
    print "running tcp_sender.py..."
    command = "python Documents/fydp/tcp_sender.py\n" 
    print "SUCCESS: RUN TCP_RECEIVER.PY, SERVER IS LISTENING"
    tn.write(command)
    tn.write("exit\n")
    print tn.read_all()

# drone_connect()
network_connect()
raspi_telnet()

