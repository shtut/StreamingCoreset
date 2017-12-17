"""
Streaming client mimics the client.
It generates the data and streams it to the server, then requests the summary.
"""

import time
from datetime import datetime
import array_util
import connection_data as conn
import message_codes as codes
from create_database import createDB
from connection import Connection
from message import Message
import os
import configuration as cfg
import threading


def _print_server_response_code(code):
    if code == codes.TERMINATE:
        print "Problem, server died"
    elif int(code) == codes.ACCEPTED:
        print "Points sent successfully!"
    else:
        print "Problem, received code", code


class Client:
    def __init__(self, server):
        self._server = server
        self._connection = Connection()

    def run_client(self, path):
        """
        starts the client. creates a database and sends it to the server,  then asks for the summary (coreset)
        :return:
        """
        self._connect_server()
        db = createDB(self._process_chunk)
        csv_files = self.find_csv_filenames(path)
        for file in csv_files:
            db.read_from_csv(path, file, cfg.CSV_READ_SIZE)
        time.sleep(1)
        self.get_summary_points()

    def parse_and_send_data(self,path):
        db = createDB(self._process_chunk)
        csv_files = self.find_csv_filenames(path)
        for file in csv_files:
            time.sleep(10)
            db.read_from_csv(path, file, cfg.CSV_READ_SIZE)

    def find_csv_filenames(self, path, suffix=".csv"):
        """
        Return a list of file names with given suffix in specific path
        The list is sorted by creation time
        :param path: given path to files names
        :param suffix: suffix of files to look for, by default ".csv"
        :return:sorted strings list of file names sorted by creation time
        """
        fileNames = os.listdir(path)
        # sort file on creation time
        fileNames.sort(key=lambda x: os.stat(os.path.join(path, x)).st_ctime )
        return [filename for filename in fileNames if filename.endswith(suffix)]

    def get_summary_points(self):
        """
            requests and handles the summary (coreset) from the server
        :return:
        """

        print "Getting the summary..."
        self._connection.send_message(Message(codes.GET_UNIFIED))

        for summary in cfg.CORESET_SIZE:
            start = datetime.now()
            message = self._connection.receive_message()
            data = [message.points, message.weights]
            print "Received the summary of size ",summary
            print "Points:\n %s" % data[0]
            print "Weights:\n %s" % data[1]
            end = datetime.now()
            total = end - start

            db = createDB(self._process_chunk)
            file_name = "coreset_size_{0}_total_time_{1}".format(summary,total.total_seconds())
            print file_name
            #file_name = "coreset_size_%s_output_start %s.%s.%s.%s end %s.%s.%s.%s total %s" % (summary, start.hour,start.minute, start.second, start.microsecond, end.hour,end.minute, end.second, end.microsecond, total.total_seconds())
            db.write_matrix_to_csv(file_name + ".csv", data)

    def _connect_server(self):
        """
        connects to the server
        :return:
        """
        self._connection.connect(self._server, conn.client_port)

    def _process_chunk(self, chunk):
        print "read from csv chunk in size of: ", len(chunk)
        self._send_points(array_util.convert_points_to_float(chunk))

    def _send_points(self, chunk):
        self._connection.send_message(Message(codes.ADD_POINTS, chunk))
        self._get_server_response()

    def _get_server_response(self):
        message = self._connection.receive_message()
        _print_server_response_code(message.code)
