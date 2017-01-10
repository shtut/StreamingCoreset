import logging as log
import pickle
import socket
import time
from Queue import PriorityQueue
from threading import Thread
import numpy as np
import array_util as utils
import connection_data as conn
import message_codes as codes
import connection_util as conn_util

log.basicConfig(filename='server.log', level=log.DEBUG)


class Server(object):

    CHUNK_SIZE = 100

    def __init__(self, server_name):
        self._server_name = server_name
        self._registered_workers = []
        self._summary_worker = None
        self._current_load = PriorityQueue()
        self._received_points = []

    def main(self):
        client_handler = self._start_handlers()
        print "Server is UP"
        client_handler.join()
        print "Server is shutting down"

    def _start_handlers(self):
        worker_handler = Thread(target=self._handle_worker_registration)
        client_handler = Thread(target=self._handle_client)
        worker_handler.start()
        client_handler.start()
        return client_handler

    def _handle_worker_registration(self):
        """Separate thread that handles worker registration.

        Opens a socket and waits for worker connections. Accepts only
        messages codes.REGISTER_WORKER. When the message is received the
        worker is added to the queue of registered users and is added to the
        priority queue that keeps track of the worker load. For each worker
        a new thread is spawned and it handles the future communication with the
        worker while this main thread continues accepting workers.
        """

        incoming = self._listen(conn.worker_port)

        while True:
            self._register_workers(incoming)

    def _register_workers(self, incoming):
        log.debug("Main server waiting for instructions...")
        connection, worker_address = incoming.accept()
        command = self.receive_command(connection)
        print "Server : got command"
        if command == codes.REGISTER_WORKER:
            self._registered_workers.append((connection, worker_address))
            self._current_load.put((0, connection))

            # Spawn a new thread to handle the worker communication.
            t = Thread(target=self._worker_thread, args=(connection,))
            t.start()
            print "Registering worker: ", (connection, worker_address)
        elif command == codes.REGISTER_SUMMARY_WORKER:
            # self._summary_worker = (connection, worker_address)
            self._summary_worker = connection

            # Spawn a new thread to handle the worker communication.
            t = Thread(target=self._worker_thread, args=(connection,))
            t.start()
            print "Registering summary worker: ", (connection, worker_address)
        else:
            log.error("Command not recognized: %s" % command)

    def _listen(self, port):
        incoming = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_name = self._server_name
        server_address = (server_name, port)
        incoming.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        incoming.bind(server_address)
        incoming.listen(1)
        return incoming

    def _send_to_worker(self, data):
        """Sends points to the registered workers.

        The workers are chosen according to the current load which is
        defined by by the total number of points sent to the machine.
        The data is communcated in 3 steps:
        1. We communicate codes.ADDPOINTS to the worker
        2. We communicate the number of points to be sent to the worker
        3. We send the points.
        All data sent over the channel is byte-serialized.
        """

        #
        if len(self._registered_workers) == 0:
            raise Exception("No workers available.")

        load, worker_socket = self._current_load.get()
        size = self._send_data_to_worker(data, worker_socket)

        self._current_load.put((load + int(size), worker_socket))
        log.debug("Sent %s points to worker %s" % (data.shape[0], worker_socket))

    @staticmethod
    def _send_data_to_worker(data, worker_socket):
        # serialized = pickle.dumps(data)
        # size = "%010d" % (len(serialized))
        # worker_socket.send(bytes(codes.ADD_POINTS))
        # worker_socket.send(bytes(size))
        # worker_socket.send(serialized)
        # return size
        return conn_util.send_points(data, worker_socket)

    def _worker_thread(self, worker_socket):
        worker_socket.send(bytes(codes.CONTINUE))
        while True:
            command = worker_socket.recv(1, 0)
            if command == '':
                log.error("Worker has died.")
                break
            command = int(command)
            if command == codes.ACCEPTED:
                log.debug("Worker has received the points.")
            elif command == codes.SENDING:
                log.debug("Worker is sending points as requested.")
                length = int(worker_socket.recv(10, 0))
                data = worker_socket.recv(length, 0)
                data = pickle.loads(data)
                self._received_points.append(data)
            else:
                log.error("Received unrecognized command: %s" % command)
        worker_socket.close()

    def _handle_client(self):
        """Thread that handles the user connection.

        User is the entity using our API. They have the option to send new
        points or ask for the current coreset. In this approach, they
        connect to the server and send commands via sockets. This is ideal
        for a cloud setup. Thread opens a new port and awaits for the
        client connection.
        """

        incoming = self._listen(10001)

        log.debug("Waiting for client connection...")
        connection, client_address = incoming.accept()
        self._handel_client_commands(connection)
        connection.close()

    def _handel_client_commands(self, connection):
        while True:
            command = self.receive_command(connection)
            log.debug("Received command {0} from client:".format(command))
            if command == codes.ADD_POINTS:
                self._forward_points_to_workers(connection)
            elif command == codes.GET_UNIFIED:
                self.get_summary_from_workers(connection)
            elif command == codes.TERMINATE:
                break
            else:
                log.error("Command not recognized: ", command)

    @staticmethod
    def receive_command(connection):
        command_string = connection.recv(1, 0)
        if command_string == '':
            command_string = codes.TERMINATE
        return int(command_string)

    def _forward_points_to_workers(self, client_socket):
        print "Forwarding points to workers"
        length = int(client_socket.recv(10, 0))
        data = client_socket.recv(length, 0)
        client_socket.send(bytes(codes.ACCEPTED))
        data = pickle.loads(data)

        for split in utils.array_split(data, self.CHUNK_SIZE):
            self._send_to_worker(split)

    def get_summary_from_workers(self, client_socket):
        """Queries each worker for the current summary

        Each registered worker is asked for the current summary
        via codes.GETUNIFIED. Then the function waits till all the
        chunks arrive in a for loop. When the data is ready
        it is serialized and sent to the client.
        """
        print "Getting summaries from workers"

        self._obtain_workers_results()

        log.debug("Collected all parts, sending to client...")
        points = np.vstack(self._received_points)

        # clearing received data cache
        self._received_points = []
        # sending all 'final results' to summary worker
        self._send_to_worker(points)
        self._send_data_to_worker(points, self._summary_worker)
        self._summary_worker.send(bytes(codes.GET_UNIFIED))

        # wait for summary points
        self._wait_for_results(1)

        summary_points = np.vstack(self._received_points)
        # serialize the summary and sent back to the client

        # serialized = pickle.dumps(summary_points)
        # size = "%010d" % (len(serialized))
        # client_socket.sendall(bytes(size))
        # client_socket.sendall(serialized)

        conn_util.send_results(summary_points, client_socket)
        # conn_util.send_points(summary_points, client_socket)

        del self._received_points[:]

    def _obtain_workers_results(self):
        self._request_workers_results()
        self.wait_for_workers_results()

    def _request_workers_results(self):
        for worker in self._registered_workers:
            worker_socket = worker[0]
            worker_socket.send(bytes(codes.GET_UNIFIED))

    def wait_for_workers_results(self):
        need = len(self._registered_workers)
        self._wait_for_results(need)

    def _wait_for_results(self, need):
        while len(self._received_points) < need:
            time.sleep(1)
