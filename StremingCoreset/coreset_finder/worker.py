"""
The worker handles the creation of the core-set.
Contains an instance of 'CoresetTreeAlgorithm' which creates a binary tree from the data and returns the core-set.
"""

import logging as log
import random as rand
import socket
import sys
import array_util as util
import connection_data as conn
import message_codes as codes
from connection import Connection
from message import Message
from simple_coreset import SimpleCoreset
from coreset_tree_algorithm import CoresetTeeAlgorithm

log.basicConfig(filename='worker.log', level=log.DEBUG)
MAX_RANDOM_NUMBER = 2000
CORESET_SIZE = 10
CORSET_ALGORITHM = SimpleCoreset.coreset_alg


# CORSET_ALGORITHM = adiel.LineKMeans.coreset_alg


class Worker(object):
    def __init__(self, server):
        number = 0
        self._server = server
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

        server_connection = Connection()
        server_connection.connect(self._server, conn.worker_port)

        self._register_to_server(server_connection)

        message = server_connection.receive_message()
        command = message.code
        if command != codes.CONTINUE:
            log.error("Server sent %s, but expected codes.CONTINUE!" % command)
            server_connection.close()
            return -1

        self._handle_commands(server_connection)

        server_connection.close()

    def _handle_commands(self, server_connection):
        """
        handles the communication codes received from the server
        :param server_connection: server connection
        :return: none
        """
        while True:
            message = server_connection.receive_message()
            command = message.code
            log.debug("Received command %s" % command)
            if command == codes.ADD_POINTS:
                self._new_points(message.points)
            elif command == codes.GET_UNIFIED:
                self._get_summary(server_connection)
            elif command == codes.TERMINATE:
                break

    def _worker_code(self):
        return codes.REGISTER_WORKER

    def _register_to_server(self, server_connection):
        """
        registers the worker to the server
        :param server_connection: server connection
        :return: none
        """
        try:
            server_connection.send_message(Message(self._worker_code()))
        except socket.error:
            sys.exit()

    def _new_points(self, points):
        data = util.convert_points_to_float(points)
        self._coresetTreeBuilder.add_points(data)
        print "Got a new matrix", data.shape

    def _get_summary(self, server_connection):
        """
        returns the current tree coreset to the server
        :param server_connection: server connection
        :return: none
        """
        summary = self._coresetTreeBuilder.get_unified_coreset()
        log.debug("Sending the summary to the server %s" % summary)
        server_connection.send_message(Message(codes.SENDING, summary))
        print "Summary sent to the server. Going back to the loop."

    def _init_number(self, number):
        if number != 0:
            self._number = number
        else:
            self._number = rand.randint(1, MAX_RANDOM_NUMBER)
