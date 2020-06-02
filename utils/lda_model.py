import os
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import gensim
from gensim import corpora


def lda(flattened, num_topics,num_words ):
    # term dictionary of our corpus, Every unique term will be assigned an index
    dictionary = corpora.Dictionary(flattened)

    ''' We can add this dictionary to our database later '''
    # List of documents (Corpus) converted into term matrix
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in flattened]

    # pickle.dump(corpus, open('corpus.pkl', 'wb'))
    # dictionary.save('dictionary.gensim')

    # object for LDA model
    Lda = gensim.models.ldamodel.LdaModel

    # Running and Training LDA model on the document term matrix.
    ldamodel = Lda(doc_term_matrix, num_topics, id2word=dictionary, passes=50)

    print(ldamodel.print_topics(num_topics, num_words))

    return ldamodel
