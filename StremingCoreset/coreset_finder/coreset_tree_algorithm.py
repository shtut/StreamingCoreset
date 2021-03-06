"""
Exists within each worker-
Works by creating a binary tree, where each node is of size 'CORESET_SIZE'.
The leaves are the original data, and each level above provides a smaller and better representation of the data.
The root holds the best representation of all the leaves: the core-set.
Has a configurable merging algorithm - 'CORESET-ALGORITHM'.
"""


from collections import namedtuple
import numpy as np
from stack import Stack
import array_util as utils
import configuration as cfg

StackItem = namedtuple("StackItem", "coreset level")
WeightedPointSet = namedtuple("WeightedPointSet", "points weights")


class CoresetTeeAlgorithm(object):
    def __init__(self, coreset_alg, coreset_size):
        """
        constructor
        :param coreset_alg: the provided algorithm to computer the coreset
        :param coreset_size: the required size of the coreset (and nodes)
        """
        self._coreset_alg = coreset_alg
        self._last_leaf = WeightedPointSet([], [])
        self._coreset_size = coreset_size
        self._data = Stack()

    def add_points(self, points, weights):
        """
        Adds a set of points to the stream.

        If the set is larger than coreset_size, it is split
        into several sets and a coreset is constructed on each set.
        :param weights:
        :param points: input data
        :return: none
        """
        if points.size == 0:
            return
        if weights is None:
            weights = np.ones_like(points.T[0])

        split_points = utils.array_split(points, self._coreset_size)
        split_weights = utils.array_split(weights, self._coreset_size)

        for p,w in zip(split_points,split_weights):
            if len(p) == self._coreset_size:
                # debugging prints
                if(cfg.DEBUG):
                    print "split pts and weights:"
                    print p
                    print w
                self._add_leaf(p, w)
            else:
                self._add_leftovers(p, w)

    def get_unified_coreset(self):
        """
        merges the tree and returns the unified coreset (root)
        :return:
        """
        current_data = self._data.list()
        res = None
        weights = None
        solution = None
        if(cfg.DEBUG):
            self._print_tree_data(current_data)

        solution = self._merge_solution(current_data, solution)

        if solution is not None:
            res = solution.points
            weights = solution.weights

        return WeightedPointSet(res, weights)

    def _add_leaf(self, points, weights):
        self._insert_into_tree(WeightedPointSet(points, weights))

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
        return self._activate_coreset_alg(points,weights)

    def _activate_coreset_alg(self, points, weights):
        alg = self._coreset_alg(points, weights)
        coreset, coreset_weights = alg.sample_orig(self._coreset_size)
        return WeightedPointSet(coreset, coreset_weights)

    def _add_leftovers(self, points, weights):
        # print "adding leftovers:"
        # print len(self._last_leaf.points)
        # print len(self._last_leaf.weights)
        self._last_leaf.points.extend(points)
        self._last_leaf.weights.extend(weights)

        #if last_leaf contains enough data to become a full sized leaf
        if len(self._last_leaf.points) >= self._coreset_size:
            #create a leaf from it that is coreset_size
            self._add_leaf(self._last_leaf.points[:self._coreset_size], self._last_leaf.weights[:self._coreset_size])
            #remove coreset_size of data from the last leaf
            self._last_leaf = WeightedPointSet(self._last_leaf.points[self._coreset_size:] , self._last_leaf.weights[self._coreset_size:])

    @staticmethod
    def _print_tree_data(current_data):
        """
        prints the tree data
        :param current_data:  current data
        :return: none
        """
        print "Total items in tree: %d" % (len(current_data))
        print "Tree: %s" % current_data

    def _merge_solution(self, data, solution):

        for node in data:
            coreset = node.coreset
            if solution is None:
                solution = coreset
            else:
                solution = self._merge(solution, coreset)
        return solution
