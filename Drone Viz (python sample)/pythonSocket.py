import socket
import time

ip = '127.0.0.1'
port = 12340

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ip, port))
s.listen(1)
conn, addr = s.accept()
print('Connection address:', addr)

i = 0
while (i < 5):
	time.sleep(1)
	conn.send(b"m,1,1,1,0\n")
	time.sleep(1)
	conn.send(b"p,0.2,0,0,20\n")
	time.sleep(1)
	conn.send(b"m,2,2,2,30\n")
	time.sleep(1)
	conn.send(b"p,0,0,0,0\n")
	i+=1
	
conn.close()


s.close()