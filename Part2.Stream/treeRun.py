import simpleCoreset
from stack import Stack
from stream import Stream

s = Stream(simpleCoreset.CoreSetHandler.coreset_alg, 4, 4)
s.add_points(range(1, 17))
res = s.get_unified_coreset()
print "####################################################"
print res.points
print "####################################################"