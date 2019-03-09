import telnetlib

HOST = "192.168.1.1"
tn = telnetlib.Telnet(HOST)
tn.write("reboot\n")