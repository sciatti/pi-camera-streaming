import socket
import cv2
import base64
import numpy as np

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect(('172.29.108.89', 12345))
s.connect(('192.168.1.123', 12345))
data = []
while True:
    datum = s.recv(1000000)
    #print(data)
    print("data received: ", len(datum))
    if not datum: break
    data.append(datum)
    try:
        for i in range(1, len(data)):
            data[0] = data[0] + data[i]
        img = base64.b64decode(data[0])
        npimg = np.frombuffer(img, dtype=np.uint8)
        #print(npimg)
        source = cv2.imdecode(npimg, 1)
        cv2.imwrite('infrared_camera_shot_plants.jpg', source)
        cv2.imshow("Stream", source)
        cv2.waitKey(1)

    except KeyboardInterrupt:
        cv2.destroyAllWindows()