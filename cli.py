import cv2
import numpy as np
import socket
import sys
import pickle
import struct ### new code

HOST=''
PORT=8089

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print('Socket created')

s.bind((HOST,PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')

conn,addr=s.accept()

cap=cv2.VideoCapture(0)

while True:
    ret,frame=cap.read()
    data = pickle.dumps(frame) ### new code
    conn.sendall(struct.pack("H", len(data))+data) ### new code
