import socket
import message_codes as codes
import numpy as np
import pickle
import connection_data as conn
import time
from CreateDatabase import createDB
import connection_util as conn_util


def _print_server_response_code(code):
    if len(code) == 0:
        print "Problem, server died"
    elif int(code) == codes.ACCEPTED:
        print "Points sent successfully!"
    else:
        print "Problem, received code", code


class Client:
    def __init__(self):
        self._socket = None

    def run_client(self):
        self._connect_server()
        db = createDB(self._process_chunk)
        db.read_from_csv('2.csv', 100)
        time.sleep(1)
        self.get_summary_points()

    def get_summary_points(self):
        print "Getting the summary..."
        self._socket.send(bytes(codes.GET_UNIFIED))
        msg = self._socket.recv(10, 0)
        length = int(msg)
        data = self._socket.recv(length, 0)
        data = pickle.loads(data)
        print "Received the summary:\n %s" % data

    def _connect_server(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', conn.client_port)
        self._socket.connect(server_address)

    def _process_chunk(self, chunk):
        print "read from csv chunk in size of: ", len(chunk)
        num_of_samples = chunk.shape[0]
        num_of_channels = chunk.shape[1]
        chunk = np.random.rand(num_of_samples, num_of_channels)
        self._send_points(chunk)

    def _send_points(self, chunk):
        conn_util.send_points(chunk, self._socket)
        self._get_server_response()

    def _get_server_response(self):
        code = self._socket.recv(1, 0)
        _print_server_response_code(code)
