from __future__  import  print_function
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")
from utils.data_preprocessing import data_load
from utils.tfidf_vector import tfidf_vector
from utils.k_means_cluster import kmeans_clustering
from utils.lda_model import lda

if __name__ == "__main__":

    directory = r"E:\utils\training.sets.released\2"
    unwanted = {'patient','order','showed','exam', 'number','home','left', 'right', 'history','daily','instruction', 'interaction', 'fooddrug', 'time','override', 'unit','potentially', 'march', 'added'}
    ####
    # clustering_type = Mention the type of clustering here
    # 'k-means' : Mention the number of cluster in num_clusters_kmeans
    # 'lda' : Mention the num_words and num_topics if using lda
    # 'hierarchical' : to be implemented
    ####
    clustering_type = 'hierarchical'
    num_clusters_kmeans = 8

    num_words = 4
    num_topics = 5

    flattened, vocab_frame, file_list = data_load(directory, unwanted)
    dist, tfidf_matrix, terms = tfidf_vector(flattened)
    if clustering_type == 'k-means':
        clustering = kmeans_clustering(tfidf_matrix, flattened,terms,  file_list, num_clusters_kmeans)
    elif clustering_type == 'lda':
        clustering = lda(flattened, num_topics, num_words)
    elif clustering_type == 'hierarchical':
        print('Not Implemented')
