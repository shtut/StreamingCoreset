from StreamingClient import Client
import sys

#starts up the client
try:
    client = Client(sys.argv[1])
    client.run_client()
except KeyboardInterrupt:
    print "caught SIGINT, dying."
    exit()
except AttributeError as e:
    print e
    exit()

