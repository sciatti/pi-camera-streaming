# File Write Test
import cv2
import time
from picamera import PiCamera
from picamera.array import PiRGBArray

camera = PiCamera()
rawCapture = PiRGBArray(camera, size=(640, 480))
camera.resolution = (640, 480)
camera.framerate = 5
count = 0
fourcc = cv2.VideoWriter_fourcc(*"H264")
v = cv2.VideoWriter('test.avi', fourcc, 5, camera.resolution, True)
time.sleep(0.1)
for frame in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
    if count >= 25: break 
    v.write(frame.array)
    count += 1
    rawCapture.truncate(0)
    time.sleep(0.2)