import socket
import time

ip = '127.0.0.1'
port = 1337

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (ip, port)
s.connect(server_address)


# i = 0
# while (i < 5):
# 	time.sleep(1)
# 	s.sendall(b"to")
# 	#time.sleep(1)
# 	#conn.send(b"p,0.2,0,0,20\n")
# 	#time.sleep(1)
# 	#conn.send(b"m,2,2,2,30\n")
# 	#time.sleep(1)
# 	#conn.send(b"p,0,0,0,0\n")
# 	i+=1
# 	# Look for the response
	

# 	data = s.recv(4096)
# 	print(data);

time.sleep(1)
s.sendall(b"to")

data = s.recv(4096)
print(data)

time.sleep(5)
s.sendall(b"fo-1")
data = s.recv(4096)
print(data)

s.sendall(b"ra")
data = s.recv(4096)
print(data)

time.sleep(5)
s.sendall(b"la")

data = s.recv(4096)
print(data)

s.close()