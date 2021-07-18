import cv2
from collections import deque
import threading
import time

# testing how many frames a second we can grab
# and add to a list or deque on a single raspberry pi 3 B+ thread
def single_thread_fps_grab(Lst, video):
    frame_stack = None
    if Lst:
        frame_stack = []
    else:
        frame_stack = deque()
    # bring in static stop value
    global stop_threads
    # use the stop_threads value to check whether we need to stop yet
    while stop_threads == False:
        _, frame = video.read()
        frame_stack.append(frame)
    printPerformance(frame_stack) 

def printPerformance(frame_stack):
    print("expected frames gathered ", str(10*cv2.CAP_PROP_FPS), " actual frames gathered ", str(len(frame_stack)))

def FpsGrabDriver():
    global stop_threads
    # init camera
    video = cv2.VideoCapture(0)
    stop_threads = False
    t1 = threading.Thread(target = single_thread_fps_grab, args=[True, video])
    t1.start()
    time.sleep(10)
    stop_threads = True

    stop_threads = False
    t1 = threading.Thread(target = single_thread_fps_grab, args=[False, video])
    t1.start()
    time.sleep(10)
    stop_threads = True

stop_threads = None
#FpsGrabDriver()

def TestFpsMatching():
    cnt = 0
    video = cv2.VideoCapture(0)
    frame_stack = deque()
    while cnt < 5*4:
        check, frame = video.read()
        frame_stack.append(frame)
        time.sleep(1/5)
        cnt += 1
    cnt = 0
    for frame in frame_stack:
        cv2.imwrite('imgs/exp' + str(cnt) + '.jpg', frame)
        cnt+=1
x = 5
for i in range(5):
    print(str(x))
    x-=1
    time.sleep(1)
TestFpsMatching()
    