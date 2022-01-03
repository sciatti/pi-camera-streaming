import socket
import cv2
import argparse
import numpy as np

parser = argparse.ArgumentParser(description='Receive a connection')
parser.add_argument('ip', type=str, help='ip address to set up on')
parser.add_argument('port', type=int, help='port number')
parser.add_argument('-w', action='count', default=0, help='flag to tell the server to write its images out')

args = parser.parse_args()

def receive(conn, addr, names):
    """Parser for the data received over socket"""
    msg = bytes()
    while True:
        data = conn.recv(1024)
        if not data:
            break
        msg += data
    return parse(msg, names)

def parse(msg, names):
    start = 0
    c = 0
    images = []
    while start < len(msg):
        substr_idx = msg.find(b'\x89PNG\r\n', start, start+50)
        image_size = int(msg[start:substr_idx].decode())
        image_size_len = len(msg[start:substr_idx].decode())

        x = np.frombuffer(msg[substr_idx:substr_idx+image_size], dtype=np.uint8)
        img = cv2.imdecode(x, cv2.IMREAD_UNCHANGED)

        if args.w > 0:
            cv2.imwrite(str(c) + ".png", img)
        c += 1
        start = start+image_size+image_size_len
        images.append(img)
    return images

def detectMotion(image_list):
    """Function that detects motion with a fine algorithm and then draws contour lines over it"""
    pass

def sendToServer(image_list):
    """Function to send to the cloud or server which stores the file"""
    pass

def main():
    """Driver for the receiver program."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((args.ip, args.port))
        sock.listen()
        print("listening on:", (args.ip, args.port))
        conn, addr = sock.accept()
        print("conn from:", addr)
        c = 0
        #names = ["red-received.png", "green-received.png", "blue-received.png"]
        names = ["blue-received.png", "red-received.png"]
        while c < 2:
            with conn:
                if conn.fileno() == -1:
                    print("closed:", c)
                    break
                try:
                    data = receive(conn, addr, names)
                    if detectMotion(data):
                        sendToServer(data)
                except Exception as e:
                    print("exception:", e)
                    print("exiting")
                    break

                c += 1
        print('exited conn\n')

if __name__ == "__main__":
    main()