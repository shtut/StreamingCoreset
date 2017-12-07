"""
The summary worker handles the creation of the final core-set.
Holds a regular worker.
"""
from worker import Worker
import message_codes as codes


class SummaryWorker(Worker):
    def __init__(self, server, coreset_size):
        Worker.__init__(self, server, coreset_size)

    def _worker_code(self):
        return codes.REGISTER_SUMMARY_WORKER

