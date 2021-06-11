import cv2
import numpy as np
import socket
import sys
import pickle
import struct ### new code
clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsocket.connect(('192.168.0.140',8089))
### new
data = bytes()
payload_size = struct.calcsize("I") 
cnt = 0
while True:
    while len(data) < payload_size:
        data = data + clientsocket.recv(4096)
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    x = struct.unpack("I", packed_msg_size)
    msg_size = x[0]
    print(x)
    while len(data) < msg_size:
        data = data + clientsocket.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]
    ###

    frame=pickle.loads(frame_data)
    cv2.imshow('frame',frame)
    cv2.waitKey(1)
    #cv2.imwrite('frame' + str(cnt) + '.jpg', frame)
    cnt+=1
