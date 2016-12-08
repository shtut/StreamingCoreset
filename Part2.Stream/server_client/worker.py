import logging as log
import pickle
import socket
import time
import sys
sys.path.insert(0, "../")

import codes
from simpleCoreset import CoreSetHandler
from CoresetTreeBuilder import CoresetTreeBuilder

log.basicConfig(filename='worker.log', level=log.DEBUG)


class Worker:

    def __init__(self):
        self._coresetTreeBuilder = CoresetTreeBuilder(CoreSetHandler.coreset_alg, 10, 10)

    def register_and_handle(self):
        """Registers with the server and enters the send/receive loop.

        Connects to the server and tries to register. If successfull it
        starts waiting for commands, otherwise it stops and reports an
        error.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 10000)
        sock.connect(server_address)
        sock.sendall(bytes(codes.REGISTER_WORKER))

        command = int(sock.recv(1, 0))
        if command != codes.CONTINUE:
            log.error("Server sent %s, but expected codes.CONTINUE!" % command)
            sock.close()
            return -1

        # Server accepted the worker. Await for commands.
        while True:
            command = int(sock.recv(1, 0))
            log.debug("Received command %s" % command)
            if command == codes.ADDPOINTS:
                self.new_points(sock)
            elif command == codes.GETUNIFIED:
                self.get_summary(sock)

        sock.close()

    def new_points(self,sock):
        length = int(sock.recv(10, 0))
        data = sock.recv(length, 0)
        sock.send(bytes(codes.ACCEPTED))
        a = pickle.loads(data)
        self._coresetTreeBuilder.add_points(a)
        print "Got a new matrix", a.shape

    def get_summary(self,sock):
        summary = self._coresetTreeBuilder.get_unified_coreset()
        log.debug("Sending the summary to the server %s" % summary)
        time.sleep(5)
        serialized = pickle.dumps(summary)
        size = "%10d" % (len(serialized))
        sock.send(bytes(codes.SENDING))
        sock.send(bytes(size))
        sock.send(serialized)
        print "Summary sent to the server. Going back to the loop."


worker = Worker()
worker.register_and_handle()
