from SummaryWorker import SummaryWorker
import sys

#starts up the worker
try:
    worker = SummaryWorker(sys.argv[1])
    worker.register_and_handle()
except KeyboardInterrupt:
    print "caught SIGINT, dying."
    exit()
except AttributeError as e:
    print e
    exit()
