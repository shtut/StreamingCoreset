"""
Creates and runs a worker.
"""
from worker import Worker
from threading import Thread
import configuration as cfg
import time
import sys

#starts up the worker
try:
    if __name__ == '__main__':

        # for different processes
        # worker = Worker(sys.argv[1] , sys.argv[2])
        # worker.register_and_handle()

        # for the same PC with threads
        for i in xrange(cfg.NUMBER_OF_WORKERS):
            worker = Worker(sys.argv[1], cfg.LEAF_SIZE)
            Thread(target=worker.register_and_handle).start()
            time.sleep(1)
except KeyboardInterrupt:
    print "caught SIGINT, dying."
    exit()
except AttributeError as e:
    print e
    exit()
