import pickle

from gevent._socket2 import socket

import message_codes as codes


def send_points(points, connection_socket):
    serialized, size = _serialize_data(points)
    connection_socket.send(bytes(codes.ADD_POINTS))
    _send_data(connection_socket, serialized, size)
    return size


def send_results(result, client_socket):
    serialized, size = _serialize_data(result)
    _send_data(client_socket, serialized, size)


def _serialize_data(points):
    serialized = pickle.dumps(points)
    return serialized, "%010d" % (len(serialized))


def _send_data(connection_socket, serialized, size):
    connection_socket.send(bytes(size))
    connection_socket.send(serialized)
