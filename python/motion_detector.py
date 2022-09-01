"""Motion Detection File For Raspberry Pi using a camera, Copyright Salvatore Ciatti"""
import time
import argparse
import io
import socket
import struct
import picamera
import numpy as np
from PIL import Image
from skimage.measure import find_contours
from scipy.ndimage import gaussian_filter

parser = argparse.ArgumentParser(
    description='Display rasperrypi live footage with background subtraction'
)
parser.add_argument('--net', action='store_true')
parser.add_argument('-p', '--port', dest='port', default=8000, action='store', type=int)
parser.add_argument('-E', '--Energy', dest='energy', default=False, action='store_true')

args = parser.parse_args()

class MyMotionDetector():
    """Class that implements motion detection with picamera module"""
    def __init__(self):
        # TODO: Maybe I should convert these into keys inside a dictionary (eventually)
        self.step = 0
        self.reductionFactor = 5
        self.reductionShape = (480 // self.reductionFactor, 640 // self.reductionFactor)
        self.T_v = 32
        self.arrType = np.float64
        self.M_t = None
        self.V_t = np.zeros(self.reductionShape, dtype=self.arrType)
        self.E_t = np.zeros(self.reductionShape, dtype=self.arrType)
        self.m = 64
        self.t = 0
        self.N = 3
        self.V_min = 2
        self.V_max = np.finfo(self.arrType).max
        self.contour_times = []
        self.area_times = []
        if args.net:
            self.server_socket = socket.socket()
            self.server_socket.bind(('0.0.0.0', args.port))
            self.server_socket.listen(0)
            # Accept a single connection and make a file-like object out of it
            self.connection = self.server_socket.accept()[0].makefile('wb')
        self.start_time = time.time()

    def send_stream_to_computer(self, input_arr=None):
        """Function used to send an image (input_arr) to a client computer"""
        # This is used in conjunction with the --net argument
        if not args.net:
            return
        arr = self.E_t
        if input_arr is not None:
            arr = input_arr
        stream = io.BytesIO(arr.tobytes())
        stream.seek(0,2)
        self.connection.write(struct.pack('<L', stream.tell()))
        self.connection.flush()
        # Rewind the stream and send the image data over the wire
        stream.seek(0)
        self.connection.write(stream.read())

    def write(self, buf):
        """Write method used to detect motion"""
        if self.step == 0:
            stream = io.BytesIO(buf)
            stream.seek(0)
            data = Image.open(stream)
            self.driver(data)
            if self.detect_motion():
                print(f'Motion detected! at {time.time()}')
            self.send_stream_to_computer()
        self.step = (self.step + 1) % 6
        return len(buf)

    def basic_sigma_delta_update(self, I_t):
        """A basic sigma delta background subtraction algorithm"""
        self.M_t = np.where(self.M_t < I_t, self.M_t + 1, self.M_t)
        self.M_t = np.where(self.M_t > I_t, self.M_t - 1, self.M_t)

        O_t = np.absolute(self.M_t - I_t, dtype=self.arrType)

        self.V_t = np.where(self.V_t < self.N * O_t, self.V_t + 1, self.V_t)
        self.V_t = np.where(self.V_t > self.N * O_t, self.V_t - 1, self.V_t)
        self.V_t = np.clip(self.V_t, self.V_min, self.V_max, dtype=self.arrType)

        self.E_t = np.where(O_t < self.V_t, 0.0, 1.0)

    def driver(self, input_img):
        """Driver for Sigma Delta Estimation Function"""
        self.t += 1
        # Recevied new frame, begin image preprocessing optimization
        # downscale to significantly increase performance
        input_img = input_img.reduce(self.reductionFactor)
        input_img = input_img.convert("L")

        if args.net and not args.energy:
            # Send downscaled image from camera to client (not energy image)
            self.send_stream_to_computer(input_arr=input_img)

        frame = np.asarray(input_img, dtype=self.arrType)
        if self.t == 1:
            self.M_t = np.ndarray.astype(gaussian_filter(frame, 1), self.arrType)
        # call update step after image preprocessing is finished
        self.basic_sigma_delta_update(frame)

    def my_area(self, contour) -> float:
        """Deduce Area Of Contour"""
        # construct numpy array of x and y coordinates
        Xcontour = np.take(contour, (0), axis=1)
        Ycontour = np.take(contour, (1), axis=1)
        Xoffset = np.roll(Xcontour, -1, axis=0)
        Yoffset = np.roll(Ycontour, -1, axis=0)
        return 0.5 * np.sum(Xoffset * Ycontour - Xcontour * Yoffset)

    def detect_motion(self) -> bool:
        """Determine if there is a large enough white contour to classify as motion"""
        # run analysis on energy image to determine if motion exists
        if args.net and args.energy:
            # Send energy image to client
            self.send_stream_to_computer()
        contours = find_contours(self.E_t, 0.8)
        for contour in contours:
            if self.my_area(contour) > 0.025 * self.E_t.shape[0] * self.E_t.shape[1]:
                return True
        return False

start = None
try:
    with picamera.PiCamera(resolution='VGA', framerate=30) as camera:
        output = MyMotionDetector()
        time.sleep(2)
        start = time.time()
        camera.start_recording(output, format='mjpeg')
        camera.wait_recording(180)
        camera.stop_recording()
finally:
    finish = time.time()
    print('read %d images in %d seconds at %.2ffps' % (
    output.t, finish-start, output.t / (finish-start)))
