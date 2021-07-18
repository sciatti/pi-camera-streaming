# File Write Test 2
import cv2
import time

video = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*"H264")
video.set(cv2.CAP_PROP_FPS, 30)
video.set(cv2.CAP_PROP_FRAME_WIDTH, 640.0)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480.0)
_, frame = video.read() # read the first frame which takes a lot longer than the rest

dims = (frame.shape[1], frame.shape[0])
print(dims, " ---- ", frame.shape)

print(type(dims))
v = cv2.VideoWriter('videos/test.avi', fourcc, 30, dims, True)
for i in range(300):
    _, frame = video.read()
    v.write(frame)