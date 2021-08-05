import cv2
import time
from collections import deque

class stream:
    def __init__(self, fps, height, width):
        # Capturing video
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FPS, fps)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.video.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.stop = False
        self.frame_queue = deque()

    def run(self):
        print("Resolution: ", self.video.get(cv2.CAP_PROP_FRAME_WIDTH), self.video.get(cv2.CAP_PROP_FRAME_HEIGHT),
     " @ ", self.video.get(cv2.CAP_PROP_FPS), " FPS")

        st = time.time()
        z = 0
        c = 0
        while self.stop != True:
            if time.time() - st > 10:
                print(c, "frames found in", time.time() - st, "seconds")
                st = time.time()
                c = 0
            _, frame = self.video.read()
            self.frame_queue.appendleft(frame)
            c+=1
            z+=1
    
    def stop(self):
        self.stop = True
    
    def empty(self):
        return len(self.frame_queue) == 0

    def pop(self):
        if len(self.frame_queue) > 0:
	        return self.frame_queue.pop()
        else:
            return None

    def release(self):
        self.video.release()
