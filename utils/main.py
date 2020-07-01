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

from __future__ import print_function
from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer("english")
from utils.data_preprocessing import load_data
from utils.tfidf_vector import tfidf_vector
from utils.k_means_cluster import kmeans_clustering,silhoutteMethod
from utils.lda_model import lda
from utils.hierarchichal_clustering import hierarchical_cluster
import pickle
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# ## to do
# we might have a lot of unwanted keywords
# So we have to make it easy to store all unwanted keywords in a json file
# To DO : json file to create dictionary of keywords
# read the json to create dictionary again
# elbow method to determine the number of clusters
# refine the test.py to understand whether the model loading works


if __name__ == "__main__":

    directory = r'E:\Infinitag\tests\test_dataset'
    # directory =  r'E:\amos\utils\t5\dummy'
    unwanted_keywords = {'patient', 'order', 'showed', 'exam', 'number', 'home',
                         'left', 'right', 'history', 'daily', 'instruction',
                         'interaction', 'fooddrug', 'time', 'override', 'unit',
                         'potentially', 'march', 'added'}
    extensions_allowed = ['.txt', '.pdf', '.eml', '.docx', '.html', '.xml',
                          '.ods', '.doc', '.ppt', '.xls', '.text']
    ####
    # clustering_type = Mention the type of clustering here
    # 'k-means' : Mention the number of cluster in num_clusters_kmeans
    # 'lda' : Mention the num_words and num_topics if using lda
    # 'hierarchical' : to be implemented
    ####
    clustering_type = 'k-means'

    # Change number of words and number of topics below for LDA model
    num_words = 5
    num_topics = 10

    # Change hyperparameters below for customizing k-means clustering
    num_clusters_kmeans = 5
    words_per_cluster = 5

    flattened, vocab_frame, file_list, overall = load_data(directory, unwanted_keywords)
    print(flattened)


    count=0
    for words in flattened:
        count+=len(words)

    print(count)

    dist, tfidf_matrix, terms = tfidf_vector(flattened)

    print(tfidf_matrix.shape)

    if clustering_type == 'k-means':
        #nselectedfiles = len(file_list)
        #clustering = silhoutteMethod(tfidf_matrix,nselectedfiles)
        #clustering = optimal_clusters(tfidf_matrix,nselectedfiles)
        clustering = kmeans_clustering(tfidf_matrix, flattened, terms,
                                       file_list, num_clusters_kmeans,
                                       words_per_cluster)
    elif clustering_type == 'lda':
        clustering = lda(flattened, num_topics, num_words)
    elif clustering_type == 'hierarchical':
        clustering = hierarchical_cluster(dist, terms, file_list)
