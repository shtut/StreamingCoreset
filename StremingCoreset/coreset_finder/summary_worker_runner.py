"""
Creates and runs a summary worker.
"""
from summary_worker import SummaryWorker
import sys

#starts up the worker
try:
    if __name__ == '__main__':
        worker = SummaryWorker(sys.argv[1])
        worker.register_and_handle()
except KeyboardInterrupt:
    print "caught SIGINT, dying."
    exit()
except AttributeError as e:
    print e
    exit()
