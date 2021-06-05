import socket
import sys
import cv2
import pickle
import numpy as np
import struct ## new

HOST=''
PORT=8089

clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsocket.connect(('localhost',8089))

### new
data = ""
payload_size = struct.calcsize("H") 
while True:
    while len(data) < payload_size:
        data += clientsocket.recv(4096)
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("H", packed_msg_size)[0]
    while len(data) < msg_size:
        data += clientsocket.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]
    ###

    frame=pickle.loads(frame_data)
    print(frame)
    cv2.imshow('frame',frame)