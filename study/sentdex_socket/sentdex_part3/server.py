import time
import socket
import pickle

HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1241))

s.listen(5)

while True:
    clientsocket, address = s.accept()
    print('Connection from {} has been established.'.format(address))

    d = {1: "Hey", 2: "There"}
    msg = pickle.dumps(d)
    msg = bytes('{:<{}}'.format(len(msg), HEADERSIZE),"utf-8") + msg
    clientsocket.send(msg)
