import socket
import struct


TCP_IP = "192.168.43.242"
TCP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))

def collect_packet(sock, size):
    data = b''
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None

        data = data + packet

    return data

def decode_data(sock):
    #first get the length of packet from first 4 bytes
    packet_length_bytes = collect_packet(sock , 4)
    if not packet_length_bytes:
        return None

    packet_length = struct.unpack('>I', packet_length_bytes)[0]

    encoded_data = collect_packet(sock, packet_length)
    pair = (encoded_data[0], encoded_data[1:])

    return pair

while True:
    encoded_data = decode_data(sock)
    (sensor_id, distance) = encoded_data
    print("Sensor ID: ", sensor_id)
    print("Distance in cm: ", distance)
