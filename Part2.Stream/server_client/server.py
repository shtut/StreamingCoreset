import time
import socket
import sys
import codes
from threading import Thread
import pickle
from Queue import PriorityQueue
import numpy as np
import logging as log
import streamUtils as utils

log.basicConfig(filename='server.log', level=log.DEBUG)


class Server:
    CHUNK_SIZE = 10

    def __init__(self, server_name):
        self._server_name = server_name
        self._registered_workers = []
        self._current_load = PriorityQueue()
        self._received_points = []
        self._handler = {
            codes.ADDPOINTS: self.forward_points_to_workers,
            codes.GETUNIFIED: self.get_summary_from_workers
        }

    def send_to_worker(self, data):
        """Sends points to the registered workers.

        The workers are chosen according to the current load which is
        defined by by the total number of points sent to the machine.
        The data is communcated in 3 steps:
        1. We communicate codes.ADDPOINTS to the worker
        2. We communicate the number of points to be sent to the worker
        3. We send the points.
        All data sent over the channel is byte-serialized.
        """
        if len(self._registered_workers) == 0:
            raise Exception("No workers available.")
        else:
            load, connection = self._current_load.get()
            serialized = pickle.dumps(data)
            size = "%010d" % (len(serialized))
            connection.send(bytes(codes.ADDPOINTS))
            connection.send(bytes(size))
            connection.send(serialized)
            self._current_load.put((load + int(size), connection))
            log.debug("Sent %s points to worker %s" % (data.shape[0], connection))

    def handle_worker_registration(self):
        """Separate thread that handles worker registration.

        Opens a socket and waits for worker connections. Accepts only
        messages codes.REGISTER_WORKER. When the message is received the
        worker is added to the queue of registered users and is added to the
        priority queue that keeps track of the worker load. For each worker
        a new thread is spawned and it handles the future communication with the
        worker while this main thread continues accepting workers.
        """

        incomming = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_name = self._server_name
        server_address = (server_name, 10000)
        incomming.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        incomming.bind(server_address)
        incomming.listen(1)

        threads_to_kill = []
        while True:
            log.debug("Main server waiting for instructions...")
            connection, client_address = incomming.accept()
            while True:
                command = int(connection.recv(1, 0))
                if command == codes.REGISTER_WORKER:
                    print "Registering worker: ", (connection, client_address)
                    self._registered_workers.append((connection, client_address))
                    self._current_load.put((0, connection))

                    # Spawn a new thread to handle the worker communication.
                    t = Thread(target=self.worker_thread, args=(connection,))
                    threads_to_kill.append(t)
                    t.start()
                    break
                else:
                    log.error("Command not recognized: %s" % command)

        # When the server goes down kill all client threads.
        for t in threads_to_kill:
            t.join()

    def worker_thread(self, sock):
        sock.send(bytes(codes.CONTINUE))
        while True:
            command = sock.recv(1, 0)
            if command == '':
                log.error("Worker has died.")
                break
            command = int(command)
            if command == codes.ACCEPTED:
                log.debug("Worker has received the points.")
            elif command == codes.SENDING:
                log.debug("Worker is sending points as requested.")
                length = int(sock.recv(10, 0))
                data = sock.recv(length, 0)
                data = pickle.loads(data)
                self._received_points.append(data)
            else:
                log.error("Received unrecognized command: %s" % command)
        sock.close()

    def handle_client(self):
        """Thread that handles the user connection.

        User is the entity using our API. They have the option to send new
        points or ask for the current coreset. In this approach, they
        connect to the server and send commands via sockets. This is ideal
        for a cloud setup. Thread opens a new port and awaits for the
        client connection.
        """

        incomming = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_name = self._server_name
        server_address = (server_name, 10001)
        incomming.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        incomming.bind(server_address)
        incomming.listen(1)

        while True:
            log.debug("Waiting for client connection...")
            connection, client_address = incomming.accept()
            while True:
                command = connection.recv(1, 0)
                if len(command) == 0:
                    break
                command = int(command)
                log.debug("Received command %s from client:" % command)
                if command not in self._handler:
                    log.error("Command not recognized: " % command)
                else:
                    self._handler[command](connection, client_address)
            connection.close()

    def main(self):
        # Start handler threads.

        worker_handler = Thread(target=self.handle_worker_registration)
        client_handler = Thread(target=self.handle_client)

        worker_handler.start()
        client_handler.start()
        print "Server is UP"
        worker_handler.join()
        client_handler.join()
        print "Server is shutting down"

    def forward_points_to_workers(self, sock, client_address):
        print "Forwarding points to workers"
        length = int(sock.recv(10, 0))
        data = sock.recv(length, 0)
        sock.send(bytes(codes.ACCEPTED))
        data = pickle.loads(data)


        for split in utils._array_split(data, self.CHUNK_SIZE):
            self.send_to_worker(split)

    def get_summary_from_workers(self, sock, client_address):
        """Queries each worker for the current summary

        Each registered worker is asked for the current summary
        via codes.GETUNIFIED. Then the function waits till all the
        chunks arrive in a for loop. When the data is ready
        it is serialized and sent to the client.
        """
        print "Getting summaries from workers"

        for worker in self._registered_workers:
            socket = worker[0]
            socket.send(bytes(codes.GETUNIFIED))

        need = len(self._registered_workers)

        while len(self._received_points) < need:
            time.sleep(1)

        log.debug("Collected all parts, sending to client...")
        points = np.vstack(self._received_points)
        serialized = pickle.dumps(points)
        size = "%010d" % (len(serialized))
        sock.sendall(bytes(size))
        sock.sendall(serialized)
        del self._received_points[:]


# # Start the server.
# try:
#     server = Server(sys.argv[1])
#     server.main()
# except KeyboardInterrupt:
#     print "caught SIGINT, dying."
#     exit()
# except AttributeError as e:
#     print e
#     exit()
