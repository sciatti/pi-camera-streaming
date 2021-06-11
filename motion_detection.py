# Python program to implement
# Webcam Motion Detector

# importing OpenCV, time libraries
import cv2
import time
import atexit
from collections import deque

def motion_capture():
    fourcc = cv2.VideoWriter_fourcc(*"H264")
    frame_queue = deque()
    # Capturing video
    video = cv2.VideoCapture(0)

    atexit.register(cleanUp, video)

    #create the background frame
    # Read the first frame from video
    check, frame = video.read()
    dims = (frame.shape[1], frame.shape[0])
    # Converting color image to gray_scale image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Converting gray scale image to GaussianBlur
    # so that change can be found easily
    static_back = cv2.GaussianBlur(gray, (21, 21), 0)
    time.sleep(0.2)
    # Infinite while loop to treat stack of image as video
    while True:
        motion = False
        # Reading frame(image) from video
        check, frame = video.read()

        # Converting color image to gray_scale image
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        # if we have something detected on screen
        if motion == True:
        # Appending current frame which has motion in it to the frame array
            frame_queue.append(frame)
            print("motion detected")
            time.sleep(1/15)

        # if we dont have something detected on screen
        elif motion == False and len(frame_queue) > 0:
            # motion has stopped, append this frame to the stack then write it out to disk and clear the stack
            frame_queue.append(frame)
            #v = cv2.VideoWriter(str(int(time.time())) + '.mp4', cv2.VideoWriter_fourcc('f', 'f', 'v', '1'), cv2.CAP_PROP_FPS, frame_queue[0].shape, True)
            fname = str(int(time.time()))
            print(dims)
            v = cv2.VideoWriter(fname + '.avi', fourcc, 15, dims, True)
            # Define the codec and create VideoWriter object
            print(frame.shape)
            x = len(frame_queue)
            for i in range(x):
                f = frame_queue.popleft()
                v.write(f)
            print("Wrote File: ", fname, ".avi with ", x, " frames.")
            frame_queue = deque()
            #time.sleep(1/18)

        else:
            time.sleep(1/15)

def cleanUp(video):
    video.release()

    # Destroying all the windows
    cv2.destroyAllWindows()

motion_capture()