"""This File Sucks, Don't Use It"""
import argparse
import io
import picamera
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.ndimage.morphology import binary_dilation
from sigma_delta_est import zipfian_sigma_delta_update
from skimage.measure import find_contours
from PIL import Image
import time

import copy
import socket
import struct

parser = argparse.ArgumentParser(description='Display rasperrypi live footage with background subtraction')
#parser.add_argument('ip', type=str, action='store')
#parser.add_argument('port', type=int, action='store')
parser.add_argument('--gray', '-g', default=False, action='store_true')
parser.add_argument('--bits', '-b', type=int, default=32, action='store', choices=[16, 32, 64])
parser.add_argument('--period', '-p', type=int, default=32, action='store', choices=[1, 2, 4, 8, 16, 32, 64])
parser.add_argument('--debug', '-d', default=False, action='store_true')

args = parser.parse_args()

server_socket = None
connection = None
if args.debug:
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8000))
    server_socket.listen(0)
    # Accept a single connection and make a file-like object out of it
    connection = server_socket.accept()[0].makefile('wb')

def zipf_driver(camera, M_t, V_t, E_t, T_v, m, count, arrType):
    """Driver for Zipfian Sigma Delta Estimation Function"""
    # collect image off of camera
    stream = io.BytesIO()
    camera.capture(stream, format='jpeg', use_video_port=True)
    stream2 = copy.deepcopy(stream)
    stream.seek(0)
    count += 1
    # Recevied new frame, begin image preprocessing optimization
    img = Image.open(stream)
    img = img.reduce(4) # downscale to 120x160 to significnatly increase performance
    if args.gray is True:
        img = img.convert("L")
    frame = np.asarray(img, dtype=arrType)
    # First iteration book keeping
    if M_t is None:
        M_t = np.ndarray.astype(gaussian_filter(frame, 1), arrType)
        V_t = np.zeros(M_t.shape, dtype=arrType)
        E_t = np.zeros(M_t.shape, dtype=arrType)
    #print(E_t.dtype, end=" ")
    # call update step after image preprocessing is finished
    z = [stream2, zipfian_sigma_delta_update(frame, M_t, V_t, E_t, count, m, T_v, np.finfo(arrType).max)]
    #print(E_t.dtype)
    return z

def my_area(contour) -> float:
    """Deduce Area Of Contour"""
    # construct numpy array of x and y coordinates
    Xcontour = np.take(contour, (0), axis=1)
    Ycontour = np.take(contour, (1), axis=1)
    Xoffset = np.roll(Xcontour, -1, axis=0)
    Yoffset = np.roll(Ycontour, -1, axis=0)
    return 0.5 * np.sum(Xoffset * Ycontour - Xcontour * Yoffset)

def detect_motion(E_t) -> bool:
    # run analysis on energy image to determine if motion exists
    E_t[E_t < 30] = 0
    E_t[E_t >= 30] = np.finfo(E_t.dtype).max
    thresh_arr = E_t.astype(dtype=np.uint8)
    thresh_arr = binary_dilation(thresh_arr, iterations=2)
    # need to find the contours after dilation
    contours = find_contours(thresh_arr, 0.8)
    for contour in contours:
        if my_area(contour) > 0.01 * thresh_arr.shape[0] * thresh_arr.shape[1]:
            return True
    return False

def send_to_computer(stream):
    if not args.debug:
        pass
    else:
        connection.write(struct.pack('<L', len(stream)))
        connection.flush()
        # Rewind the stream and send the image data over the wire
        #stream.seek(0)
        #connection.write(stream.read())
        connection.write(stream)

def main():
    # initialize variables
    T_v = args.period
    arrType = np.float32
    m = args.bits
    if args.bits == 16:
        arrType = np.float16
    elif args.bits == 32:
        arrType = np.float32 # Unnecessary but added for readability
    elif args.bits == 64:
        arrType = np.float64
    count = 0
    M_t, V_t, E_t = None, None, None

    with picamera.PiCamera() as camera:
        print("initializing camera")
        camera.resolution = (640, 480)
        camera.framerate = 15
        stream = picamera.PiCameraCircularIO(camera, seconds=10)
        camera.start_recording(stream, format='h264')
        try:
            print("initializing BGS")
            # Initialize the BGS algorithm by running it for 60s
            st = time.time()
            while time.time() - st < 30:
                camera.wait_recording(1)
                measure = time.perf_counter()
                vals = zipf_driver(camera, M_t, V_t, E_t, T_v, m, count, arrType)
                print("processing time:", time.perf_counter() - measure, "fps:", 1 / (time.perf_counter() - measure))
                E_t, M_t, V_t = vals[1][0], vals[1][1], vals[1][2]
                send_to_computer(E_t.tobytes())
            # Background Subtraction has been initialized, proceed to detecting input
            print("BGS initialized")
            while True:
                camera.wait_recording(1)
                # Call update driver
                vals = zipf_driver(camera, M_t, V_t, E_t, T_v, m, count, arrType)
                E_t, M_t, V_t = vals[1][0], vals[1][1], vals[1][2]
                send_to_computer(vals[0])
                print(E_t.shape)
                if detect_motion(E_t):
                    print('Motion detected!')
                    # As soon as we detect motion, split the recording to
                    # record the frames "after" motion
                    camera.split_recording('after.h264')
                    # Write the 10 seconds "before" motion to disk as well
                    stream.copy_to('before.h264', seconds=10)
                    stream.clear()
                    # Wait until motion is no longer detected, then split
                    # recording back to the in-memory circular buffer
                    while detect_motion(camera):
                        camera.wait_recording(1)
                    print('Motion stopped!')
                    camera.split_recording(stream)
                    break
        finally:
            camera.stop_recording()

if __name__ == '__main__':
    main()
