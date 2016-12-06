import time
import socket
import sys
import codes
from threading import Thread
import pickle
from Queue import PriorityQueue
import numpy as np
import logging as log

log.basicConfig(filename='server.log', level=log.DEBUG)

registered_workers = []
current_load = PriorityQueue()
CHUNK_SIZE = 5
received_points = []


def send_to_worker(data):
    """Sends points to the registered workers.

    The workers are chosen according to the current load which is
    defined by by the total number of points sent to the machine.
    The data is communcated in 3 steps:
    1. We communicate codes.ADDPOINTS to the worker
    2. We communicate the number of points to be sent to the worker
    3. We send the points.
    All data sent over the channel is byte-serialized.
    """
    if len(registered_workers) == 0:
        raise Exception("No workers available.")
    else:
        load, connection = current_load.get()
        serialized = pickle.dumps(data)
        size = "%010d" % (len(serialized))
        connection.send(bytes(codes.ADDPOINTS))
        connection.send(bytes(size))
        connection.send(serialized)
        current_load.put((load + int(size), connection))
        log.debug("Sent %s points to worker %s" % (data.shape[0], connection))


def handle_worker_registration():
    """Separate thread that handles worker registration.

    Opens a socket and waits for worker connections. Accepts only
    messages codes.REGISTER_WORKER. When the message is received the
    worker is added to the queue of registered users and is added to the
    priority queue that keeps track of the worker load. For each worker
    a new thread is spawned and it handles the future communication with the
    worker while this main thread continues accepting workers.
    """
    incomming = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_name = sys.argv[1]
    server_address = (server_name, 10000)
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
                registered_workers.append((connection, client_address))
                current_load.put((0, connection))

                # Spawn a new thread to handle the worker communication.
                t = Thread(target=worker_thread, args=(connection, ))
                threads_to_kill.append(t)
                t.start()
                break
            else:
                log.error("Command not recognized: %s" % command)

    # When the server goes down kill all client threads.
    for t in threads_to_kill:
        t.join()


def worker_thread(sock):
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
            received_points.append(data)
        else:
            log.error("Received unrecognized command: %s" % command)
    sock.close()


def handle_client():
    """Thread that handles the user connection.

    User is the entity using our API. They have the option to send new
    points or ask for the current coreset. In this approach, they
    connect to the server and send commands via sockets. This is ideal
    for a cloud setup. Thread opens a new port and awaits for the
    client connection.
    """

    incomming = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_name = sys.argv[1]
    server_address = (server_name, 10001)
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
            if command not in handler:
                log.error("Command not recognized: " % command)
            else:
                handler[command](connection, client_address)
        connection.close()


def main():
    # Start handler threads.
    worker_handler = Thread(target=handle_worker_registration)
    client_handler = Thread(target=handle_client)

    worker_handler.start()
    client_handler.start()
    worker_handler.join()
    client_handler.join()


def forward_points_to_workers(sock, client_address):
    print "Forwarding points to workers"
    length = int(sock.recv(10, 0))
    data = sock.recv(length, 0)
    sock.send(bytes(codes.ACCEPTED))
    data = pickle.loads(data)

    for split in np.array_split(data, CHUNK_SIZE):
        send_to_worker(split)


def get_summary_from_workers(sock, client_address):
    """Queries each worker for the current summary

    Each registered worker is asked for the current summary
    via codes.GETUNIFIED. Then the function waits till all the
    chunks arrive in a for loop. When the data is ready
    it is serialized and sent to the client.
    """
    print "Getting summaries from workers"

    for worker in registered_workers:
        socket = worker[0]
        socket.send(bytes(codes.GETUNIFIED))

    need = len(registered_workers)

    while len(received_points) < need:
        time.sleep(1)

    log.debug("Collected all parts, sending to client...")
    points = np.vstack(received_points)
    serialized = pickle.dumps(points)
    size = "%010d" % (len(serialized))
    sock.sendall(bytes(size))
    sock.sendall(serialized)
    del received_points[:]


handler = {
    codes.ADDPOINTS: forward_points_to_workers,
    codes.GETUNIFIED: get_summary_from_workers
}

# Start the server.
try:
	main()
except KeyboardInterrupt:
	print "caught SIGINT, dying."
	exit
except AttributeError as e:
	print e
	exit
