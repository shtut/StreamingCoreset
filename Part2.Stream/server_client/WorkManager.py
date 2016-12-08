from worker import Worker
from server import Server
from threading import Thread
from StreamingClient import Client


class WorkManager:
    def __init__(self):
        pass

    def main(self):
        # number of workers to launch
        workers_num = 2
        # start server
        server = Server("localhost")
        Thread(target=server.main).start()

        # start workers
        for i in xrange(workers_num):
            worker = Worker()
            Thread(target=worker.register_and_handle).start()

        # call client
        client = Client()
        Thread(target=client.test).start()


try:
    manager = WorkManager()
    manager.main()

except KeyboardInterrupt:
    print "caught SIGINT, dying."
    exit
except AttributeError as e:
    print e
    exit
except:
    exit
