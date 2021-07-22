# Robust Motion Detection Test File
# Python program to implement
# Webcam Motion Detector

# importing OpenCV, time libraries
from types import FrameType
import cv2
import time
import atexit
from collections import deque
import threading

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
            self.frame_queue.appendleft((frame, z))
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

def cleanUp(video):
    video.release()

    # Destroying all the windows
    cv2.destroyAllWindows()

def detect_motion(cameraStream, static_back):
    motion = False
    #TODO: rewrite this as something intelligent, bozo
    while cameraStream.empty():
        time.sleep(0.01)
    frame = cameraStream.pop()
    # Converting color image to gray_scale image
    gray = cv2.cvtColor(frame[0], cv2.COLOR_BGR2GRAY)
    # Converting gray scale image to GaussianBlur
    # so that change can be find easily
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Difference between static background
    # and current frame(which is GaussianBlur)
    diff_frame = cv2.absdiff(static_back, gray)

    # If change in between static background and
    # current frame is greater than 30 it will show white color(255)
    thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
    thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)

    # Finding contour of moving object
    cnts,_ = cv2.findContours(thresh_frame.copy(),
                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in cnts:
        if cv2.contourArea(contour) < 10000:
            continue
        motion = True

        (x, y, w, h) = cv2.boundingRect(contour)
        # making green rectangle arround the moving object
        cv2.rectangle(frame[0], (x, y), (x + w, y + h), (0, 255, 0), 3)
    return motion, frame

def write_queue(frame_queue):
    fourcc = cv2.VideoWriter_fourcc(*"H264")
    name = str(int(time.time()))
    #v = cv2.VideoWriter(name + '.avi', fourcc, video.get(cv2.CAP_PROP_FPS), (video.get(cv2.CAP_PROP_FRAME_WIDTH), video.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    v = cv2.VideoWriter(name + '.avi', fourcc, 30, (640, 480))
    c=0
    f = open(name, 'w') 
    while len(frame_queue) != 0:
        frame = frame_queue.pop()
        v.write(frame[0])
        f.write(str(frame[1]) + "\n")
        c+=1
    print("wrote file: ", name + ".avi with", c, "frames")
    
def simple(cameraStream):
	cameraStream.run()

def simple2(frame_queue):
    write_queue(frame_queue)

def motion_capture():
    cameraStream = stream(30, 480.0, 640.0)
    threads = []
    threads.append(threading.Thread(target=simple, args=[cameraStream]))
    threads[0].start()
	# video = cv2.VideoCapture(0)
    # video.set(cv2.CAP_PROP_FPS, 30)
    # video.set(cv2.CAP_PROP_FRAME_WIDTH, 640.0)
    # video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480.0)

    atexit.register(cleanUp, cameraStream)

    frame_queue = deque()

    #create the background frame
    # Read the first frame from video
    #check, frame = video.read()
    #TODO: rewrite this as something intelligent, bozo
    while cameraStream.empty():
        time.sleep(0.01)
        #print("empty")
    print(len(cameraStream.frame_queue))
    print(cameraStream.empty())
    frame = cameraStream.pop()
    #dims = (frame.shape[0], frame.shape[1])
    # Converting color image to gray_scale image
    gray = cv2.cvtColor(frame[0], cv2.COLOR_BGR2GRAY)

    # Converting gray scale image to GaussianBlur
    # so that change can be found easily
    static_back = cv2.GaussianBlur(gray, (21, 21), 0)
    
    stop_motion_time = 0
    start_motion_time = 0
    motion_time = 0
    motion_last_frame = False
    motion = False
    swappedBG = True
    clear_threads = time.time()
    while True:
        if time.time() - clear_threads > 30:
            print("searching threads list for dead threads")
            for i in range(len(threads)):
                if not threads[i].is_alive():
                    threads.pop(i)
            clear_threads = time.time()
        motion, frame = detect_motion(cameraStream, static_back)
        if motion:
            swappedBG = False
            motion_time = time.time()
            if not motion_last_frame:
                start_motion_time = motion_time
            if motion_time - start_motion_time > 10:
                # Change BG photo because there has been motion detected for a continuous 10 seconds
                static_back = cv2.GaussianBlur(cv2.cvtColor(frame[0], cv2.COLOR_BGR2GRAY), (21,21), 0)
            frame_queue.appendleft(frame)
            print("appended frame from motion")
        else:
            if motion_last_frame:
                print("found motion last frame", time.time())
                stop_motion_time = time.time()
            elif (time.time() - stop_motion_time) < 2.0:
                frame_queue.appendleft(frame)
                print('appending frame from no motion', time.time(), stop_motion_time)
            else:
                # We can stop collecting frames and write out to the file
                if len(frame_queue) > 0:
                    if not threads[-1].is_alive():
                        threads.pop(-1)
                    print("spawning write out thread")
                    shadow_queue = frame_queue
                    frame_queue = deque()
                    threads.append(threading.Thread(target=simple2, args=[shadow_queue]))
                    threads[-1].start()
                # Eligible to change the BG photo after 10 seconds without motion
                if time.time() - stop_motion_time > 10 and not swappedBG:
                    # Change the BG photo because we've went 10 seconds without new motion
                    static_back = cv2.GaussianBlur(cv2.cvtColor(frame[0], cv2.COLOR_BGR2GRAY), (21,21), 0)
                    swappedBG = True

        motion_last_frame = motion
    
    # # Infinite while loop to treat stack of image as video
    # while True:
    #     before = motion
    #     motion = False
    #     # Reading frame(image) from video
    #     check, frame = video.read()

    #     # Converting color image to gray_scale image
    #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #     # Converting gray scale image to GaussianBlur
    #     # so that change can be find easily
    #     gray = cv2.GaussianBlur(gray, (21, 21), 0)

    #     # Difference between static background
    #     # and current frame(which is GaussianBlur)
    #     diff_frame = cv2.absdiff(static_back, gray)

    #     # If change in between static background and
    #     # current frame is greater than 30 it will show white color(255)
    #     thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
    #     thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)

    #     # Finding contour of moving object
    #     cnts,_ = cv2.findContours(thresh_frame.copy(),
    #                     cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #     for contour in cnts:
    #         if cv2.contourArea(contour) < 10000:
    #             continue
    #         motion = True

    #         (x, y, w, h) = cv2.boundingRect(contour)
    #         # making green rectangle arround the moving object
    #         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

    #     # if we have something detected on screen
    #     if motion == True:
    #     # Appending current frame which has motion in it to the frame array
    #         frame_queue.append(frame)
    #         print("motion detected")
    #         if before == False:
    #             st = time.time()
    #         #time.sleep(1/15)

    #     # if we dont have something detected on screen
    #     elif motion == False and time.time() - st > 1.5 and len(frame_queue) > 0:
    #         # motion has stopped, append this frame to the stack then write it out to disk and clear the stack
    #         frame_queue.append(frame)
    #         #v = cv2.VideoWriter(str(int(time.time())) + '.mp4', cv2.VideoWriter_fourcc('f', 'f', 'v', '1'), cv2.CAP_PROP_FPS, frame_queue[0].shape, True)
    #         fname = str(int(time.time()))
    #         print(dims)
    #         v = cv2.VideoWriter(fname + '.avi', fourcc, 30, dims, True)
    #         # Define the codec and create VideoWriter object
    #         print(frame.shape)
    #         x = len(frame_queue)
    #         for i in range(x):
    #             f = frame_queue.popleft()
    #             v.write(f)
    #         print("Wrote File: ", fname, ".avi with ", x, " frames.")
    #         frame_queue = deque()
    #         #time.sleep(1/18)

    #     elif motion == False and time.time() - st < 1.5 and len(frame_queue) > 0:
    #         frame_queue.append(frame)
    #         #time.sleep(1/15)

def main():
    motion_capture()

if __name__ == "__main__":
    main()