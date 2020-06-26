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
import pandas as pd
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")
from sklearn.cluster import KMeans
import joblib


def kmeans_clustering(tfidf_matrix,flattened,terms, file_list, num_clusters,words_per_cluster ):
    km = KMeans(n_clusters=num_clusters)

    # pickle.dump(km, open("kmeans_model.pkl", "wb"))
    km.fit(tfidf_matrix)
    joblib.dump(km, 'kmeans_model.pkl')
    clusters = km.labels_.tolist()
    print(len(clusters))
    document = {'title': file_list, 'synopsis': flattened, 'cluster': clusters}

    frame = pd.DataFrame(document, index=[clusters], columns=['title', 'cluster'])
    frame['cluster'].value_counts()

    print("Top terms per cluster:")
    print()
    # sort cluster centers by proximity to centroid
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    keywords_dict = {}
    for clustering in range(num_clusters):
        print("Cluster %d words:" % clustering, end='')
        print('')
        keywords = []
        for tags in order_centroids[clustering, : words_per_cluster]:  # replace 6 with n words per cluster
            kmeans_tags = terms[tags]
            keywords.append(kmeans_tags)
            print(' %s' % kmeans_tags)
        print('')
        print('')
        print("Cluster %d titles:" % clustering, end='')
        docname = []
        for title in frame.loc[clustering]['title'].values.tolist():
            docname.append(title)

            print(' %s,' % title, end='')
        #checking[clustering]=(keywords, docname)
        for filename in docname:
            keywords_dict[filename]=keywords
            print('')
            print('')

    return keywords_dict


## Elbow method to determine the ideal amount of cluster
"""" cluster_error = []
    K = range(1,50)
    for k in K:
        kmeanModel = KMeans(n_clusters=k)
        kmeanModel.fit(tfidf_matrix)
        cluster_error.append( kmeanModel.inertia_ )

    clusters_df = pd.DataFrame( { "num_clusters":K, "cluster_error": cluster_error } )
    print(clusters_df)

    # Plot the elbow Plot
    plt.figure(figsize=(12,6))
    plt.plot( clusters_df.num_clusters, clusters_df.cluster_error, marker = "o" )
    plt.xlabel('k')
    plt.ylabel('Clusters_Error')
    plt.title('The Elbow Method showing the optimal k')
    plt.show()"""
