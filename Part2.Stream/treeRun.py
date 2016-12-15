import simpleCoreset
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
i=0
arr = []
for i in xrange(3):
    arr.append(np.arange(i*5,(i+1)*5))
    #arr.extend([np.arange(i*2, (i+1)*2)])

print utils._array_split(arr, 2)
for split in utils._array_split(arr, 2):
    print split

