import time
import array_util
import connection_data as conn
import message_codes as codes
from CreateDatabase import createDB
from connection import Connection
from message import Message


def _print_server_response_code(code):
    if code == codes.TERMINATE:
        print "Problem, server died"
    elif int(code) == codes.ACCEPTED:
        print "Points sent successfully!"
    else:
        print "Problem, received code", code


class Client:
    def __init__(self):
        self._connection = Connection()

    def run_client(self):
        """
        starts the client. creates a database and sends it to the server,  then asks for the summary (coreset)
        :return:
        """
        self._connect_server()
        db = createDB(self._process_chunk)
        db.read_from_csv('2.csv', 100)
        time.sleep(1)
        self.get_summary_points()

    def get_summary_points(self):
        """
            requests and handles the summary (coreset) from the server
        :return:
        """
        print "Getting the summary..."
        self._connection.send_message(Message(codes.GET_UNIFIED))
        message = self._connection.receive_message()
        data = message.points
        print "Received the summary:\n %s" % data

    def _connect_server(self):
        """
        connects to the server
        :return:
        """
        self._connection.connect(conn.server_ip, conn.client_port)

    def _process_chunk(self, chunk):
        print "read from csv chunk in size of: ", len(chunk)
        self._send_points(array_util.convert_points_to_float(chunk))

    def _send_points(self, chunk):
        self._connection.send_message(Message(codes.ADD_POINTS, chunk))
        self._get_server_response()

    def _get_server_response(self):
        message = self._connection.receive_message()
        _print_server_response_code(message.code)
