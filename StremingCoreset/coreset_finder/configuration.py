"""
Global variables
"""
from coreset_tree_algorithm import CoresetTeeAlgorithm
from simple_coreset import SimpleCoreset

CORESET_SIZE = 20
LEAF_SIZE = 2
WORKER_CHUNK_SIZE = 2             # size of chunks sent to the different workers (used in server)
PACKET_SIZE = 10            # size of a packet sent in the socket (client-server, server-workers)
CSV_READ_SIZE = 10          # size of the chunks read from the CSV
NUMBER_OF_WORKERS = 10       # number of workers
DEBUG = False


### restrictions
# - CORESET_SIZE must be K x LEAF_SIZE , where K is integer.
# - CORESET_SIZE must be smaller/equal to  NUMBER_OF_WORKERS x LEAF_SIZE


