from __future__  import  print_function
import pandas as pd
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")
from sklearn.cluster import KMeans


def kmeans_clustering(tfidf_matrix,flattened,terms, file_list, num_clusters ):

    km = KMeans(n_clusters=num_clusters)

    km.fit(tfidf_matrix)

    clusters = km.labels_.tolist()
    print(len(clusters))
    document = { 'title': file_list, 'synopsis': flattened, 'cluster': clusters}

    frame = pd.DataFrame(document, index = [clusters] , columns = ['title', 'cluster'])
    frame['cluster'].value_counts()

    print("Top terms per cluster:")
    print()
    #sort cluster centers by proximity to centroid
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    for clustering in range(num_clusters):
        print("Cluster %d words:" % clustering, end='')
        print('')

        for tags in order_centroids[clustering, :5]: #replace 6 with n words per cluster
            kmeans_tags = terms[tags]
            print(' %s' % kmeans_tags  )
        print('')
        print('')
        print("Cluster %d titles:" % clustering, end='')

        for title in frame.ix[clustering]['title'].values.tolist():
            print(' %s,' % title, end='')
        print('')
        print('')
