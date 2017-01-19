import socket
from connection import Connection


class ConnectionListener(object):
    def __init__(self, server_name, port):
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (server_name, port)
        self.connection_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.connection_socket.bind(server_address)
        self.connection_socket.listen(1)

    def accept(self):
        connection = Connection()
        connection._socket, connection._address = self.connection_socket.accept()
        return connection
