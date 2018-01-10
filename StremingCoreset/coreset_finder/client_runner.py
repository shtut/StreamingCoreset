"""
Creates and runs a client.
"""
from streaming_client import Client
import sys
import os

#starts up the client
try:
    if __name__ == '__main__':
        dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(dir + os.sep, 'db_files')
        client = Client(sys.argv[1])
        client.run_client(path)
except KeyboardInterrupt:
    print "caught SIGINT, dying."
    exit()
except AttributeError as e:
    print e
    exit()