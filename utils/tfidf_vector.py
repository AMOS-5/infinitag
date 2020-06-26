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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
stemmer = SnowballStemmer("english")

def dummy_fun(doc):
    #Due to some error in a function 'tfid vectorizer'
    return doc

def get_top_tf_idf_words(feature_names, response, top_n=2):
    # Sort the top n terms in the tfidf vectorizer
    sorted_nzs = np.argsort(response.data)[:-(top_n+1):-1]
    return feature_names[response.indices[sorted_nzs]]

def tfidf_vector(flattened):

    tfidf_vectorizer = TfidfVectorizer(max_features=200000, stop_words='english',
                             use_idf=True,tokenizer=dummy_fun, preprocessor=dummy_fun,ngram_range=(1,1))

    tfidf_matrix = tfidf_vectorizer.fit_transform(flattened)
    print(tfidf_matrix.shape)
    terms = tfidf_vectorizer.get_feature_names()
    dist = 1 - cosine_similarity(tfidf_matrix)
    return dist, tfidf_matrix, terms

def tfidf_vector_keywords(file_list, flattened, num_keywords):
    #this function is used to obtain keywords if num of files is less than 5 where kmeans cannot be used.
    keywords = []
    for flat in flattened:
        tfidf_vectorizer = TfidfVectorizer(max_features=200000, stop_words='english',
                                 use_idf=True,tokenizer=dummy_fun, preprocessor=dummy_fun,ngram_range=(1,1))

        tfidf_matrix = tfidf_vectorizer.fit_transform([flat])
        print(tfidf_matrix.shape)
        terms = tfidf_vectorizer.get_feature_names()
        keywords_tfidf = [get_top_tf_idf_words(np.array(terms),tfidf_matrix, num_keywords) for top_n_terms in tfidf_matrix]
        keywords_tfidf = keywords_tfidf.pop()
        keywords.append(keywords_tfidf)
    keywords = np.array(keywords).tolist()
    keywords_dict = {}
    count= 0
    for file in file_list:
        keywords_dict[file]=keywords[count]
        count += 1
    print('keywords_dict : ', keywords_dict)
    return keywords_dict
