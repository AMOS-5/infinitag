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
from backend.autotagging.data_preprocessing import load_data
from backend.autotagging.tfidf_vector import tfidf_vector
from backend.autotagging.k_means_cluster import kmeans_clustering, silhoutte_method, optimal_clusters_elbowMethod
from backend.autotagging.lda_model import lda
from backend.autotagging.hierarchichal_clustering import hierarchical_cluster
import pickle
from pathlib import Path
import warnings
import time
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
    clustering_type = 'kmeans'
    mini_batch = True # Values : Bool . True runs MiniBatch. K means False runs Kmeans
    optimal_k_method = 'silhoutte' ## Values :  'silhoutte' , 'elbow'
    words_per_cluster = 5
    # Change number of words and number of topics below for LDA model
    num_words = 5
    num_topics = 10


    flattened, vocab_frame, file_list, overall = load_data(directory, unwanted_keywords)
    number_of_files = len(file_list)
    dist, tfidf_matrix, terms = tfidf_vector(flattened)



    if clustering_type == 'kmeans' and optimal_k_method == 'elbow' :

        start = time.time()
        num_clusters_kmeans = optimal_clusters_elbowMethod(tfidf_matrix,
                                                           number_of_files,
                                                           mini_batch=mini_batch)
        print('Number of Files Selected : ', number_of_files)
        clustering = kmeans_clustering(tfidf_matrix, flattened, terms,
                                       file_list, num_clusters_kmeans,
                                       words_per_cluster, mini_batch=mini_batch)
        print('Execution Time Elbow Method and Mini Batch is ' + str(
            mini_batch) + ': ', time.time() - start)

    elif clustering_type == 'kmeans' and optimal_k_method == 'silhoutte' :
        start = time.time()
        num_clusters_kmeans = silhoutte_method(tfidf_matrix, number_of_files, mini_batch= mini_batch)
        print('Number of Files Selected : ',number_of_files)
        clustering = kmeans_clustering(tfidf_matrix, flattened, terms,
                                      file_list, num_clusters_kmeans,
                                      words_per_cluster,mini_batch=mini_batch)

    elif clustering_type == 'lda':
        clustering = lda(flattened, num_topics, num_words)
    elif clustering_type == 'hierarchical':
        clustering = hierarchical_cluster(dist, terms, file_list)
