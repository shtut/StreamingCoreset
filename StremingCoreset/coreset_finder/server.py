"""
The server coordinates between all the registered workers and the client.
Listens to incoming commands from the client-  when receiving data, divides it between the workers for processing.
Upon request collects the unified core-set from all the workers and sends it back to the client.

"""
import logging as log
import time
from Queue import PriorityQueue
from threading import Thread

import numpy as np

import array_util as utils
import connection_data as conn
import message_codes as codes
from connectionListener import ConnectionListener
from message import Message

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
        """
        initializes the server-  makes the server prepared to register the workers and the client
        after registration listens to incoming commands and performs accordingly
        :return:
        """
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
        """
        Separate thread that handles worker registration.

        Opens a socket and waits for worker connections. Accepts only
        messages codes.REGISTER_WORKER. When the message is received the
        worker is added to the queue of registered users and is added to the
        priority queue that keeps track of the worker load. For each worker
        a new thread is spawned and it handles the future communication with the
        worker while this main thread continues accepting workers.
        :return:
        """
        worker_listener = ConnectionListener(self._server_name, conn.worker_port)

        while True:
            self._register_workers(worker_listener)

    def _register_workers(self, worker_listener):
        log.debug("Main server waiting for instructions...")
        connection = worker_listener.accept()
        message = connection.receive_message()
        command = message.code
        print "Server : got command"
        if command == codes.REGISTER_WORKER:
            self._registered_workers.append(connection)
            self._current_load.put((0, connection))
            self._start_worker_thread(connection)
            print "Registering worker: ", (connection._socket, connection._address)
        elif command == codes.REGISTER_SUMMARY_WORKER:
            self._summary_worker = connection
            self._start_worker_thread(connection)
            print "Registering summary worker: ", (connection._socket, connection._address)
        else:
            log.error("Command not recognized: %s" % command)

    def _start_worker_thread(self, connection):
        t = Thread(target=self._worker_thread, args=(connection,))
        t.start()

    def _send_to_worker(self, data):
        """
        Sends points to the registered workers.

        The workers are chosen according to the current load which is
        defined by by the total number of points sent to the machine.
        The data is communicated in 3 steps:
        1. We communicate codes.ADD_POINTS to the worker
        2. We communicate the number of points to be sent to the worker
        3. We send the points.
        All data sent over the channel is byte-serialized.
        :param data:
        :return:
        """
        if len(self._registered_workers) == 0:
            raise Exception("No workers available.")

        load, worker_connection = self._current_load.get()
        size = self._send_data_to_worker(data, worker_connection)

        self._current_load.put((load + int(size), worker_connection))
        log.debug("Sent %s points to worker %s" % (data.shape[0], worker_connection))

    @staticmethod
    def _send_data_to_worker(data, worker_connection):
        return worker_connection.send_message(Message(codes.ADD_POINTS, data))

    def _worker_thread(self, worker_connection):
        worker_connection.send_message(Message(codes.CONTINUE))
        while True:
            message = worker_connection.receive_message()
            command = message.code
            if command == codes.ACCEPTED:
                log.debug("Worker has received the points.")
            elif command == codes.SENDING:
                log.debug("Worker is sending points as requested.")
                self._received_points.append(message.points)
            elif command == codes.TERMINATE:
                log.error("worker has died")
                break
            else:
                log.error("Received unrecognized command: %s" % command)
        worker_connection.close()

    def _handle_client(self):
        """
        Thread that handles the user connection.

        User is the entity using our API. They have the option to send new
        points or ask for the current coreset. In this approach, they
        connect to the server and send commands via sockets. This is ideal
        for a cloud setup. Thread opens a new port and awaits for the
        client connection.
        :return:
        """
        client_listener = ConnectionListener(self._server_name, conn.client_port)
        log.debug("Waiting for client connection...")
        client_connection = client_listener.accept()
        self._handle_client_commands(client_connection)
        client_connection.close()

    def _handle_client_commands(self, connection):
        while True:
            message = connection.receive_message()
            command = message.code
            log.debug("Received command {0} from client:".format(command))
            if message.code == codes.ADD_POINTS:
                self._forward_points_to_workers(message.points)
                connection.send_message(Message(codes.ACCEPTED))
            elif command == codes.GET_UNIFIED:
                self.get_summary_from_workers(connection)
            elif command == codes.TERMINATE:
                break
            else:
                log.error("Command not recognized: ", command)

    def _forward_points_to_workers(self, data):
        print "Forwarding points to workers"
        for split in utils.array_split(data, self.CHUNK_SIZE):
            self._send_to_worker(split)

    def get_summary_from_workers(self, client_connection):
        """
        Queries each worker for the current summary

        Each registered worker is asked for the current summary
        via codes.GET_UNIFIED. Then the function waits till all the
        chunks arrive in a for loop. When the data is ready
        it is serialized and sent to the client.
        :param client_connection:
        :return:
        """
        print "Getting summaries from workers"

        self._obtain_workers_results()

        log.debug("Collected all parts, sending to client...")
        # remove leftover received from workers
        temp = self._received_points[:]
        for points_list in temp:
            if points_list is None:
                self._received_points.remove(points_list)

        points = np.vstack(self._received_points)

        # clearing received data cache
        self._received_points = []
        # sending all 'final results' to summary worker
        self._send_data_to_worker(points, self._summary_worker)
        self._summary_worker.send_message(Message(codes.GET_UNIFIED))

        # wait for summary points
        self._wait_for_results(1)

        summary_points = np.vstack(self._received_points)
        client_connection.send_message(Message(codes.SENDING, summary_points))

        del self._received_points[:]

    def _obtain_workers_results(self):
        self._request_workers_results()
        self._wait_for_workers_results()

    def _request_workers_results(self):
        for worker_connection in self._registered_workers:
            worker_connection.send_message(Message(codes.GET_UNIFIED))

    def _wait_for_workers_results(self):
        need = len(self._registered_workers)
        self._wait_for_results(need)

    def _wait_for_results(self, need):
        while len(self._received_points) < need:
            time.sleep(1)
