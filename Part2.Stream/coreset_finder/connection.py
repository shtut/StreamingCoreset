import socket
import message_codes as codes
import pickle

from coreset_finder.message import Message


class Connection(object):
    def __init__(self):
        self._socket = None
        self._address = None

    def connect(self, server, port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (server, port)
        self._socket.connect(server_address)

    def receive_message(self):
        len_str = self._socket.recv(10, 0)
        if len_str == '':
            return Message(codes.TERMINATE)
        length = int(len_str)
        data = self._socket.recv(length, 0)
        if data == '':
            return Message(codes.TERMINATE)
        return pickle.loads(data)

    def send_message(self, message):
        serialized, size = self._serialize_data(message)
        self._socket.send(bytes(size))
        self._socket.send(serialized)
        return size

    @staticmethod
    def _serialize_data(points):
        """
        serializes the given input.  returns the serialized data and the size of the data.
        :param points: input data
        :return: serialized data
        """
        serialized = pickle.dumps(points)
        return serialized, "%010d" % (len(serialized))

    def close(self):
        self._socket.close()
