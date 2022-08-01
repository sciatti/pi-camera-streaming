import socket
from sigma_delta_est import zipfian_sigma_delta_update
import picamera
import struct
import time
import io
from PIL import Image
from scipy.ndimage import gaussian_filter
import numpy as np
import copy

stream = True

connection = None
server_socket = None
if stream:
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8001))
    server_socket.listen(0)
    # Accept a single connection and make a file-like object out of it
    connection = server_socket.accept()[0].makefile('wb')

arrType = np.float32

m = 32
T_v = 32
V_max = np.finfo(arrType).max

def send_stream_to_computer(stream):
    connection.write(struct.pack('<L', stream.tell()))
    connection.flush()
    # Rewind the stream and send the image data over the wire
    stream.seek(0)
    connection.write(stream.read())

def zipfian_sigma_delta_driver(camera):
    M_t, V_t, E_t = None, None, None
    c = 0
    #while video array is not empty:
    st = time.time()
    while time.time() - st < 600.0:
        stream = io.BytesIO()
        measure = time.perf_counter()
        camera.capture(stream, format='jpeg', use_video_port=True)
        print("capture time:", time.perf_counter() - measure, "fps:", 1 / (time.perf_counter() - measure))
        if stream:
            stream2 = copy.deepcopy(stream)
            send_stream_to_computer(stream2)
        processingStart = time.perf_counter()
        stream.seek(0)
        c += 1
        # Recevied new frame, call update step
        img = Image.open(stream)
        img = img.reduce(4) # downscale to 120x160 to significnatly increase performance
        img = img.convert("L")
        frame = np.asarray(img, dtype=arrType)
        # First iteration book keeping
        if M_t is None:
            M_t = np.ndarray.astype(gaussian_filter(frame, 1), arrType)
            V_t = np.zeros(M_t.shape, dtype=arrType)
            E_t = np.zeros(M_t.shape, dtype=arrType)        
        E_t, M_t, V_t = zipfian_sigma_delta_update(frame, M_t, V_t, E_t, c, m, T_v, V_max)
        print("processing time:", time.perf_counter() - processingStart, "fps:", 1 / (time.perf_counter() - processingStart))
    exit(1)


def main():
    with picamera.PiCamera() as camera:
        print("initializing camera")
        camera.resolution = 'vga'
        camera.framerate = 30
        stream = picamera.PiCameraCircularIO(camera, seconds=10)
        camera.start_recording(stream, format='mjpeg')
        zipfian_sigma_delta_driver(camera)

if __name__ == "__main__":
    main()