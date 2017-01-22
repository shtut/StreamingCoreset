"""
Creates and runs a worker.
"""
from worker import Worker
import sys

#starts up the worker
try:
    if __name__ == '__main__':
        worker = Worker(sys.argv[1])
        worker.register_and_handle()
except KeyboardInterrupt:
    print "caught SIGINT, dying."
    exit()
except AttributeError as e:
    print e
    exit()
