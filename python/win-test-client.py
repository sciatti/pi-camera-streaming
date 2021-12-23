import socket

def wait_for_conn():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hn = socket.gethostname()
    print(hn)
    #ip = socket.gethostbyname(hn)
    ip = socket.gethostbyname(hn)
    #s.bind(('192.168.1.142',12345))
    print('starting on address: ', ("192.168.1.147", 12345))
    s.bind(("192.168.1.147",12345))
    s.listen()
    conn,addr = s.accept()
    print('connection from: ', addr)
    while True:
        datum = s.recv(128)
        #print(data)
        print("data received: ", len(datum))
        if not datum: break

def main():
    while True:
        wait_for_conn()

if __name__ == "__main__":
    main()