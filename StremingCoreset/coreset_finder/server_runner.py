"""
Creates and runs a server.
"""
import sys
from server import Server

# Start the server.
try:
    if __name__ == '__main__':
        server = Server(sys.argv[1])
        server.main()
except KeyboardInterrupt:
    print "caught SIGINT, dying."
    exit()
except AttributeError as e:
    print e
    exit()
