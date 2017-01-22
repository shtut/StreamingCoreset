"""
Creates and runs a client.
"""
from StreamingClient import Client
import sys

#starts up the client
try:
    if __name__ == '__main__':
        client = Client(sys.argv[1])
        client.run_client()
except KeyboardInterrupt:
    print "caught SIGINT, dying."
    exit()
except AttributeError as e:
    print e
    exit()

