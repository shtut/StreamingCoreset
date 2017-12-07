"""
Provides a very simplistic method for merging nodes in the tree.
Contains a simple coreset algorithm - return a random portion of the data in size of coreSetSize

"""
import random
import numpy as np
from AdielCoresetDense import adielCoresetDense as ACD1
import configuration as cfg


class SimpleCoreset:
    """
    contains a simple coreset algorithm - return a random portion of the data
    In size of coreSetSize
    """

    def __init__(self, p, w):
        self._points = p
        self._weights = w

    @staticmethod
    def coreset_alg(p,w):
        return SimpleCoreset(p,w)

    #takes the maximum value for the points,  and half the weights
    def sample(self, coreSetSize):
        x = sorted(self._points, key=lambda y: np.sum(y), reverse=True)[:coreSetSize]
        weights = sorted(self._weights, key=lambda y: np.sum(y), reverse=True)[:coreSetSize]
        # weights = self._weights[:coreSetSize]
        return x, weights

    #multiplies a vector of weights by the given matrix
    #i.e :  mat = [[1,2][3,4]] vec=[2,10]
    # result = [[2,4],[30,40]]
    def multiply_by_weights(self,mat,vec):
        new_mat = np.copy(mat)
        for i in range(vec.shape[0]):
            new_mat[:,i] *= vec[i]
        return new_mat

    # GW1 is the weights vectors
    # tags1 is index matrix line is one tweet , columns is words indexes
    # x is the corset
    # weights - not relevant for our data
    def sample_orig(self, coreSetSize):
        A = ACD1(self._points)
        curr_points = self._points
        curr_weights = self._weights
        if(cfg.DEBUG):
            print "sample_orig points:"
            print curr_points
            print curr_weights
        #curr_weights=np.ravel(curr_weights)
        weighted_points= np.multiply(curr_weights,curr_points.T)
        xx, radiuses , weights , Tags1, new_weights = A.k_means_clustering(weighted_points.T, curr_weights, coreSetSize, is_sparse=1, is_plspls=0,
                                                      is_klinemeans=0)
        if (cfg.DEBUG):
            print new_weights

        x= curr_points[Tags1, :]
        # x,w,ind = A.CNW(A._points, coreSetSize)
        # e,x=A.Nonuniform_Mahuni(A._points, coreSetSize)
        return x, new_weights

    # Normalize and convert to sparse matrix size of number of different words
    def sample1(self, current_weights, coreSetSize):
        A = ACD1(self._points)
        X = self._points
        mat = np.ravel(X)  # all of the indeces of the two matrices, flatted
        unique_ind = np.unique(mat[mat > 0])  # taking only the unique and greater than 0
        X1 = np.copy(X)

        for i in range(0, len(unique_ind)):
            X1[np.where(X == unique_ind[i])] = i  # defining the original matrices with new indeces
        X_sparse = np.zeros((X1.shape[0], len(unique_ind)))

        for y in range(0, X1.shape[0]):
            X_sparse[y, X1[y, X1[y, :] > 0]] = 1  # convert them to sparce matrices
        X_sparse_cor,radiuses , weights , Tags1  =A.k_means_clustering(np.multiply(current_weights,X_sparse),5,1,1,1) #producing a coreset
        rand_ind = np.random.randint(0, 9, 5)
        x = X[rand_ind, :]
        new_weights = np.multiply(np.current_weights[Tags1], weights)
        return x, new_weights