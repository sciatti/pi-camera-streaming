# Example Video Capture and Output to .avi file format
import cv2
import argparse

def capture(file, duration, framerate, height, width):

    video = cv2.VideoCapture(0) # init the video capture module
    fourcc = cv2.VideoWriter_fourcc(*"H264") # use the h264 video encoder
    video.set(cv2.CAP_PROP_FPS, framerate) # set the framerate to whatever FPS you want
    video.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    _, frame = video.read() # read the first frame which takes a lot longer than the rest

    print("Capturing Video For", duration, "seconds with Resolution", frame.shape, "@", framerate, "fps")

    v = cv2.VideoWriter(file, fourcc, framerate, (width, height))
    for i in range(duration * framerate):
        _, frame = video.read()
        v.write(frame)
    v.release()


def main():
    parser = argparse.ArgumentParser(description='Example Video Capture and Output file')
    parser.add_argument('-f', default='test.avi', help='file name of output file')
    parser.add_argument('-d', default=5, type=int, help='video duration')
    parser.add_argument('--fps', default=30, type=int, help='framerate of video')
    parser.add_argument('--height', default=480, type=int, help='height of video')
    parser.add_argument('--width', default=640, type=int, help='width of video')
    args = parser.parse_args()
    capture(args.f, args.d, args.fps, args.height, args.width)

if __name__ == "__main__":
    main()