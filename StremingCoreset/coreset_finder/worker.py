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
from coreset_tree_algorithm import CoresetTeeAlgorithm
from simple_coreset import SimpleCoreset
import configuration as cfg
log.basicConfig(filename='worker.log', level=log.DEBUG)


class Worker(object):
    def __init__(self, server, leaf_size):
        self._server = server
        self._coresetTreeBuilder = CoresetTeeAlgorithm(SimpleCoreset.coreset_alg, leaf_size)

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
                self._new_points(message.points, message.weights)
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

    def _new_points(self, points, weights):
        data = util.convert_points_to_float(points)
        self._coresetTreeBuilder.add_points(data, weights)
        print "Got a new matrix", data.shape

    def _get_summary(self, server_connection):
        """
        returns the current tree coreset to the server
        :param server_connection: server connection
        :return: none
        """
        summary = self._coresetTreeBuilder.get_unified_coreset()
        # log.debug("Sending the summary to the server %s" % summary)
        server_connection.send_message(Message(codes.SENDING, summary))
        print "Summary sent to the server. Going back to the loop."
