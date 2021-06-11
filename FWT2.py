# File Write Test 2
import cv2
import time

video = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*"H264")
_, frame = video.read()
dims = (frame.shape[1], frame.shape[0])
time.sleep(0.2)
v = cv2.VideoWriter('test.avi', fourcc, 5, dims, True)
for i in range(25):
    _, frame = video.read()
    v.write(frame)
    time.sleep(0.2)