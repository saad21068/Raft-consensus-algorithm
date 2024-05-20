import numpy as np
from numpy.linalg import norm


class Kmeans:
    '''Implementing Kmeans algorithm.'''

    def __init__(self, n_clusters, max_iter=100, random_state=123):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.random_state = random_state

    def initializ_centroids(self, X):
        np.random.RandomState(self.random_state)
        random_idx = np.random.permutation(X.shape[0])
        centroids = X[random_idx[:self.n_clusters]]
        print(centroids)
        return centroids

    def compute_centroids(self, X, labels):
        centroids = np.zeros((self.n_clusters, X.shape[1]))
        for k in range(self.n_clusters):
            centroids[k, :] = np.mean(X[labels == k, :], axis=0)
        return centroids

    def compute_distance(self, X, centroids):
        distance = np.zeros((X.shape[0], self.n_clusters))
        for k in range(self.n_clusters):
            row_norm = norm(X - centroids[k, :], axis=1)
            print(row_norm,"@#!@")
            distance[:, k] = np.square(row_norm)
        return distance

    def find_closest_cluster(self, distance):
        return np.argmin(distance, axis=1)

    def compute_sse(self, X, labels, centroids):
        print("dafdsfasdfsd")
        distance = np.zeros(X.shape[0])
        for k in range(self.n_clusters):
            distance[labels == k] = norm(X[labels == k] - centroids[k], axis=1)
        return np.sum(np.square(distance))

    def fit(self, X):
        self.centroids = self.initializ_centroids(X)
        for i in range(self.max_iter):
            old_centroids = self.centroids
            print(old_centroids)
            distance = self.compute_distance(X, old_centroids)
            # print("DASfasdfasd")
            print(i)
            print(distance)
            self.labels = self.find_closest_cluster(distance)

            print(self.labels)
            self.centroids = self.compute_centroids(X, self.labels)
            if np.all(old_centroids == self.centroids):
                print(old_centroids)
                print(self.centroids)
                break
        self.error = self.compute_sse(X, self.labels, self.centroids)

    def predict(self, X):
        distance = self.compute_distance(X, self.centroids)
        return self.find_closest_cluster(distance)

import numpy as np

# Provided dataset
data = np.array([
    [0.4, 7.2], [0.8, 9.8], [-1.5, 7.3], [8.1, 3.4], [7.3, 2.3],
    [9.1, 3.1], [8.9, 0.2], [11.5, -1.9], [10.2, 0.5], [9.8, 1.2],
    [8.5, 2.7], [10.3, -0.3], [9.7, 0.8], [8.3, 2.9], [0.0, 7.1],
    [0.9, 9.6], [-1.6, 7.4], [0.3, 7.2], [0.7, 9.9], [-1.7, 7.5],
    [0.5, 7.4], [0.9, 9.7], [-1.8, 7.6], [11.1, -1.5], [10.8, -0.6],
    [9.5, 1.5], [8.7, 2.4], [11.2, -1.2], [10.5, -0.1], [9.3, 1.9],
    [8.6, 2.6]
])
kmeans = Kmeans(n_clusters=2)

kmeans.fit(data)

cluster_labels = kmeans.labels



