"""
Online coresets.
"""

from collections import namedtuple
import numpy as np
from stack import Stack
import array_util as utils

StackItem = namedtuple("StackItem", "coreset level")
WeightedPointSet = namedtuple("WeightedPointSet", "points weights")


class CoresetTeeAlgorithm(object):
    def __init__(self, coreset_alg, coreset_size):
        self._coreset_alg = coreset_alg
        self._last_leaf = []
        self._coreset_size = coreset_size
        self._data = Stack()

    def add_points(self, points):
        """Add a set of points to the stream.

        If the set is larger than coreset_size, it is split
        into several sets and a coreset is constructed on each set.
        """
        if points.size == 0:
            return
        for split in utils.array_split(points, self._coreset_size):
            if len(split) == self._coreset_size:
                self._add_leaf(split)
            elif len(split) != 0:
                self._add_leftovers(split)

    def get_unified_coreset(self):
        current_data = self._data.list()
        res = None
        solution = None
        self._print_tree_data(current_data)

        solution = self._merge_solution(current_data, solution)

        if solution is not None:
            res = solution.points

        return res

    def _add_leaf(self, points):
        self._insert_into_tree(WeightedPointSet(points, None))

    def _insert_into_tree(self, coreset):
        level = 1
        while self._can_merge(level):
            last = self._data.pop()
            coreset = self._merge(last.coreset, coreset)
            level += 1
        self._data.push(StackItem(coreset, level))

    def _can_merge(self, level):
        if self._data.is_empty():
            return False
        elif self._data.top().level > level:
            return False
        elif self._data.top().level == level:
            return True
        else:
            raise Exception("New level should be smaller")

    def _merge(self, set1, set2):
        points = np.vstack([set1.points, set2.points])
        weights = np.hstack([set1.weights, set2.weights])
        return self._activate_coreset_alg(points, weights)

    def _activate_coreset_alg(self, points, weights):
        alg = self._coreset_alg(points, weights)
        coreset, coreset_weights = alg.sample(self._coreset_size)
        return WeightedPointSet(coreset, coreset_weights)

    def _add_leftovers(self, points):
        print "add left overs"
        print points.size
        self._last_leaf.extend(points)
        if len(self._last_leaf) >= self._coreset_size:
            self._add_leaf(self._last_leaf[:self._coreset_size])
            self._last_leaf = self._last_leaf[self._coreset_size:]

    @staticmethod
    def _print_tree_data(current_data):
        print "Total items in tree", len(current_data)
        print "Tree: %s" % current_data

    def _merge_solution(self, data, solution):
        for node in data:
            coreset = node.coreset
            if solution is None:
                solution = coreset
            else:
                solution = self._merge(solution, coreset)
        return solution
