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
from utils.data_preprocessing import data_load
from utils.tfidf_vector import tfidf_vector
from utils.k_means_cluster import kmeans_clustering
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



    directory = r'E:\clustering\t5_testdata'
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

    # Data loading process : Using pickle to save time while running experiments
    data_files = r'..\utils\data_files.p'
    pickle_data_files = Path(data_files)

    if pickle_data_files.is_file():
        print('')
        print('Pickle files for data_load are AVAILABLE')
        with open(data_files, "rb") as fp:
            print('Data File available and loading..')  # Unpickling
            flattened, vocab_frame, file_list, overall = pickle.load(fp)

    else:
        print('')
        print('Pickle files for data_load are NOT AVAILABLE')
        flattened, vocab_frame, file_list, overall = data_load(directory,
                                                               unwanted_keywords,
                                                               extensions_allowed)
        pickle.dump([flattened, vocab_frame, file_list, overall],
                    open("data_files.p", "wb"))

    # TFIDF process : Using pickle to save time while running experiments. Computation time is high during training
    distance_files = r'..\utils\distance.p'
    pickle_distance_files = Path(distance_files)

    if pickle_distance_files.is_file():
        print('')
        print('Pickle files for distances are AVAILABLE')
        with open(distance_files, "rb") as fp:
            print('Distance file available and loading..')  # Unpickling
            dist, tfidf_matrix, terms = pickle.load(fp)

    else:
        print('')
        print('Pickle files for distances are NOT AVAILABLE')
        dist, tfidf_matrix, terms = tfidf_vector(flattened)
        pickle.dump([dist, tfidf_matrix, terms], open("distance.p", "wb"))

    if clustering_type == 'k-means':
        clustering = kmeans_clustering(tfidf_matrix, flattened, terms,
                                       file_list, num_clusters_kmeans,
                                       words_per_cluster)
    elif clustering_type == 'lda':
        clustering = lda(flattened, num_topics, num_words)
    elif clustering_type == 'hierarchical':
        clustering = hierarchical_cluster(dist, terms, file_list)
