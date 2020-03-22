import time
import socket

HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1241))

s.listen(5)

while True:
    clientsocket, address = s.accept()
    print('Connection from {} has been established.'.format(address))
    msg = "Welcome to the server!"
    msg = '{:<{}}'.format(len(msg), HEADERSIZE) + msg
    clientsocket.send(bytes(msg, "utf-8"))

    while True:
        time.sleep(3)
        msg = 'The time is {}'.format(time.time())
        msg = '{:<{}}'.format(len(msg), HEADERSIZE) + msg

        print(msg)
        clientsocket.send(bytes(msg, "utf-8"))
