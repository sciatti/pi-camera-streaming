import io
import socket
import struct
import time
import picamera
import math
# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('wb')
try:
    camera = picamera.PiCamera()
    camera.resolution = (426, 320)
    camera.framerate = 15
    # Start a preview and let the camera warm up for 2 seconds
    camera.start_preview()
    time.sleep(2)

    # Note the start time and construct a stream to hold image data
    # temporarily (we could write it directly to connection but in this
    # case we want to find out the size of each capture first to keep
    # our protocol simple)
    start = time.time()
    stream = io.BytesIO()
    processing_time = []
    for foo in camera.capture_continuous(stream, 'jpeg'):
        st = time.time()
        # Write the length of the capture to the stream and flush to
        # ensure it actually gets sent
        connection.write(struct.pack('<L', stream.tell()))
        connection.flush()
        # Rewind the stream and send the image data over the wire
        stream.seek(0)
        connection.write(stream.read())
        # If we've been capturing for more than 30 seconds, quit
        if time.time() - start > 15:
            break
        # Reset the stream for the next capture
        stream.seek(0)
        stream.truncate()
        processing_time.append(time.time() - st)
    # Write a length of zero to the stream to signal we're done
    connection.write(struct.pack('<L', 0))
finally:
    connection.close()
    server_socket.close()
    print("average frame processing time: ", sum(processing_time) / len(processing_time))
    print("average fps: ", 1 / (sum(processing_time) / len(processing_time)))