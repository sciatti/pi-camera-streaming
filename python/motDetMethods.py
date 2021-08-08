# File Designed to test the methods of motion detection on around 5 seconds of footage
from collections import deque
import time
import cv2
import os

def get_video(cap, duration):
    stream = deque()
    for _ in range(duration * int(cap.get(cv2.CAP_PROP_FPS))):
        good, frame = cap.read()
        if good:
            stream.append(frame)
    return stream

def initCam():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 20)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640.0)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480.0)
    return cap

def getBG(cap):
    read, frame = cap.read()
    while not read:
        read, frame = cap.read()
    return frame

def subtractMethod(stream, background, dir):
    c = 0
    fourcc = cv2.VideoWriter_fourcc(*"H264")
    v = cv2.VideoWriter(os.path.join(dir, 'example.avi'), fourcc, 20, (640,480), True)
    for image in stream:
        diff = background - image
        cv2.imwrite(os.path.join(dir, str(c) + ".png"), diff)
        v.write(diff)
        c+=1

def countdown():
    start = time.time()
    for i in range(5, 0, -1):
        while time.time() - start < 1:
            #keep waiting
            time.sleep(0.1)
        print(i)
        start = time.time()

def main():
    cap = initCam()
    background = getBG(cap)
    input("Type Aything To Start The Test:")
    countdown()
    dir = str(int(time.time()))
    if not os.path.exists(dir):
        os.mkdir(dir)
    stream = get_video(cap, 5)
    subtractMethod(stream, background, dir)

if __name__ == "__main__":
    main()