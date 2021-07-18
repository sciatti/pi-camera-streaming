import cv2
import base64
import numpy as np
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hn = socket.gethostname()
print(hn)
#ip = socket.gethostbyname(hn)
ip = socket.gethostbyname(hn + ".local")
#s.bind(('192.168.1.142',12345))
print('starting on address: ', (ip, 12345))
s.bind((ip,12345))
s.listen()
conn,addr = s.accept()
with conn:
    print('connection from: ', addr)
    #msg = "hello world"
    #bytes_sent = conn.send(msg.encode('utf-8'))
    camera = cv2.VideoCapture(0)  # init the camera
    cnt = 0
    while 2 > cnt:
        try:
            grabbed, frame = camera.read()  # grab the current frame
            frame = cv2.resize(frame, (640, 480))  # resize the frame
            encoded, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer)
            bytes_sent = conn.send(jpg_as_text)
            cnt += 1
        except KeyboardInterrupt:
            camera.release()
            cv2.destroyAllWindows()
            break
        print("% of bytes sent: ", 100 * (bytes_sent / len(jpg_as_text)))
print("closing connection with: ", addr)
conn.close()
print("connection with ", addr, " closed")

print("closing socket connection")
s.close()
print("socket connection closed")