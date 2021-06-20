# Framerate Test/Blocking IO Test
import threading
import cv2
import time
from threading import Thread
from collections import deque

def fps_test():
    frameQueue = []
    video = cv2.VideoCapture(0)
    video.set(cv2.CAP_PROP_FPS, 30)
    print(cv2.CAP_PROP_FPS)
    #fourcc = cv2.VideoWriter_fourcc(*"H264")
    #_, frame = video.read()
    #dims = (frame.shape[1], frame.shape[0])
    frameCount = 0

    global frameAvailable
    frameAvailable = False
    t2 = threading.Thread(target=getFrame)
    t2.start()
    global stopVal
    global frame
    while stopVal != True:
        _, frame = video.read()
        frameAvailable = True

def getFrame():
    frameQueue = deque()
    global frameAvailable
    global frame
    global stopVal
    while stopVal != True:
        if frameAvailable:
            frameQueue.append(frame)
            frameAvailable = False
    print("Frames Expected", 5 * 30, "Frames Gathered: ", len(frameQueue))


def fps_test_driver():
    global stopVal
    t1 = threading.Thread(target=fps_test)
    t1.start()
    time.sleep(5)
    stopVal = True

frame = None
frameAvailable = None
stopVal = False
fps_test_driver()