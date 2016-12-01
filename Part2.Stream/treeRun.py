import simpleCoreset
from stream import Stream

s = Stream(simpleCoreset.CoreSetHandler.coreset_alg,4, 4)
s.add_points(range(1,16))
res =  s.get_unified_coreset()
print res.points