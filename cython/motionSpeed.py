import cython
import cv2
from collections import deque
import time

def detect_motion(frame, static_back):
    motion = False
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

        #(x, y, w, h) = cv2.boundingRect(contour)
        # making green rectangle arround the moving object
        #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
    return motion, frame

def main():
    que = deque()
    video = cv2.VideoCapture(0)
    video.set(cv2.CAP_PROP_FPS, 30)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    _, bg = video.read()
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
    bg = cv2.GaussianBlur(bg, (21, 21), 0)

    for i in range(5, 0, -1):
        print("Capturing Frames in " + str(i) + " seconds...")
        time.sleep(1)
    print("capturing Frames...")
    for i in range(100):
        _, frame = video.read()
        que.appendleft(frame)
    ts = []
    while len(que) > 0:
        st = time.time()
        detect_motion(que.pop(), bg)
        ts.append(time.time() - st)
    for t in ts: # yes I know this is poor naming
        print(t)

if __name__ == "__main__":
    main()