from __future__ import print_function
import os
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import pandas as pd
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")
stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()


def cleantext(doc):

    stop_word_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punct_free = ''.join(ch for ch in stop_word_free if ch not in exclude)
    cleaned_text = " ".join(lemma.lemmatize(word) for word in punct_free.split())

    return cleaned_text


def data_load(dir, unwanted):
    txts = {}
    overall =[]
    file_list = os.listdir(dir)
    #print('fl',file_list)
    for file in file_list:

        path = os.path.join(dir, file)
        #print('path',path)
        file_open = open(path, 'r', encoding="latin")
        txts[file] = file_open.read()
        file_open.close()
        '''Creating Dictionary with Cleaned docs'''
        doc_clean = [cleantext(txts[file]).split()]

        for i in doc_clean:
            new_items = [item for item in i if not item.isdigit()]
            new_list = [test for test in new_items if (len(test)>3)]
            new_lists = [items for items in new_list if items not in unwanted]
            overall.append([new_lists])

    flattened = [val for sublist in overall for val in sublist]
    vocab_frame = pd.DataFrame({'words': flattened})
    print('there are ' + str(vocab_frame.shape[0]) + ' items in vocab_frame')

    return flattened, vocab_frame, file_list
