"""
Creates and runs a client.
"""
from streaming_client import Client
import sys

#starts up the client
try:
    if __name__ == '__main__':
        path = 'D:\GitHub\StremingCoreset\StremingCoreset\coreset_finder\db_files'
        client = Client(sys.argv[1])
        client.run_client(path)
except KeyboardInterrupt:
    print "caught SIGINT, dying."
    exit()
except AttributeError as e:
    print e
    exit()