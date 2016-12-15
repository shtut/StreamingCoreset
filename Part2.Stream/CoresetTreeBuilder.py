"""
Online coresets.
"""

from collections import namedtuple
import numpy as np
from stack import Stack
import streamUtils as utils

StackItem = namedtuple("StackItem", "coreset level")
WeightedPointSet = namedtuple("WeightedPointSet", "points weights")




class CoresetTreeBuilder(object):
    def __init__(self, coreset_alg, coreset_size):
        self.coreset_alg = coreset_alg
        self.last_leaf = []
        self.coreset_size = coreset_size
        self.stack = Stack()

    def _merge(self, pset1, pset2):
        points = np.hstack([pset1.points, pset2.points])
        weights = np.hstack([pset1.weights, pset2.weights])
        return self._activate_coreset_alg(points, weights)
        
    def _activate_coreset_alg(self, points, weights):
        cset = self.coreset_alg(points, weights, 10, 10)
        coreset, coresetWeights = cset.sample(self.coreset_size)
        return WeightedPointSet(coreset, coresetWeights)

    def _add_leaf(self, points):
        self._insert_into_tree(WeightedPointSet(points, None))

    def _can_merge(self, level):
        if self.stack.is_empty():
            return False
        elif self.stack.top().level > level:
            return False
        elif self.stack.top().level == level:
            return True
        else:
            raise Exception("New level should be smaller")

    def _insert_into_tree(self, coreset):
        level = 1
        while self._can_merge(level):
            last = self.stack.pop()
            coreset = self._merge(last.coreset, coreset)
            level += 1
        self.stack.push(StackItem(coreset, level))

    def add_points(self, points):
        """Add a set of points to the stream.

        If the set is larger than coreset_size, it is split
        into several sets and a coreset is constructed on each set.
        """
        if points.size == 0:
            return
        
        for split in utils._array_split(points, self.coreset_size):
            if len(split) == self.coreset_size:
                self._add_leaf(split)
            else:
                if len(split) == 0:
                    return
                # self.last_leaf = np.concatenate([self.last_leaf, split], axis=0)
                self.last_leaf.extend(split)
                # print "###########################"
                # print "last leaf"
                # print self.last_leaf
                # print "###########################"
                # Not enough points, check whether the last leaf
                # and these points are enough to construct a coreset.
                # if len(self.last_leaf) == 0:
                #     self.last_leaf = points
                if len(self.last_leaf) >= self.coreset_size:
                    self._add_leaf(self.last_leaf[:self.coreset_size])
                    self.last_leaf = self.last_leaf[self.coreset_size:]

    def get_unified_coreset(self):
        solution = None

        print "Total items in tree", len(self.stack.items)
        print "Tree: %s" % self.stack

        if len(self.last_leaf) > 0:
            # construct a coreset of the remaining points
            print "Leftover points in the last leaf: %s" % len(self.last_leaf)
            cset = self.coreset_alg(self.last_leaf, None, 10, 10)
            coreset, weights = cset.sample(self.coreset_size)
            solution = WeightedPointSet(coreset, weights)

        while not self.stack.is_empty():
            coreset = self.stack.pop().coreset
            if solution is None:
                solution = coreset
            else:
                solution = self._merge(solution, coreset)

        return solution.points
