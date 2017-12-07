"""
Simulates the entire working system.
Sets a server, registers a number of workers (defined in the WorkManager constructor) and a summary worker, and connects a clients.

The client creates a DB and sends the data to the server.
Then it asks for the summary which the server provides, and exits.
"""
import sys
import time
from threading import Thread
import psutil
from streaming_client import Client
from summary_worker import SummaryWorker
import connection_data as conn
from server import Server
from worker import Worker
import signal
import configuration as cfg


class WorkManager:
    def __init__(self, workers_num):
        self._workers_num = workers_num
        pass

    @property
    def number_of_workers(self):
        """
        number of workers to launch
        :return:
        """
        return self._workers_num

    def main(self):
        """
        starts the server, registers workers and runs the client
        :return:
        """
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
        path = 'C:\Users\Hadas\Dropbox\coreset_finder_weights\coreset_finder\iterable'
        client = Client(conn.server_ip)
        signal.signal(signal.SIGBREAK, client.get_summary_points_param)
        client.run_client(path)

    @staticmethod
    def _start_summary_worker():
        summary_worker = SummaryWorker(conn.server_ip, cfg.CORESET_SIZE)
        Thread(target=summary_worker.register_and_handle).start()
        time.sleep(1)

    def _start_workers(self):
        for i in xrange(self.number_of_workers):
            worker = Worker(conn.server_ip, cfg.LEAF_SIZE)
            Thread(target=worker.register_and_handle).start()
            time.sleep(1)


def kill_process(process_name):
    """
    given process name, kills the process
    :param process_name: process name
    :return: None
    """
    for process in psutil.process_iter():
        # check whether the process name matches
        if process.name() == process_name:
            process.kill()


try:
    if __name__ == '__main__':
        manager = WorkManager(cfg.NUMBER_OF_WORKERS)
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
