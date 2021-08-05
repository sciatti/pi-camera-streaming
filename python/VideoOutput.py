# Example Video Capture and Output to .avi file format
import cv2
import argparse
import time
from collections import deque

def capture(file, duration, framerate, height, width):
    bench = []
    bench.append(time.time()) # 0 - Capture() start time
    video = cv2.VideoCapture(-1) # init the video capture module
    fourcc = cv2.VideoWriter_fourcc(*"H264") # use the h264 video encoder
    video.set(cv2.CAP_PROP_FPS, framerate) # set the framerate to whatever FPS you want
    video.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    #video.set(cv2.CAP_PROP_BUFFERSIZE, 3)
    bench.append(time.time()) # 1 - Video Capture init time
    _, frame = video.read() # read the first frame which takes a lot longer than the rest
    bench.append(time.time()) # 2 - First Frame Read Time

    print("Capturing Video For", duration, "seconds with Resolution", frame.shape, "@", framerate, "fps")
    frames = deque()
    v = cv2.VideoWriter(file, fourcc, framerate, (width, height))   
    bench.append(time.time()) # 3 - Video Writer init time
    for i in range(duration * framerate):
        _, frame = video.read()
        frames.append(frame)
    print("Recording Stopped")
    bench.append(time.time()) # 4 - Frame Recording time
    for i in range(len(frames)):
        v.write(frames[i])
    bench.append(time.time()) # 5 - Write to Video File time
    v.release()
    bench.append(time.time()) # 6 - Video Writer Release time
    print("Video Capture init time", bench[1] - bench[0])
    print("First Frame Read Time", bench[2] - bench[1])
    print("Video Writer init time", bench[3] - bench[2])
    print("Frame Recording time", bench[4] - bench[3])
    print("Write to Video File time", bench[5] - bench[4])
    print("Video Writer Release time", bench[6] - bench[5])
    print("Total Time", bench[-1] - bench[0])

def main():
    parser = argparse.ArgumentParser(description='Example Video Capture and Output file')
    parser.add_argument('-f', default='test.avi', help='file name of output file')
    parser.add_argument('-d', default=5, type=int, help='video duration')
    parser.add_argument('--fps', default=30, type=int, help='framerate of video')
    parser.add_argument('--height', default=480, type=int, help='height of video')
    parser.add_argument('--width', default=640, type=int, help='width of video')
    args = parser.parse_args()
    st = time.time()
    capture(args.f, args.d, args.fps, args.height, args.width)
if __name__ == "__main__":
    main()
