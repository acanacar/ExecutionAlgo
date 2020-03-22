import socket

HEADERSIZE = 10
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1241))

while True:
    full_msg = ''
    new_msg = True
    while True:
        msg = s.recv(16)
        if new_msg:
            print("new message len: ", msg[:HEADERSIZE])
            msglen = int(msg[:HEADERSIZE])
            new_msg = False

        print('full message len : {}'.format(msglen))

        full_msg += msg.decode('utf-8')

        print(len(full_msg))

        if len(full_msg) - HEADERSIZE == msglen:
            print('full msg received')
            print(full_msg[HEADERSIZE:])
            new_msg = True
            full_msg = ''

