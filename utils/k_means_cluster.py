# InfiniTag Copyright © 2020 AMOS-5
# Permission is hereby granted,
# free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions: The above copyright notice and this
# permission notice shall be included in all copies or substantial portions
# of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
# NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__  import  print_function
import time
import pandas as pd
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")
from sklearn.cluster import KMeans, MiniBatchKMeans
import joblib
import matplotlib.pyplot as plt
from kneed import KneeLocator
import time
from sklearn.metrics import silhouette_score
<<<<<<< HEAD
=======

def optimal_clusters_elbowMethod(tfidf_matrix,nselectedfiles):

    startime= time.time()
    cluster_error = []
    K = range(1, nselectedfiles)
    for k in K:
        print(k)
        kmeanModel = KMeans(n_clusters=k)
        kmeanModel.fit(tfidf_matrix)
        cluster_error.append(kmeanModel.inertia_)

    clusters_df = pd.DataFrame({"num_clusters": K, "cluster_error": cluster_error})
    print(clusters_df)

    # Plot the elbow Plot
    plt.figure(figsize=(12, 6))
    plt.plot(clusters_df.num_clusters, clusters_df.cluster_error, marker="o")
    plt.xlabel('k')
    plt.ylabel('Clusters_Error')
    plt.title('The Elbow Method showing the optimal k')
    plt.show()
    plt.savefig('Elbow.png')

    x = range(1, len(cluster_error) + 1)


    kn = KneeLocator(x, cluster_error, curve='convex', direction='decreasing')
    nclust= kn.knee
    print("\n\nOptimal no. of clusters : ",nclust)

    plt.xlabel('number of clusters k')
    plt.ylabel('Sum of squared distances')
    plt.plot(x, cluster_error, 'bx-')
    plt.vlines(kn.knee, plt.ylim()[0], plt.ylim()[1], linestyles='dashed')
    plt.show()
    plt.savefig('Knee.png')

>>>>>>> research on optimal clusters

def optimal_clusters_elbowMethod(tfidf_matrix,number_of_files, mini_batch = True):

    cluster_error = []
    K = range(1, number_of_files)
    for k in K:
        print(k)
        if mini_batch:
            kmeanModel = MiniBatchKMeans(n_clusters=k, init='k-means++', n_init=2, init_size=1000)
        else:
            kmeanModel = KMeans(n_clusters=k)
        kmeanModel.fit(tfidf_matrix)
        cluster_error.append(kmeanModel.inertia_)
    clusters_df = pd.DataFrame({"num_clusters": K, "cluster_error": cluster_error})
    print(clusters_df)

    # Plot the elbow Plot
    plt.figure(figsize=(12, 6))
    plt.xlabel('k')
    plt.ylabel('Clusters_Error')
    plt.title('The Elbow Method showing the optimal k')
    plt.plot(clusters_df.num_clusters, clusters_df.cluster_error, marker="o")
    print('Saving the elbow image')
    plt.savefig('Elbow.png')

    # Obtain the optimal 'k' with knee locator
    x = range(1, len(cluster_error) + 1)
    kn = KneeLocator(x, cluster_error, curve='convex', direction='decreasing')
    nclust= kn.knee
    print("\n\nOptimal no. of clusters : ",nclust)
    plt.xlabel('number of clusters k')
    plt.ylabel('Sum of squared distances')
    plt.plot(x, cluster_error, 'bx-')
    plt.vlines(kn.knee, plt.ylim()[0], plt.ylim()[1], linestyles='dashed')
    print('Saving the knee image')
    plt.savefig('Knee.png')
    return nclust


def silhoutteMethod(tfidfmatrix, number_of_files, mini_batch=True):

    range_n_clusters = range(2, number_of_files-1)# clusters range you want to select
    best_clusters = 0  # best cluster number which you will get
    previous_silh_avg = 0.0

    for n_clusters in range_n_clusters:
        if mini_batch:
            clusterer = MiniBatchKMeans(n_clusters=n_clusters, init='k-means++', n_init=2, init_size=1000)
        else:
            clusterer = KMeans(n_clusters=n_clusters)
        cluster_labels = clusterer.fit_predict(tfidfmatrix)
        silhouette_avg = silhouette_score(tfidfmatrix, cluster_labels)
        print("silhoutte avg:",silhouette_avg)
        if silhouette_avg > previous_silh_avg:
            previous_silh_avg = silhouette_avg
            best_clusters = n_clusters
        end = time.time()
    print("best clusters:",best_clusters)
    return best_clusters

    return nclust


def silhoutteMethod(tfidfmatrix,nselected):

    range_n_clusters = range(2, nselected-1)# clusters range you want to select
    #dataToFit = [[12, 23], [112, 46], [45, 23]]  # sample data
    best_clusters = 0  # best cluster number which you will get
    previous_silh_avg = 0.0

    for n_clusters in range_n_clusters:
        clusterer = KMeans(n_clusters=n_clusters)
        cluster_labels = clusterer.fit_predict(tfidfmatrix)
        silhouette_avg = silhouette_score(tfidfmatrix, cluster_labels)
        print("silhoutte avg:",silhouette_avg)
        if silhouette_avg > previous_silh_avg:
            previous_silh_avg = silhouette_avg
            best_clusters = n_clusters

    print("best clusters:",best_clusters)
    return best_clusters

def kmeans_clustering(tfidf_matrix,
                      flattened,
                      terms,
                      file_list,
                      num_clusters,
                      words_per_cluster,
                      job=None,
                      mini_batch=True):

    ### Check the optimal clsuetrs here
<<<<<<< HEAD
    if mini_batch:
        print('Mini Batch K Means')
        km = MiniBatchKMeans(n_clusters=num_clusters, init='k-means++', n_init=2, init_size=1000)
    else:
        print('K Means')
        km = KMeans(n_clusters=num_clusters)
=======

    km = KMeans(n_clusters=num_clusters)
>>>>>>> research on optimal clusters

    km.fit(tfidf_matrix)
    joblib.dump(km, 'kmeans_model.pkl')
    clusters = km.labels_.tolist()
    document = {'title': file_list, 'synopsis': flattened, 'cluster': clusters}

    frame = pd.DataFrame(document, index=[clusters], columns=['title', 'cluster'])
    frame['cluster'].value_counts()

    # sort cluster centers by proximity to centroid
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    keywords_dict = {}

    if job is not None:
        job.status = 'TAGGING_JOB.START_SORT'
    progress_step = 0
    start_time = time.time()
    time_index = 0
    iteration_time = None
    idx = 0
    if job is not None:
        job.status = 'TAGGING_JOB.APPLYING_CLUSTERS'

    for clustering in range(num_clusters):
        if idx == 0:
            progress_step = 50 / num_clusters

        keywords = []
        for tags in order_centroids[clustering, : words_per_cluster]:  # replace 6 with n words per cluster
            kmeans_tags = terms[tags]
            keywords.append(kmeans_tags)
        docname = []
        for title in frame.loc[clustering]['title'].values.tolist():
            docname.append(title)


        for filename in docname:
            keywords_dict[filename] = keywords

        if time_index == 0:
            end_time = time.time()
            iteration_time = end_time - start_time
            time_index = 1

        remaining_iterations = num_clusters - idx
        idx += 1
        if iteration_time != - 1:
            if job is not None:
                job.time_remaining = iteration_time * remaining_iterations
        if job is not None:
            job.progress += progress_step
    print('keywords_dict : ',keywords_dict)
    return keywords_dict
<<<<<<< HEAD
=======

>>>>>>> research on optimal clusters
