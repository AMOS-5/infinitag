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
