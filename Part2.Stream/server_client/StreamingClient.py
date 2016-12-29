import socket
import codes
import numpy as np
import pickle
import csv
import time
from CreateDatabase import createDB


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

    def read_from_csv(self, file_name, chunksize):
        """
        The purpose of this method is to read from a given file and create an array from it
        The method reads chunk by chunk from a CSV file and process it
        :param chunksize: given size of chunk to read from CSV
        :param file_name: given file name to read from
        """

        print "start read from csv"
        print "file name is " + file_name
        print "chunk size is " + str(chunksize)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 10001)
        sock.connect(server_address)

        reader = csv.reader(open(file_name, 'rb'))
        # chunk = np.array([])
        chunk = None
        for i, line in enumerate(reader):
            # if i > 500:
            #     return
            if i % chunksize == 0 and i > 0:
                data = pickle.dumps(chunk)
                size = "%010d" % (len(data))
                sock.send(bytes(codes.ADDPOINTS))
                sock.send(bytes(size))
                sock.send(data)

                code = sock.recv(1, 0)

                if len(code) == 0:
                    print "Problem, server died"
                elif int(code) == codes.ACCEPTED:
                    print "Points sent successfully!"
                else:
                    print "Problem, received code", code
                # del chunk[:]
                chunk = None

            if chunk is None:
                chunk = np.asarray(line)
            else:
                chunk = np.vstack([chunk, np.asarray(line)])

        print "Getting the summary..."

        sock.send(bytes(codes.GETUNIFIED))
        msg = sock.recv(10, 0)
        length = int(msg)
        data = sock.recv(length, 0)
        data = pickle.loads(data)

        print "Received the summary:\n %s" % data

    def test(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 10001)
        sock.connect(server_address)

        send_size = 2000
        num_of_samples = 24
        num_of_channels = 3
        for i in xrange(10):
            # data = pickle.dumps(np.arange(i * 2, (i + 1) * 2))
            A = np.random.rand(num_of_samples, num_of_channels)
            data = pickle.dumps(A)

            size = "%010d" % (len(data))
            sock.send(bytes(codes.ADDPOINTS))
            sock.send(bytes(size))
            sock.send(data)

            code = sock.recv(1, 0)

            if len(code) == 0:
                print "Problem, server died"
            elif int(code) == codes.ACCEPTED:
                print "Points sent successfully!"
            else:
                print "Problem, received code", code

        print "Getting the summary..."

        sock.send(bytes(codes.GETUNIFIED))
        msg = sock.recv(10, 0)
        length = int(msg)
        data = sock.recv(length, 0)
        data = pickle.loads(data)

        print "Received the summary:\n %s" % data

    def run_client(self):
        self._connect_server()
        db = createDB(self._process_chunk)
        db.read_from_csv('2.csv', 100)
        time.sleep(1)
        self.get_summary_points()

    def get_summary_points(self):
        print "Getting the summary..."
        self._socket.send(bytes(codes.GETUNIFIED))
        msg = self._socket.recv(10, 0)
        length = int(msg)
        data = self._socket.recv(length, 0)
        data = pickle.loads(data)
        print "Received the summary:\n %s" % data

    def _connect_server(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 10001)
        self._socket.connect(server_address)

    def _process_chunk(self, chunk):
        print "read from csv chunk in size of: ", len(chunk)
        num_of_samples = chunk.shape[0]
        num_of_channels = chunk.shape[1]
        chunk = np.random.rand(num_of_samples, num_of_channels)
        self._send_points(chunk)

    def _send_points(self, chunk):
        data = pickle.dumps(chunk)
        size = "%010d" % (len(data))
        self._socket.send(bytes(codes.ADDPOINTS))
        self._socket.send(bytes(size))
        self._socket.send(data)
        self._get_server_response()

    def _get_server_response(self):
        code = self._socket.recv(1, 0)
        _print_server_response_code(code)

# client = Client()
# client.run_client()
# client.read_from_csv('1.csv',10000)
