# Import the pandas library.
import pandas
# Import matplotlib
import matplotlib.pyplot as plt
# Import the kmeans clustering model.
from sklearn.cluster import KMeans
# Import the PCA model.
from sklearn.decomposition import PCA

import numpy as np
from scipy.sparse import rand
from scipy.sparse import random
from scipy import stats


class CustomRandomState(object):

    @staticmethod
    def randint(k):

        i = np.random.randint(k)
        return i - i % 2


# Read in the data.
rs = CustomRandomState()
rvs = stats.poisson(25, loc=10).rvs
games = rand(100000, 10, density=0.01, format='csr') + random(100000 , 10, density=0.25, random_state=rs, data_rvs=rvs)
games.data[:] = 1
print(np.unique(games.todense().flat))

# Remove any rows without user reviews.
# games = games[games["users_rated"] > 0]
# Remove any rows with missing values.
# games = games.dropna(axis=0)

# Initialize the model with 2 parameters -- number of clusters and random state.
kmeans_model = KMeans(n_clusters=2, random_state=1)
# Get only the numeric columns from games.
# good_columns = games._get_numeric_data()
# Fit the model using the good columns.
kmeans_model.fit(games)
# Get the cluster assignments.
labels = kmeans_model.labels_

# Create a PCA model.
pca_2 = PCA(2)
# Fit the PCA model on the numeric columns from earlier.
plot_columns = pca_2.fit_transform(games.toarray())
# Make a scatter plot of each game, shaded according to cluster assignment.
plt.scatter(x=plot_columns[:,0], y=plot_columns[:,1], c=labels)
# Show the plot.
plt.show()


