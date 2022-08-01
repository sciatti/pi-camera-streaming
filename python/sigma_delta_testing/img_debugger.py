import io
import socket
import argparse
import struct
import cv2
import numpy as np

parser = argparse.ArgumentParser(description='Display rasperrypi live footage for debugging')
parser.add_argument('ip', type=str, action='store')
parser.add_argument('port', type=int, action='store')

args = parser.parse_args()

reductionFactor = 5
shape = (480, 640)
reducedShape = (shape[0] // reductionFactor, shape[1] // reductionFactor)

# Start a socket connection to the supplied ip address and port
client_socket = socket.socket()
client_socket.connect((args.ip, args.port))

def debug():
    connection = client_socket.makefile('rb')
    cv2.namedWindow('energy', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('energy', 640, 480)
    while True:
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            break
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        
        data = connection.read(image_len)
        img = np.frombuffer(data)#, dtype=np.float32)
        img = np.reshape(img, reducedShape)

        #image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with opencv and do some
        # processing on it
        #image_stream.seek(0)
        #image = cv2.imdecode(np.asarray(image_stream.getbuffer()), cv2.IMREAD_COLOR)
        #image = cv2.imdecode(img, cv2.IMREAD_GRAYSCALE)
        cv2.imshow('energy', img)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

def main():
    debug()

if __name__ == "__main__":
    main()