import socket
import cv2
import base64
import numpy as np

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect(('172.29.108.89', 12345))
s.connect(('192.168.1.123', 12345))
data = []
while True:
    datum = s.recv(4096)
    print("data received: ", len(datum))
    if not datum: break
    data = []
    # scan for the initial size
    if b'size=' in datum:
        # found the initial size parameter, use it to keep reading and then reset back to this loop
        # find the length that the size parameter takes up
        Length = len(datum[datum.index(b'size=') : datum.index(b':') + 1])
        # find the number of bytes to read
        size = int((datum[datum.index(b'=') + 1 : datum.index(b':')]).decode('utf-8'))
        # determine how much data is read already
        bytes_read = len(datum) - Length
        # append the raw data into the data array
        data.append(datum[datum.index(b':') + 1 :])
        # now read 'size' number of bytes from the socket
        while bytes_read < size:
            # collect another payload of data
            datum = s.recv(4096)
            print("data received: ", len(datum))
            if not datum: break
            # append payload to the data array
            data.append(datum)
            # no need to do fancy stuff in this loop since we're collecting the rest of the image
            # simply add the size of what you are appending to the count
            bytes_read += len(datum)
            # rinse and repeat until the size of the payload has been read in fully
        if not datum: break
        # now prune out the new size parameter from the data array
        if b'size=' in data[-1]:
            data[-1] = data[-1][ : data[-1].index('size=')]
        
# append the image into one contiguous byte array
for i in range(1, len(data)):
    data[0] = data[0] + data[i]
#        file = open('writeback', 'w')
#        file.write(str(data[0]))
#        file.close()
# decode from byte array to buffer/string
img = base64.b64decode(data[0])
# cast to numpy array from buffer
npimg = np.frombuffer(img, dtype=np.uint8)
#        print(npimg)
# create image from numpy array
source = cv2.imdecode(npimg, 1)
# display image
#        cv2.imwrite('cam_shot_' + cnt + '.jpg', source)
cv2.imshow("Stream", source)
cv2.waitKey(1)