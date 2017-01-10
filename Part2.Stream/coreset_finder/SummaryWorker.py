from worker import Worker
import message_codes as codes


class SummaryWorker(Worker):
    def _worker_code(self):
        return codes.REGISTER_SUMMARY_WORKER

