from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy
from datetime import datetime, timedelta

MOTION_RECORD_TIME = timedelta(seconds = 3)


def have_motion(frame1, frame2):
    if frame1 is None or frame2 is None:
        return False
    delta = cv2.absdiff(frame1, frame2)
    thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
    return numpy.sum(thresh) > 0

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

prev_frame = None
last_motion = None
motion_filename = None
motion_file = None

frame_size = camera.resolution
fourcc = cv2.VideoWriter_fourcc(*"H264")

for frame in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
    image = frame.array



    frame_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    frame_gray = cv2.GaussianBlur(frame_gray, (21, 21), 0)



    if have_motion(prev_frame, frame_gray):
        if motion_file is None:
            now = datetime.now()
            motion_filename = now.strftime("%Y_%m_%d_%H_%M_%S_MOTION.avi")
            motion_file = cv2.VideoWriter(motion_filename, fourcc, 5, frame_size)
            last_motion = time.time()
        print("Motion!", last_motion)

    if motion_file is not None:
        motion_file.write(image)
        print('Saving...')
        print(now)
        print(time.time() - last_motion)
        if time.time() - last_motion > 3:
            motion_file.release()
            motion_file = None
            print('Saved')
            print(motion_filename)
            break


    prev_frame = frame_gray
    #cv2.imshow('frame', image)
    rawCapture.truncate(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
