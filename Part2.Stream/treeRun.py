import simpleCoreset
import adiel
from stack import Stack
from CoresetTreeBuilder import CoresetTreeBuilder
import numpy as np
import streamUtils as utils

#s = CoresetTreeBuilder(simpleCoreset.CoreSetHandler.coreset_alg, 20)
# s.add_points(np.random.rand(1000,100))
# res = s.get_unified_coreset()
# print "####################################################"
# print res.points
# print "####################################################"
# i=0
# arr = []
# for i in xrange(3):
#     arr.append(np.arange(i*5,(i+1)*5))
#     #arr.extend([np.arange(i*2, (i+1)*2)])
#
# print utils._array_split(arr, 2)
# for split in utils._array_split(arr, 2):
#     print split

# ctb = CoresetTreeBuilder(simpleCoreset.CoreSetHandler.coreset_alg, 20)
ctb = CoresetTreeBuilder(adiel.LineKMeans.coreset_alg, 20)
num_of_samples = 24
num_of_channels = 3
CHUNK_SIZE = 12
for i in xrange(1):
    # data = pickle.dumps(np.arange(i * 2, (i + 1) * 2))
    A = np.random.rand(num_of_samples, num_of_channels)
    for split in utils._array_split(A, CHUNK_SIZE):
        ctb.add_points(split)

print ctb.get_unified_coreset()