from __future__ import print_function
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
stemmer = SnowballStemmer("english")

def dummy_fun(doc):
    #Due to some error in a function 'tfid vectorizer'
    return doc


def tfidf_vector(flattened):
    tfidf_vectorizer = TfidfVectorizer(max_df=0.8, min_df=0.2,max_features=200000, stop_words='english',
                             use_idf=True,tokenizer=dummy_fun, preprocessor=dummy_fun,ngram_range=(1,3))

    tfidf_matrix = tfidf_vectorizer.fit_transform(flattened) #fit the vectorizer to synopses

    print(tfidf_matrix.shape)
    terms = tfidf_vectorizer.get_feature_names()
    dist = 1 - cosine_similarity(tfidf_matrix)
    return dist, tfidf_matrix, terms
