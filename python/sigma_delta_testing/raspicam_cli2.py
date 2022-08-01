import io
import socket
import struct
from PIL import Image
import numpy as np
import cv2

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
client_socket = socket.socket()
client_socket.connect(('192.168.0.140', 8000))

image = None
# Make a file-like object out of the connection
connection = client_socket.makefile('rb')
try:
    while True:
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            cv2.imwrite("testimg.jpg", image)
            break
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        image = cv2.imdecode(np.asarray(image_stream.getbuffer()), cv2.IMREAD_COLOR)
        #np.array(Image.open(image_stream))[:,:,::-1].copy()
        #image = Image.open(image_stream)
        #print('Image Size:' , image.shape)
        #image.verify()
        #print('Image is verified')
        cv2.imshow('img', image)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
finally:
    connection.close()
    client_socket.close()
    cv2.destroyAllWindows()
