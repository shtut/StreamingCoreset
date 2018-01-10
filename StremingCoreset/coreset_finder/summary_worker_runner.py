"""
Creates and runs a summary worker.
"""
from summary_worker import SummaryWorker
import configuration as cfg
from threading import Thread
import time
import sys

#starts up the worker
try:
    if __name__ == '__main__':
        # for different processes
        # worker = SummaryWorker(sys.argv[1] , sys.argv[2])
        # worker.register_and_handle()

        # for the same PC with threads
        for coreset in cfg.CORESET_SIZE:
            summary_worker = SummaryWorker(sys.argv[1], coreset)
            # Thread(target=summary_worker.register_and_handle).start()
            summary_worker.register_and_handle()
            time.sleep(1)

except KeyboardInterrupt:
    print "caught SIGINT, dying."
    exit()
except AttributeError as e:
    print e
    exit()
