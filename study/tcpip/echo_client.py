import socket

import sys

""" ECHO CLIENT """
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = (sys.argv[1], 10000)
print('starting up on %s port %s' % server_address, file=sys.stderr)
sock.connect(server_address)

try:

    # Send data
    message = b'This is the message.  It will be repeated.'
    print('sending "%s"' % message, file=sys.stderr)
    sock.sendall(message)

    # Look for the response
    amount_received = 0
    amount_expected = len(message)

    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print('received "%s"' % data, file=sys.stderr)

finally:
    print('closing socket', file=sys.stderr)
    sock.close()
