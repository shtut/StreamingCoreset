import numpy as np
import time as time
from numpy.linalg import inv

# these are functions that operates weighted kmeans
def cluster_points(X, mu):
    bestmukey=np.zeros((X.shape[0],1))
    j=0
    for x in X:
        bestmukey1 = min([(i[0], np.linalg.norm(x-mu[i[0]])) \
                    for i in enumerate(mu)], key=lambda t:t[1])[0]
        j=j+1
        bestmukey[j-1]= bestmukey1
    return bestmukey

def reevaluate_centers(mu, weights, bestmukey, X):
    newmu =np.zeros((mu.shape))
    mone =np.zeros((mu.shape[0],mu.shape[1]))
    mechane =np.zeros((mu.shape[0],mu.shape[1]))
    newmu=[]

    for k in range (1,mu.shape[0]+1):
        wheres=np.where(bestmukey==k-1)
        weights2=weights[wheres[0]]

        mone[k-1,:]=np.sum(np.multiply(np.dot(weights2,np.ones((1,mu.shape[1]))),X[wheres[0],:]),0)
        mechane[k-1,:]=np.full_like(np.ones(mu.shape[1]), 1/np.sum(weights2), dtype=np.double)

    newmu=np.multiply(mone,mechane)
    return newmu

def find_centers(X, weigths, K):
    mu = X[0:K-1,:]
    old_bestmukey=np.zeros((X.shape[0],1))
    bestmukey = cluster_points(X, mu)
    diffC=bestmukey-old_bestmukey
    while not sum(diffC==np.zeros((diffC.shape[0],1)))==diffC.shape[0]:
        oldmu = mu
        old_bestmukey=bestmukey
        bestmukey = cluster_points(X, mu)
        diffC=bestmukey-old_bestmukey
        mu = reevaluate_centers(oldmu, weigths, bestmukey, X)
    return(mu, bestmukey)  #mu is the centroids, bestmukey is an indexing for each row to which cluser it belongs



# this funtion gets the data A and produce the coreset SA

def k_means_users(A, size_of_coreset):
    num_of_samples = A.shape[0]
    num_of_channels = A.shape[1]
    weights = np.ones((num_of_samples, 1))
    weights[:,0] = np.sqrt(np.sum(np.power(A, 2), 1))
    normalization=np.dot(weights,np.ones((1,A.shape[1])))
    A1=np.divide(A,normalization)
    K = size_of_coreset+1
    start = time.time()
    centroids,bestmukey=find_centers(A1, weights, K)
    centroids1=centroids[0:K-1,:]
    sizes = np.zeros((len(centroids1), 1))
    weights_s = np.zeros((len(centroids1), 1))

    for h1 in range(1, K):

        sizes[h1-1] = sum(bestmukey==h1-1) #I want here to count how many membersare in cluster h1.
        weights_s[h1-1] = (sum(np.power(weights[np.where(bestmukey==h1-1)],2)))
    wei_sizes=np.dot(np.sqrt(weights_s),np.ones((1, num_of_channels)))

    SA=np.multiply(wei_sizes,centroids1)
    return SA

class LineKMeans:
    def __init__(self, p, w):
        self._points = p
        self._wights = w

    @staticmethod
    def coreset_alg(p, w, num1, num2):
        return LineKMeans(p, w)

    def sample(self, coreset_size):
        if(len(self._points) > coreset_size):
            result = k_means_users(A, coreset_size)
        else:
            result = self._pointss
        return result, np.ones((coreset_size, 1))


#MAIN


third_meas=1
num_of_samples=10
num_of_channels=3
A = np.random.rand(num_of_samples,num_of_channels) #the original data
size_of_coreset=2
SA=k_means_users(A, size_of_coreset)
At=np.transpose(A)
AtA=np.dot(At,A)
SAt=np.transpose(SA)
SAtSA=np.dot(SAt,SA)
print(np.linalg.norm(SAtSA-AtA,2)/np.linalg.norm(AtA,2)) #calculating the error




