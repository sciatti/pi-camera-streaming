import socket
import sys
import cv2
import pickle
import numpy as np
import struct ## new
import time
import atexit

def cleanUp(sock):
    print('closing socket')
    sock.close()
    print('socket closed')

HOST=socket.gethostbyname(socket.gethostname() + '.local')
PORT=8089

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print('Socket created')

s.bind((HOST,PORT))
print('Socket bound to ', (HOST,PORT))
s.listen(10)
print('Socket now listening')

conn,addr=s.accept()

atexit.register(cleanUp, conn)

cap=cv2.VideoCapture(0)
while True:
    ret,frame=cap.read()
    frame = cv2.resize(frame, (100, 100))
    data = pickle.dumps(frame) ### new code
    print('len of data: ', len(data))
    x = struct.pack("H", len(data))
    conn.sendall(x+data) ### new code
    # send frames 16 times every second 
    time.sleep(0.0625)
    # TODO: Figure out a better way to record at 16 fps?
