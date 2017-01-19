import sys
from server import Server

# Start the server.
try:
    server = Server(sys.argv[1])
    server.main()
except KeyboardInterrupt:
    print "caught SIGINT, dying."
    exit()
except AttributeError as e:
    print e
    exit()
