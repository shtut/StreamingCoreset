# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 14:22:50 2017

@author: statman2
"""

from __future__ import division
import scipy.io
import numpy as np
import time as time
from numpy.linalg import inv
import matplotlib.pyplot as plt


class adielCoresetDense:
    """
    contains a simple coreset algorithm - return a random portion of the data
    In size of coreSetSize
    """

    def __init__(self, p):
        self._points = p

    def initializing_data(self, Q, k):
        U, D, V = np.linalg.svd(np.transpose(Q), full_matrices=True)
        D = np.diag(D)
        Z = V[:, 0:2 * k]
        V_k = V[:, 0:k]
        DVk = np.dot(D[0:k, 0:k], np.transpose(V_k))
        Q_k = np.dot(U[:, 0:k], DVk)
        ZZt = np.dot(Z, np.transpose(Z))
        Qt = np.transpose(Q)
        A_2t = (np.sqrt(k) / np.linalg.norm(Q - np.transpose(Q_k), 'fro')) * (Qt - np.dot(Qt, ZZt))
        A_2 = np.transpose(A_2t)
        An = np.concatenate((Z, A_2), 1)

        return An, A_2

    def calc_error(self, A, SA, k):
        AtA = np.dot(np.transpose(A), A)
        SAtSA = np.dot(np.transpose(SA), SA)

        ro = 100
        d = AtA.shape[0]
        X = np.random.rand(d, d - k)
        V, R = np.linalg.qr(X)
        Vt = np.transpose(V)
        VtAtAV = np.dot(Vt, np.dot(AtA, V))
        VtSAtSAV = np.dot(Vt, np.dot(SAtSA, V))
        if np.trace(VtSAtSAV) == 0:
            newro = 1
        else:
            newro = np.abs(np.trace(VtAtAV) / np.trace(VtSAtSAV))
        j = 0

        while np.logical_and(max(ro / newro, newro / ro) > 1.01, j < 10):
            j = j + 1
            ro = newro

            G = AtA - ro * SAtSA
            w, v = np.linalg.eig(G)
            V = v[:, 0:d - k]
            Vt = np.transpose(V)
            VtAtAV = np.dot(Vt, np.dot(AtA, V))
            VtSAtSAV = np.dot(Vt, np.dot(SAtSA, V))
            newro = np.abs(np.trace(VtAtAV) / np.trace(VtSAtSAV))
        roS = 100
        d = AtA.shape[0]
        X = np.random.rand(d, d - k)
        V, R = np.linalg.qr(X)
        Vt = np.transpose(V)
        VtAtAV = np.dot(Vt, np.dot(AtA, V))
        VtSAtSAV = np.dot(Vt, np.dot(SAtSA, V))
        newroS = np.abs(np.trace(VtAtAV) / np.trace(VtSAtSAV))
        j = 0
        while np.logical_and(max(roS / newroS, newroS / roS) > 1.01, j < 10):
            j = j + 1
            roS = newroS
            G = SAtSA - roS * AtA
            w, v = np.linalg.eig(G)
            V = v[:, 0:d - k]
            Vt = np.transpose(V)
            VtAtAV = np.dot(Vt, np.dot(AtA, V))
            VtSAtSAV = np.dot(Vt, np.dot(SAtSA, V))
            newroS = np.abs(np.trace(VtSAtSAV) / np.trace(VtAtAV))
        return max(np.abs(newroS - 1), np.abs(newro - 1), np.abs(1 - newro), np.abs(1 - newroS))

    def Nonuniform_Mahuni(self, AA, size_of_coreset):

        B = AA
        A = np.transpose(AA)
        start = time.time()
        n = A.shape[1]
        p = np.zeros(n)
        p = np.multiply(np.sqrt(np.sum(np.power(A, 2), 0)), np.sqrt(np.sum(np.power(B, 2), 1)))
        print('sA', np.sqrt(np.sum(np.power(A, 2), 0)))
        print('sB', np.sqrt(np.sum(np.power(B, 2), 1)))

        c = int(size_of_coreset)

        # S=np.zeros((n,c))
        D = np.zeros((c, c))
        comsum_p = np.cumsum(p)
        comsum_p = comsum_p / comsum_p[n - 1]
        p = p / sum(p)  # normalizing p in order that its sum will be 1.
        DMM_ind = np.zeros((c,), dtype=np.int)
        w = np.zeros(n + 1)
        for t in range(0, c):
            r = np.random.rand(1,
                               1)  # choosing a arbitrary r and the chosen row will be the one that the r is between its cumulative borders
            where_p = np.where(r < comsum_p)  # finding all indeces of Fmin that are greater than r
            where_p1 = where_p[1]  # choosing the first index
            D[t, t] = 1 / np.sqrt(c * p[where_p1[0]])
            # S[where_p1[0],t]=1
            DMM_ind[t] = int(where_p1[0])
        print('D', D)

        w22 = np.zeros((size_of_coreset, 1))
        w22[:, 0] = np.diag(D)
        SA0 = np.multiply(w22, B[DMM_ind, :])

        return SA0, w22, DMM_ind

    # def CNW(A1,k,coreset_size):
    #    
    #        """
    #        This function operates the CNW algorithm, exactly as elaborated in Feldman & Ras
    #
    #        inputs:
    #        A: data matrix, n points, each of dimension d.
    #        k: an algorithm parameter which determines the normalization neededand the error given the coreset size.
    #        coreset_size: the maximal coreset size (number of lines inequal to zero) demanded for input.
    #        output:
    #        error: The error between the original data to the CNW coreset.        
    #        duration: the duration this CNW operation lasted
    #        """
    #        A,A3=initializing_data(A1,k)
    #        At=np.transpose(A)
    #        AtA=np.dot(At,A)
    #        num_of_samples = A.shape[0]
    #        num_of_channels = A.shape[1]
    #
    #       
    #
    #        i=np.int(np.floor(min(A.shape[0],coreset_size))) #end of loop
    #        
    #
    #        ww = np.zeros((coreset_size,1))
    #
    #        Z = np.zeros((num_of_channels,num_of_channels))
    #
    #        X_u = k*np.diag(np.ones(num_of_channels))
    #        X_l =-k*np.diag(np.ones(num_of_channels))
    #        epsi = np.power(k/i, 1/2)
    #        delta_u = epsi+2*np.power(epsi, 2)
    #        delta_l = epsi-2*np.power(epsi, 2)
    #        j=1 #in the algorithm the maxinal epsilon is 0.5, thus the coreset cannot be less than 4k
    #        ind=np.zeros(coreset_size, dtype=np.int)
    #        while j<i+1:#each time another row is added to the coreset.
    #
    #             X_u=X_u+delta_u*AtA
    #             X_l=X_l+delta_l*AtA
    #             Z,jj,t=single_CNW_iteration(A,At,delta_u,delta_l,X_u,X_l,Z)
    #             ww[j-1]=t
    #
    #             ind[j-1]=jj
    #             print('iter',j)
    #
    #             j=j+1  
    #
    #        sqrt_ww=np.sqrt(epsi*ww/k) #%because Z=(SA)'(SA) so for s we may take sqrt(t)
    #
    #        weights=sqrt_ww        
    #        SA0=np.multiply(weights,A1[ind,:])
    #
    #        return SA0,weights,ind


    def SCNW(self, A1, k, coreset_size, is_scaled):

        """
            This function operates the CNW algorithm, exactly as elaborated in Feldman & Ras

            inputs:
            A: data matrix, n points, each of dimension d.
            k: an algorithm parameter which determines the normalization neededand the error given the coreset size.
            coreset_size: the maximal coreset size (number of lines inequal to zero) demanded for input.
            output:
            error: The error between the original data to the CNW coreset.
            duration: the duration this CNW operation lasted
            """

        A, A3 = self.initializing_data(A1, k)

        At = np.transpose(A)
        AtA = np.dot(At, A)

        num_of_samples = A.shape[0]
        num_of_channels = A.shape[1]

        i = np.int(np.floor(min(A.shape[0], coreset_size)))  # end of loop
        ww = np.zeros((coreset_size, 1))

        Z = np.zeros((num_of_channels, num_of_channels))

        if is_scaled == 1:
            epsi = np.power(k / num_of_samples, 1 / 2)
            X_u = k * np.sqrt(1 / num_of_samples) * np.diag(np.ones(num_of_channels))
            X_l = -k * np.sqrt(1 / num_of_samples) * np.diag(np.ones(num_of_channels))

        else:
            epsi = np.power(k / coreset_size, 1 / 2)
            X_u = k * np.diag(np.ones(num_of_channels))
            X_l = -k * np.diag(np.ones(num_of_channels))
        delta_u = epsi + 2 * np.power(epsi, 2)
        delta_l = epsi - 2 * np.power(epsi, 2)
        j = 1  # in the algorithm the maxinal epsilon is 0.5, thus the coreset cannot be less than 4k
        ind = np.zeros(coreset_size, dtype=np.int)
        while j < i + 1:  # each time another row is added to the coreset.
            X_u = X_u + delta_u * AtA
            X_l = X_l + delta_l * AtA
            # print('iter',j)
            Z, jj, t = self.single_CNW_iteration(A, At, delta_u, delta_l, X_u, X_l, Z)
            ww[j - 1] = t
            ind[j - 1] = jj
            j = j + 1

        if is_scaled == 1:
            sqrt_ww = np.sqrt(
                num_of_samples * epsi * ww / (coreset_size * k))  # %because Z=(SA)'(SA) so for s we may take sqrt(t)
        else:
            sqrt_ww = np.sqrt(epsi * ww / k)
            # %because Z=(SA)'(SA) so for s we may take sqrt(t)

        weights = sqrt_ww
        SA0 = np.multiply(weights, A1[ind, :])

        return SA0, weights, ind

    def single_CNW_iteration(self, A, At, delta_u, delta_l, X_u, X_l, Z):
        M_u = inv(X_u - Z)
        M_l = inv(Z - X_l)
        betha_diff = np.zeros((A.shape[0], 2))
        L = np.dot(A, np.dot(M_l, At))
        L2 = np.dot(L, L)
        U = np.dot(A, np.dot(M_u, At))
        U2 = np.dot(U, U)
        betha_l0 = L2 / (delta_l * np.trace(L2)) - L
        betha_u0 = U2 / (delta_u * np.trace(U2)) + U
        betha_l = np.diag(betha_l0)
        betha_u = np.diag(betha_u0)

        betha_diff = betha_l - betha_u
        betha_diff2 = np.argsort(betha_diff)
        # print('betha_diff2',betha_diff[betha_diff2])
        h = A.shape[0]
        jj = betha_diff2[h - 1]
        # print('betha_u',betha_u[jj])
        # print('betha_l',betha_l[jj])

        t = (1 / betha_u[jj])  # should be between (1/betha_l[jj]) to (1/betha_u[jj])
        aj = np.zeros((1, A.shape[1]))
        aj[0, :] = A[jj, :]
        # w[jj,0]=w[jj]+np.power(t,1)

        ajtaj = np.dot(np.transpose(aj), aj)
        Z = Z + np.power(t, 1) * ajtaj
        return Z, jj, t

    def initial_k_lines(self, A, clus_num):
        """
        This funtion operates the kmeans++ initialization algorithm. each point chosed under the Sinus probability.
        Input:
            A: data matrix, n points, each on a sphere of dimension d.
            k: number of required points to find.
        Output:
            Cents: K initial centroids, each of a dimension d.
        """

        num_of_samples = A.shape[0]  # =n
        num_of_channels = A.shape[1]  # =d
        #    weights = np.ones((num_of_samples, 1))
        #    normalization=np.dot(np.sqrt(weights),np.ones((1,A.shape[1]))) #normalizing the points in order that they will be on 1 unit sphere
        #    A1=np.divide(A,normalization)
        Cents = np.zeros((clus_num, num_of_channels))
        Cents[0, :] = A[int(np.floor(clus_num * np.random.rand(1, 1))),
                      :]  # choosing arbitrary point as the first
        for h1 in range(1, int(clus_num)):  # h1 points of k have been chosed by far
            P = np.zeros((num_of_samples,
                          h1))  # matrix that holds the distance of each point of A from each of the centers have already chosen
            Cent_inv = Cents[0:h1, :]
            inner = np.dot(A, np.transpose(
                Cent_inv))  # the inner products between each point of A from each of the centers have already chosen. gives the cosinus between them
            inner2 = np.power(inner, 2)
            inner2n = inner2 / np.max(inner2)
            P = 1 - np.power(inner2n, 2)  # that gives the sinus^2 between each centroid to each point.
            Pmin = np.zeros(num_of_samples)
            Pmin = P.min(1)  # taking the distance of the closest center to each point
            Fmin = np.cumsum(Pmin)
            Fmin = Fmin / Fmin[num_of_samples - 1]
            r = np.random.rand(1,
                               1)  # choosing a arbitrary r and the chosen row will be the one that the r is between its cumulative borders
            where_p = np.where(r < Fmin)  # finding all indeces of Fmin that are greater than r
            where_p1 = where_p[1]  # the slot index where r falls will be chosen
            Cents[h1, :] = A[where_p1[0], :]  # adding the new point to K
        return Cents

    def k_means_clustering(self, A, cum_weights, K, is_sparse, is_plspls, is_klinemeans):

        """
        This function:
            1.normalizes data points to a unit sphere,
            2.sends them to a weighted kmeans algorithm and
            3.calculates the error between the original data to the weighted centroids.

        inputs:
            A: data matrix, n points, eachof dimension d.
            K: number of centroids demanded for the Kmeans.

        output:
            error: The error between the original data to the weighted centroids.

    """
        is_jl = 1
        sensitivity = 0.95
        num_of_samples = A.shape[0]
        weights = np.ones((num_of_samples, 1))
        if is_klinemeans == 1:
            weights[:, 0] = np.sqrt(np.sum(np.power(A, 2), 1))  # each point norm is the weight

        normalization = np.dot(weights, np.ones(
            (1, A.shape[1])))  # normalizing the points in order that they will be on 1 unit sphere
        A1 = np.divide(A, normalization)

        num_of_samples = A1.shape[0]
        num_of_channels = A1.shape[1]
        K = int(K)
        if is_jl != 1:
            Ccol = num_of_channels
            AA1 = A1
        else:
            Ccol = int(np.ceil(np.log(num_of_samples)))
            JL = 2 * np.random.randn(num_of_channels, Ccol)
            AA1 = np.dot(A1, JL)
        P = np.zeros((num_of_samples, Ccol + 2))
        # C1=np.zeros((K,Ccol+2))

        P[:, 1] = np.sum(np.power(AA1, 2), 1)  # P defined just as in the algorithm you sent me
        P[:, 0] = 1
        P[:, 2:Ccol + 2] = AA1
        if is_plspls == 1:
            Cent = self.initial_k_lines(A1, K)
        else:
            per = np.random.permutation(num_of_samples)
            Cent = np.zeros((K, num_of_channels))
            # Cent[0:K,:]=A1[per[0:K],:]
            Cent[0:K, :] = A1[0:K, :]

        iter = 0
        Cost = 50  # should be just !=0
        old_Cost = 2 * Cost

        Tags = np.zeros((num_of_samples, 1))  # a vector stores the cluster of each point

        while np.logical_and(min(Cost / old_Cost, old_Cost / Cost) < sensitivity,
                             Cost > 0.000001):  # the corrent cost indeed resuces relating the previous one,
            if num_of_channels == 2:
                plt.figure()
                plt.title("Error Rate vs Coreset Size")
                plt.plot(A1[:, 0], A1[:, 1], 'b.', label="original points")
                if is_klinemeans == 0:
                    plt.plot(Cent[:, 0], Cent[:, 1], 'ro', label="kmeans")
                else:
                    for y in range(0, K):
                        plt.plot([0, Cent[y, 0]], [0, Cent[y, 1]], 'r', label="kmeans")
                plt.xlabel("X-axis")
                plt.ylabel("Y-axis")
                plt.show()  # however the loop continues until the reduction is not significantly and their ratio is close to one, and exceeds the parameter "sensitivity"
            group_weights = np.zeros((K, num_of_channels))
            if is_jl != 1:
                Cent1 = Cent
            else:
                Cent1 = np.dot(Cent, JL)
            C = np.zeros((Cent.shape[0], Ccol + 2))
            iter = iter + 1  # counting the iterations. only for control
            old_Cost = Cost  # the last calculated Cost becomes the old_Cost, and a new Cost is going to be calculated.
            C[:, 1] = 1  # C is defined just as in the algorithm you sent me.
            C[:, 0] = np.sum(np.power(Cent1, 2), 1)
            C[:, 2:Ccol + 2] = -2 * Cent1
            D = np.absolute(np.dot(P, np.transpose(
                C)))  # it turns out that we get here the euclidian distance squared between each centroid to each point, according to the Law of Cosines
            Tags = D.argmin(1)  # finding the most close centroid for each point
            Dmin = D.min(1)
            Cost = np.sum(Dmin)  # the cost is the summation of all of the minimal distances
            K = int(K)
            for kk in range(1, K + 1):
                wheres = np.where(Tags == kk - 1)  # finding the indeces of cluster k
                weights2 = weights[wheres[0]] ** 2  # finding the weights of cluster k
                m1 = np.dot(weights2,
                            np.ones((1, Cent.shape[1])))  # generating a matrix of k weights duplicated d times.
                m2 = np.multiply(m1, A1[wheres[0], :])  # multiplying each centroid with its group weight
                mone = np.sum(m2, 0)  # summing the weighted points of the cluster
                mechane = np.full_like(np.ones(Cent.shape[1]), np.sum(weights2),
                                       dtype=np.double)  # summing the weights of the cluster
                group_weights[kk - 1, :] = mechane
                if len(weights2) > 0:
                    Cent[kk - 1, :] = np.divide(mone, mechane)
        new_weights = np.zeros(K)
        for g in range(0, K):
            new_weights[g] = np.sum(cum_weights[np.where(Tags == g)[0]])

        rad_Cents = np.zeros((K, 1))
        rad_Cents[:, 0] = np.sqrt(np.sum(Cent ** 2, 1))
        Cents = np.multiply(1 / rad_Cents, Cent)

        Tags1 = D.argmin(0)  # finding the most close point for each center of mass, opposited to Tags above!

        sqrtGW = np.sqrt(group_weights)
        GW1 = np.zeros((K, 1))
        GW1[:, 0] = np.power(sqrtGW[:, 0], 1)
        if is_sparse == 0:
            if is_klinemeans == 1:
                SA0 = np.multiply(GW1,
                                  Cents)  # We may weight each group with its overall weight in ordet to compare it to the original data.
            else:
                SA0 = np.multiply(GW1,
                                  Cent)  # We may weight each group with its overall weight in ordet to compare it to the original data.

        else:
            SA0 = np.multiply(GW1, A1[Tags1, :])

        return SA0, weights, GW1, Tags1, new_weights

    def Adiel_alg(self, A, size_of_coreset, k):

        """
        This function implements my algorithm. It finds minimal number of lines
        that represents the original data (under an allowed error) by a binaric search of the minimal appripriete number of clusters, and produce a CNW coreset on that representation.

        inputs:
            A: data matrix, n points, each of dimension d.
            k: an algorithm parameter which determines the normalization neededand the error given the coreset size.
            coreset_size: the maximal coreset size (number of lines inequal to zero) demanded for input.
        output:
            errork: the actual error between the original data and its representation in k-line means.
            errora the actual error between the representation in k-line means and the CNW coreset.
            timek: the duration it took to find the minimal appropriete number of clusters
            timea: the duration this CNW operation lasted 
        """
        cnw = 1
        added_error_parameter = 17
        errork = 0
        if cnw == 1:
            epsi = np.sqrt(k / size_of_coreset)
        else:
            epsi = 4 * np.sqrt(np.log(1 / delta)) / np.sqrt(size_of_coreset)
        num_of_samples = A.shape[0]
        cluster_diff_for_stop_searching = num_of_samples / 10  # this parameter has two uses:
        # 1. also if need (num_of_samples-cluster_diff_for_stop_searching) clusters we do not want to establish the clustering but use the competed algorithm on all of the data.
        # 2. in the binaric search we enlarge a lower bound and reduce the upper bound. if the difference between them is less than "cluster_diff_for_stop_searching" we stop the search and define the upper bound as the result.
        K = int(size_of_coreset)
        print('KKKK=', K)
        start = time.time()

        edge_cases_flag = 0  # a variable that point whether we faced one of the following edge cases:
        # checking the another edge case
        SA5, weights5, w5, ind5 = self.k_means_clustering(A, size_of_coreset, 1, 1, 1)
        error01 = self.calc_error(A, SA5, k)  # comparing with is_sparse==1

        # error0,error01,SA,SA0 = k_means_users(A,size_of_coreset)
        # print('SA0 1',SA0)
        # print('error0==',error0)
        # print('limit==',(added_error_parameter+3)*epsi)
        if error01 < (
                    added_error_parameter + 17) * epsi:  # the error is directly less than we demand for the demanded size of coreset. we should then output this and do not operate CNW at all.
            errora = 0
            # errora1=0

            timea = time.time() - start
            start = time.time()
            errork = error01
            # errork1=error01

            edge_cases_flag = 1
            suggested_num_of_clusters = size_of_coreset

        # checking the another edge case
        print('edge_cases_flag', edge_cases_flag)
        if edge_cases_flag == 0:
            SA4, weights4, w4, ind4 = self.k_means_clustering(A, K, 1, 1, 1)
            errorinf = self.calc_error(A, SA4, k)  # comparing with is_sparse==1

            # errorinf,errorinf1,AA,SA0 = k_means_users(A,num_of_samples-cluster_diff_for_stop_searching)
            # print('SA0 2',SA0)

            if errorinf > added_error_parameter * epsi:  # the error is directly greater than we demand also for all of the data. we should then output the ordinary result of CNW on all the data.
                if cnw == 1:
                    SA5, w5, ind5 = self.CNW(A, k, size_of_coreset)
                    # errora,errora1,timea,SA,SA0=CNW(Arn,A,k,num_of_samples)
                else:
                    SA5, w5, ind5 = self.Nonuniform_Mahuny(A, size_of_coreset)

                errora = self.calc_error(A, SA5)
                errork = 0
                # errork1=0

                edge_cases_flag = 1
                suggested_num_of_clusters = num_of_samples

        if edge_cases_flag == 0:  # if we don't face one of the edge cases, we operate a binaric search what is the minimal appropriete number of clusters
            max_good_K = size_of_coreset  # the lower bound for K in each iteration
            min_bad_K = num_of_samples  # the upper bound for K in each iteration
            K = np.ceil((max_good_K + min_bad_K) / 2)  # the initial guess is the average between these two bounds
            while max_good_K < min_bad_K - cluster_diff_for_stop_searching:
                SA4, weights4, w4, ind4 = self.k_means_clustering(A, K, 1, 1, 1)
                error = self.calc_error(A, SA4)
                if error <= added_error_parameter * epsi:  # if the error is less than we demanded be can reduce max_good_K to the value of K
                    min_bad_K = K - 1
                else:  # if the error is greater than we demanded be must increase min_bad_K to the value of K
                    max_good_K = K
                K = np.ceil((max_good_K + min_bad_K) / 2)
            SA4, weights4, w4, ind4 = self.k_means_clustering(A, K, 1, 1, 1)
            error = self.calc_error(A, SA4)

            # error,error1,AA,SA0 = k_means_users(A,min_bad_K)
            # print('SA0 3',SA0)

            suggested_num_of_clusters = min_bad_K
            # after finding the appropriete value of K (greater the demanded size of coreset) and the representative k-line-means, we need to operate of that CNW to get out demanded size of coreset.
            if cnw == 1:
                SA5, w5, ind5 = self.CNW(A, k, K)
                # errora,errora1,timea,SA,SA0=CNW(Arn,AA,k,size_of_coreset)
            else:
                SA5, w5, ind5 = self.Nonuniform_Mahuni(A, K)
                # errora,errora1,timea,SA,SA0=Nonuniform_Mahuni(AA,size_of_coreset)
                print('timea in mahuny', timea)
                # print('SA0 4',SA0)
                #    errora=calc_error(A,SA5)

            errork = error
            # errork1=error1

        # timek=time.time()-start
        return SA5, errork, suggested_num_of_clusters
