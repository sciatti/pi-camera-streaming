# Framerate Test/Blocking IO Test
import threading
import cv2
import time
from threading import Thread
from collections import deque
import numpy as np

def dual_thread_fps_test(fps_target, wait):
    print("Dual Thread Performance Test")
    video = cv2.VideoCapture(0)

    video.set(cv2.CAP_PROP_FPS, fps_target + 1)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 640.0)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480.0)
    print("Resolution: ", video.get(cv2.CAP_PROP_FRAME_WIDTH), video.get(cv2.CAP_PROP_FRAME_HEIGHT),
     " @ ", video.get(cv2.CAP_PROP_FPS), " FPS")

    #fourcc = cv2.VideoWriter_fourcc(*"H264")
    #_, frame = video.read()
    #dims = (frame.shape[1], frame.shape[0])

    global frameAvailable
    frameAvailable = False
    t2 = threading.Thread(target=getFrame, args=[fps_target, wait])
    t2.start()
    global stopVal
    global frame
    while stopVal != True:
        _, frame = video.read()
        frameAvailable = True


def single_thread_fps_test(fps_target, wait):
    print("Single Thread Performance Test")
    frameQueue = deque()
    video = cv2.VideoCapture(0)

    video.set(cv2.CAP_PROP_FPS, fps_target + 1)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 640.0)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480.0)
    print("Resolution: ", video.get(cv2.CAP_PROP_FRAME_WIDTH), video.get(cv2.CAP_PROP_FRAME_HEIGHT),
     " @ ", video.get(cv2.CAP_PROP_FPS), " FPS")
    #fourcc = cv2.VideoWriter_fourcc(*"H264")
    #_, frame = video.read()
    #dims = (frame.shape[1], frame.shape[0])

    while stopVal != True:
        _, frame = video.read()
        frameQueue.append(frame)
    print("Frames Expected", wait * fps_target, "Frames Gathered: ", len(frameQueue))

def getFrame(fps_target, wait):
    frameQueue = deque()
    global frameAvailable
    global frame
    global stopVal
    while stopVal != True:
        if frameAvailable:
            frameQueue.append(frame)
            frameAvailable = False
    print("Frames Expected", wait * fps_target, "Frames Gathered: ", len(frameQueue))


def no_set_fps_test(fps_target, wait):
    # using an incorrect fps target could be a hacky workaround
    print("Single Thread Performance Test, no fps target set")
    frameQueue = deque()
    video = cv2.VideoCapture(0)

    video.set(cv2.CAP_PROP_FPS, 60)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 640.0)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480.0)
    print("Resolution: ", video.get(cv2.CAP_PROP_FRAME_WIDTH), video.get(cv2.CAP_PROP_FRAME_HEIGHT),
     " @ ", video.get(cv2.CAP_PROP_FPS), " FPS")
    #fourcc = cv2.VideoWriter_fourcc(*"H264")
    _, frame = video.read()
    frameQueue.append(frame)
    #dims = (frame.shape[1], frame.shape[0])

    #print(frameQueue[0])

    while stopVal != True:
        _, frame = video.read()
        #print(frame)
        #print(cv2.compare(frameQueue[len(frameQueue) - 1], frame, cv2.CMP_EQ))
        if np.sum(cv2.compare(frameQueue[len(frameQueue) - 1], frame, cv2.CMP_EQ)) != 0:
            frameQueue.append(frame)
    print("Frames Expected", wait * fps_target + 1, "Frames Gathered: ", len(frameQueue))    

def readFrame1(video):
    global stopVal
    global f1
    while stopVal != True:
        f1 = video.read()

def readFrame2(video):
    global stopVal
    global f2
    while stopVal != True:
        f2 = video.read()

def tri_thread_fps_test(fps_target, wait):
    # a class based solution would make this much more elegant...
    print("Tri Thread Performance Test")
    video = cv2.VideoCapture(0)

    video.set(cv2.CAP_PROP_FPS, fps_target)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 640.0)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480.0)
    print("Resolution: ", video.get(cv2.CAP_PROP_FRAME_WIDTH), video.get(cv2.CAP_PROP_FRAME_HEIGHT),
     " @ ", video.get(cv2.CAP_PROP_FPS), " FPS")

    #fourcc = cv2.VideoWriter_fourcc(*"H264")
    #_, frame = video.read()
    #dims = (frame.shape[1], frame.shape[0])

    frameQueue = deque()

    t1 = threading.Thread(target=readFrame1, args=[video])
    t1.start()
    # time.sleep(1/70)
    # t2 = threading.Thread(target=readFrame2, args=[video])
    # t2.start()
    global stopVal
    global f1
    global f2
    while stopVal != True:
        if f1:
            frameQueue.append(f1)
            f1 = None
        # if f2:
        #     frameQueue.append(f2)
        #     f2 = None
    print("Frames Expected", wait * fps_target, "Frames Gathered: ", len(frameQueue))

f1 = None
f2 = None

def fps_test_driver():
    test_val = 30
    global stopVal
    wait = 15
    t1 = threading.Thread(target=single_thread_fps_test, args=[test_val, wait])
    t1.start()
    time.sleep(wait)
    stopVal = True
    time.sleep(1)
    stopVal = False
    t1 = threading.Thread(target=dual_thread_fps_test, args=[test_val, wait])
    print()
    t1.start()
    time.sleep(wait)
    stopVal = True
    time.sleep(1)
    stopVal = False
    t1 = threading.Thread(target=tri_thread_fps_test, args=[test_val, wait])
    print()
    t1.start()
    time.sleep(wait)
    stopVal = True

frame = None
frameAvailable = None
stopVal = False
fps_test_driver()