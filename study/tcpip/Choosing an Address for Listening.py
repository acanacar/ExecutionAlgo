import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address given on the command line
server_name = sys.argv[1]
server_address = (server_name, 10000)
print('starting up on %s port %s' % server_address, file=sys.stderr)
sock.bind(server_address)
print(sock.getsockname())

sock.listen(1)

while True:
    print('waiting for a connection', file=sys.stderr)
    connection, client_address = sock.accept()
    try:
        print('client connected:', client_address, file=sys.stderr)
        while True:
            data = connection.recv(16)
            print('received "%s"' % data, file=sys.stderr)
            if data:
                connection.sendall(data)
            else:
                break
    finally:
        connection.close()
