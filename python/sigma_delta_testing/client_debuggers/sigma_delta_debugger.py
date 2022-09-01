import io
import socket
import struct
from PIL import Image
from cv2 import WINDOW_NORMAL
import numpy as np
import cv2
from sigma_delta_est import zipfian_sigma_delta_update
from collections import deque
from scipy.ndimage import gaussian_filter
import argparse
import time

parser = argparse.ArgumentParser(description='Display rasperrypi live footage with background subtraction')
parser.add_argument('ip', type=str, action='store')
parser.add_argument('port', type=int, action='store')
parser.add_argument('--gray', '-g', default=False, action='store_true')
parser.add_argument('--bits', '-b', type=int, default=32, action='store', choices=[16, 32, 64])
parser.add_argument('--period', '-p', type=int, default=32, action='store', choices=[1, 2, 4, 8, 16, 32, 64])

args = parser.parse_args()

T_v = args.period
arrType = np.float32
m = args.bits
if args.bits == 32:
    arrType = np.float32 # Unnecessary but added for readability
elif args.bits == 64:
    arrType = np.float64
elif args.bits == 16:
    arrType = np.float16

def socket_driver():
    # Start a socket connection to the supplied ip address and port
    client_socket = socket.socket()
    client_socket.connect((args.ip, args.port))

    # initialize variables
    count = 0
    M_t, V_t, E_t = None, None, None
    image = None
    # Make a file-like object out of the connection
    connection = client_socket.makefile('rb')
    cv2.namedWindow('energy', WINDOW_NORMAL)
    cv2.resizeWindow('energy', 640, 480)
    start = time.time()
    try:
        while True:
            # Read the length of the image as a 32-bit unsigned int. If the
            # length is zero, quit the loop
            image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
            if not image_len:
                break
            count += 1
            # Construct a stream to hold the image data and read the image
            # data from the connection
            image_stream = io.BytesIO()
            image_stream.write(connection.read(image_len))
            # Rewind the stream, open it as an image with opencv and do some
            # processing on it
            image_stream.seek(0)
            image = cv2.imdecode(np.asarray(image_stream.getbuffer()), cv2.IMREAD_COLOR)
            frame = image.copy()

            E_t, M_t, V_t = zipfian_sigma_delta_driver(frame, count, E_t, M_t, V_t, m, T_v, arrType)

            #energy_image = cv2.resize(E_t, (E_t.shape[1] * 4, E_t.shape[0] * 4))
            
            #cv2.imshow('original', image)
            cv2.imshow('energy', E_t)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
    finally:
        connection.close()
        client_socket.close()
        print("frames received:", count, "time elapsed:", time.time() - start, "avg fps:", count / (time.time() - start))
        cv2.destroyAllWindows()


def zipfian_sigma_delta_driver(frame, count, E_t, M_t, V_t, m, T_v, arrType):
    """Driver for Zipfian Sigma Delta Estimation Function"""
    # Recevied new frame, call update step
    frame = cv2.resize(frame, (int(frame.shape[1] / 4), int(frame.shape[0] / 4))) # downscale to 120x160 to increase performance
    if args.gray is True:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # First iteration book keeping
    if M_t is None:
        M_t = np.ndarray.astype(gaussian_filter(frame, 1), arrType)
        V_t = np.zeros(M_t.shape, dtype=arrType)
        E_t = np.zeros(M_t.shape, dtype=arrType)
    
    return zipfian_sigma_delta_update(frame, M_t, V_t, E_t, count, m, T_v, arrType)



if __name__ == "__main__":
    socket_driver()