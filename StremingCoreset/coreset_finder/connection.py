"""
Defines the socket connection- handles the Receive and Send functions while dividing the data into smaller 'PACKET_SIZE' packets in order to avoid the socket max data limit.
"""
import pickle
import socket
import array_util as arr_util
import message_codes as codes
from message import Message
import configuration as cfg


class Connection(object):
    def __init__(self):
        self._socket = None
        self._address = None

    def connect(self, server, port):
        """
        creates a socket and connects to the given server via the given port
        :param server: server address
        :param port: port number
        :return:
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (server, port)
        self._socket.connect(server_address)

    def receive_message(self):
        """
        returns the received message
        :return: received message
        """
        len_str = self._socket.recv(10, 0)
        if len_str == '':
            return Message(codes.TERMINATE)
        count = int(len_str)
        tmp_str = ""
        for i in xrange(count):
            len_str = self._socket.recv(10, 0)
            if len_str == '':
                return Message(codes.TERMINATE)
            try:
                length = int(len_str)
            except:
                return Message(codes.TERMINATE)
            while length > 0:
                data = self._socket.recv(length, 0)
                length -= len(data)
                if data == '':
                    return Message(codes.TERMINATE)
                tmp_str = tmp_str + data
        res = pickle.loads(tmp_str)
        return res

    def send_message(self, message):
        """
        splits the given message into 'PACKET_SIZE' packets, and sends them
        :param message: the message to send
        :return:
        """
        serialized, size = self._serialize_data(message)
        packets = arr_util.array_split(serialized, cfg.PACKET_SIZE)
        self._socket.send(self._size_in_bytes(packets))
        for idx, packet in enumerate(packets):
            self._socket.send(self._size_in_bytes(packet))
            self._socket.send(packet)
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

    @staticmethod
    def _size_in_bytes(data):
        return bytes("%010d" % (len(data)))

    def close(self):
        """
        closes the connection
        :return:
        """
        self._socket.close()
