import socket
import codes
import numpy as np
import pickle


def test():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10001)
    sock.connect(server_address)

    for i in xrange(10):
        data = pickle.dumps(np.arange(10))
        size = "%010d" % (len(data))
        sock.send(bytes(codes.ADDPOINTS))
        sock.send(bytes(size))
        sock.send(data)

        code = sock.recv(1, 0)

        if len(code) == 0:
            print "Problem, server died"
        elif int(code) == codes.ACCEPTED:
            print "Points sent successfully!"
        else:
            print "Problem, received code", code

    print "Getting the summary..."

    sock.send(bytes(codes.GETUNIFIED))
    msg = sock.recv(10, 0)
    length = int(msg)
    data = sock.recv(length, 0)
    data = pickle.loads(data)

    print "Received the summary: %s" % data

test()
