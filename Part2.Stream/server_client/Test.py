from worker import Worker
import sys

if sys.argv[1] == 'summary':
    worker = Worker()
    worker.register_and_handle_summary()
elif sys.argv[1] == 'worker':
    worker = Worker()
    worker.register_and_handle()