import simpleCoreset
from stack import Stack
from CoresetTreeBuilder import CoresetTreeBuilder
import  numpy as np

s = CoresetTreeBuilder(simpleCoreset.CoreSetHandler.coreset_alg, 20)
s.add_points(np.random.rand(1000,100))
res = s.get_unified_coreset()
print "####################################################"
print res.points
print "####################################################"
