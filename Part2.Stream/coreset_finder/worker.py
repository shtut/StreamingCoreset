import logging as log
import pickle
import random as rand
import socket
import sys
from coreset_tree_algorithm import CoresetTeeAlgorithm

import array_util as util
import connection_data as conn
import message_codes as codes
from coreset_finder.simpleCoreset import SimpleCoreset

log.basicConfig(filename='worker.log', level=log.DEBUG)
MAX_RANDOM_NUMBER = 2000
CORESET_SIZE = 10
CORSET_ALGORITHM = SimpleCoreset.coreset_alg


# CORSET_ALGORITHM = adiel.LineKMeans.coreset_alg


class Worker(object):
    def __init__(self, number=0):
        self._coresetTreeBuilder = CoresetTeeAlgorithm(CORSET_ALGORITHM, CORESET_SIZE)
        self._init_number(number)

    def register_and_handle(self):
        """
        Registers with the server and enters the send/receive loop.

        Connects to the server and tries to register. If successfully it
        starts waiting for commands, otherwise it stops and reports an
        error.
        :return: -1 if fails
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (conn.server_ip, conn.worker_port)
        self._connect_server(server_address, server_socket)
        self._register_to_server(server_socket)

        command = int(server_socket.recv(1, 0))
        if command != codes.CONTINUE:
            log.error("Server sent %s, but expected codes.CONTINUE!" % command)
            server_socket.close()
            return -1

        self._handel_commands(server_socket)

        server_socket.close()

    def _handel_commands(self, server_socket):
        """
        handles the communication codes received from the server
        :param server_socket: server socket
        :return: none
        """
        while True:
            command = int(server_socket.recv(1, 0))
            log.debug("Received command %s" % command)
            if command == codes.ADD_POINTS:
                self._new_points(server_socket)
            elif command == codes.GET_UNIFIED:
                self._get_summary(server_socket)
            elif command == codes.TERMINATE:
                break

    def _worker_code(self):
        return codes.REGISTER_WORKER

    def _register_to_server(self, server_socket):
        """
        registers the worker to the server
        :param server_socket: server socket
        :return: none
        """
        try:
            server_socket.sendall(bytes(self._worker_code()))
        except socket.error:
            sys.exit()

    @staticmethod
    def _connect_server(server_address, server_socket):
        """
        attempts to connect to the server
        :param server_address: server address
        :param server_socket: server socket
        :return:
        """
        try:
            server_socket.connect(server_address)
        except socket.error as msg:
            sys.stderr.write("[ERROR] %s\n" % msg[1])
            sys.exit()

    def _new_points(self, sock):
        length = int(sock.recv(10, 0))
        data = sock.recv(length, 0)
        sock.send(bytes(codes.ACCEPTED))
        data = util.convert_points_to_float(pickle.loads(data))
        self._coresetTreeBuilder.add_points(data)
        print "Got a new matrix", data.shape

    def _get_summary(self, sock):
        """
        returns the current tree coreset to the server
        :param sock: server socket
        :return: none
        """
        summary = self._coresetTreeBuilder.get_unified_coreset()
        log.debug("Sending the summary to the server %s" % summary)
        serialized = pickle.dumps(summary)
        size = "%10d" % (len(serialized))
        sock.send(bytes(codes.SENDING))
        sock.send(bytes(size))
        sock.send(serialized)
        print "Summary sent to the server. Going back to the loop."

    def _init_number(self, number):
        if number != 0:
            self._number = number
        else:
            self._number = rand.randint(1, MAX_RANDOM_NUMBER)
