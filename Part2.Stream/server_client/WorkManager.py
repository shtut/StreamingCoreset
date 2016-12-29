from worker import Worker
from server import Server
from threading import Thread
from StreamingClient import Client
import time
import sys
import psutil


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
        server = Server("localhost")
        Thread(target=server.main).start()
        time.sleep(1)
        # start workers
        for i in xrange(self.number_of_workers):
            worker = Worker()
            Thread(target=worker.register_and_handle).start()
            time.sleep(1)

        # start the summary worker
        summaryWorker = Worker()
        Thread(target=summaryWorker.register_and_handle_summary).start()
        time.sleep(1)

        # call client
        client = Client()
        # t = Thread(target=client.run_client)
        client.run_client()


def kill_process(process_name):
    for process in psutil.process_iter():
        # check whether the process name matches
        if process.name() == process_name:
            process.kill()


try:
    manager = WorkManager(1)
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
