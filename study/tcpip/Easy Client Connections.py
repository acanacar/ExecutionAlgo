import socket
import sys

"""Easy Client Connections"""


def get_constants(prefix):
    """Create a dictionary mapping socket module constants to their names."""
    return dict((getattr(socket, n), n)
                for n in dir(socket)
                if n.startswith(prefix)
                )


families = get_constants('AF_')
types = get_constants('SOCK_')
protocols = get_constants('IPPROTO_')

# Create a TCP/IP socket
sock = socket.create_connection(('localhost', 10000))

print('Family  :', families[sock.family], file=sys.stderr)
print('Type    :', types[sock.type], file=sys.stderr)
print('Protocol:', protocols[sock.proto], file=sys.stderr)
print(file=sys.stderr)

try:

    # Send data
    message = b'This is the message.  It will be repeated.'
    print('sending "%s"' % message, file=sys.stderr)
    sock.sendall(message)

    amount_received = 0
    amount_expected = len(message)

    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print('received "%s"' % data, file=sys.stderr)

finally:
    print('closing socket', file=sys.stderr)
    sock.close()
