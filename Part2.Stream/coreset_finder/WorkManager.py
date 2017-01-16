import sys
import time
from threading import Thread
import psutil
from StreamingClient import Client
from SummaryWorker import SummaryWorker
import connection_data as conn
from coreset_finder.server import Server
from worker import Worker


class WorkManager:
    def __init__(self, workers_num):
        self._workers_num = workers_num
        pass

    @property
    def number_of_workers(self):
        """
        number of workers to launch
        """
        return self._workers_num

    def main(self):
        # start server
        self._run_server()
        time.sleep(1)
        self._start_workers()
        self._start_summary_worker()
        self._run_client()

    @staticmethod
    def _run_server():
        server = Server("localhost")
        t = Thread(target=server.main)
        t.start()

    @staticmethod
    def _run_client():
        client = Client(conn.server_ip)
        client.run_client()

    @staticmethod
    def _start_summary_worker():
        summary_worker = SummaryWorker(conn.server_ip)
        Thread(target=summary_worker.register_and_handle).start()
        time.sleep(1)

    def _start_workers(self):
        for i in xrange(self.number_of_workers):
            worker = Worker(conn.server_ip)
            Thread(target=worker.register_and_handle).start()
            time.sleep(1)


def kill_process(process_name):
    for process in psutil.process_iter():
        # check whether the process name matches
        if process.name() == process_name:
            process.kill()


try:
    manager = WorkManager(2)
    manager.main()
    # time.sleep(3 * manager.number_of_workers)
    kill_process("python.exe")
    sys.exit()


except KeyboardInterrupt:
    print "caught SIGINT, dying."
    exit()
except AttributeError as e:
    print e
    exit()
except:
    exit()
