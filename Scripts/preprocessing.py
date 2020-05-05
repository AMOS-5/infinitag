import os
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import gensim
from gensim import corpora


class MyNLP:
    'using current directly to read all the text documents in the directory one by one'
    dir = "."

    def __init__(self, dir):

        self.dir = dir
        self.stop = set(stopwords.words('english'))  # other languages can be entertained later
        self.exclude = set(string.punctuation)
        self.lemma = WordNetLemmatizer()

    # Clean the text

    def cleantext(self, doc):

        stop_word_free = " ".join([i for i in doc.lower().split() if i not in self.stop])
        punct_free = ''.join(ch for ch in stop_word_free if ch not in self.exclude)
        cleaned_text = " ".join(self.lemma.lemmatize(word) for word in punct_free.split())

        return cleaned_text

    def lda(self):
        txts = {}  # will be storing our docs on runtime
        extensions = [".txt", ".html", ".pdf", ".pptx", ".docx"]
        file_list = os.listdir(self.dir)
        for file in file_list:
            if file.endswith(tuple(extensions)):
                path = os.path.join(self.dir, file)
                currentfile = file
                fil = open(path, 'r', encoding="utf-8")
                txts[currentfile] = fil.read()
                fil.close()
                print("File Name: " + currentfile)

                '''Creating Dictionary with Cleaned docs'''
                doc_clean = [self.cleantext(txts[currentfile]).split()]

                # term dictionary of our corpus, Every unique term will be assigned an index
                dictionary = corpora.Dictionary(doc_clean)

                ''' We can add this dictionary to our database later '''
                # List of documents (Corpus) converted into term matrix
                doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]


                #pickle.dump(corpus, open('corpus.pkl', 'wb'))
                #dictionary.save('dictionary.gensim')

                # object for LDA model
                Lda = gensim.models.ldamodel.LdaModel

                # Running and Training LDA model on the document term matrix.
                ldamodel = Lda(doc_term_matrix, num_topics=1, id2word=dictionary, passes=50)

                print(ldamodel.print_topics(num_topics=2, num_words=4))

        return ldamodel
