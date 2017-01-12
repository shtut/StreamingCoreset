import pickle

from gevent._socket2 import socket

import message_codes as codes


def send_points(points, connection_socket):
    """
    serializes the given data and sends it to the given socket.
    also invokes the 'ADD_POINTS' code.
    :param points: data to send
    :param connection_socket: connection socket
    :return: size of the serialized data
    """
    serialized, size = _serialize_data(points)
    connection_socket.send(bytes(codes.ADD_POINTS))
    _send_data(connection_socket, serialized, size)
    return size


def send_results(result, client_socket):
    """
    serializes the given data and sends it to the given socket.
    :param result: result
    :param client_socket:  connection socket
    :return: none
    """
    serialized, size = _serialize_data(result)
    _send_data(client_socket, serialized, size)


def _serialize_data(points):
    """
    serializes the given input.  returns the serialized data and the size of the data.
    :param points: input data
    :return: serialized data
    """
    serialized = pickle.dumps(points)
    return serialized, "%010d" % (len(serialized))


def _send_data(connection_socket, serialized, size):
    """
    sends the serialized data using the connection socket.
    :param connection_socket: connection socket
    :param serialized: serialized data
    :param size: size of data
    :return: none
    """
    connection_socket.send(bytes(size))
    connection_socket.send(serialized)
