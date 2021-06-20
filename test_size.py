import socket
import sys
import cv2
import pickle
import struct ## new


cap=cv2.VideoCapture(0)
while True:
    ret,frame=cap.read()
    #frame = cv2.resize(frame, (100, 100))
    data = pickle.dumps(frame) ### new code
    print('len of data: ', len(data))
    x = struct.pack("H", len(data))
