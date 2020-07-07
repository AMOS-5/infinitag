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

from utils.tfidf_vector import tfidf_vector, tfidf_vector_keywords
from utils.k_means_cluster import kmeans_clustering, silhoutteMethod

from nltk.corpus import stopwords, wordnet
from nltk.stem.wordnet import WordNetLemmatizer
import langdetect
import spacy

import os
import io
import string
import pandas as pd
import threading as th

# TODO tika should be configure correctly to ignore images and other unnecessary data
os.environ["TIKA_PATH"] = "./downloads/tika"
print(f"Tika server set to: {os.environ['TIKA_PATH']}")

from tika import parser, detector, language
from typing import Set, List, Tuple


class Punctuation(set):
    def __init__(self):
        self.update(string.punctuation)
        self.add('"')
        self.add("“")
        self.add("„")
        self.add("”")


punctuation = Punctuation()


class EnglishLemmatizer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def lemmatize(self, word: str) -> str:
        return self.lemmatizer.lemmatize(word)


class GermanLemmatizer:
    def __init__(self):
        self.lemmatizers = spacy.load("de_core_news_sm")

    def lemmatize(self, word: str) -> str:
        token = self.lemmatizers.tokenizer(word)
        lemma = next(token.__iter__()).lemma_
        return lemma

class LemmatizerFactory:
    lemmatizers = {
        "en": EnglishLemmatizer,
        "de": GermanLemmatizer,
    }

    @staticmethod
    def get(lang: str) -> "ConcreteLemmatizer":
        if lang not in LemmatizerFactory.lemmatizers:
            print(f"No Lemmatizer can be found for language: '{lang}'")
            print("Default english lemmatizer will be used.")
            return EnglishLemmatizer()

        return LemmatizerFactory.lemmatizers[lang]()


class EnglishStopwords(set):
    def __init__(self):
        self.update(stopwords.words("english"))


class GermanStopwords(set):
    def __init__(self):
        self.update(stopwords.words("german"))


class StopwordFactory:
    stopwords = {
        "en": EnglishStopwords,
        "de": GermanStopwords,
    }

    @staticmethod
    def get(lang: str) -> "ConcreteStopwords":
        if lang not in StopwordFactory.stopwords:
            print(f"No Stopwords for language: '{lang}'")
            print("Default english stopwords will be used.")
            return StopwordFactory.stopwords["en"]()

        return StopwordFactory.stopwords[lang]()


ALLOWED_EXTENSIONS = {
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".ods",
    ".odp",
    ".pdf",
    ".eml",
    ".xml",
    ".html",
    ".txt",
    ".text",
    ".test",  # for testing purposes appears in test_* sometimes
}

UNWANTED_KEYWORDS = {
    "patient",
    "order",
    "showed",
    "exam",
    "number",
    "home",
    "left",
    "right",
    "history",
    "daily",
    "instruction",
    "interaction",
    "fooddrug",
    "time",
    "override",
    "unit",
    "potentially",
    "march",
    "added",
    "intro",
    "open",
    "exit",
    "intro",
    "stop",
    "comment",
    "intro",
    "open",
    "exit",
}

def lemmatize_keywords(keywords: dict) -> dict:
    keywords = [kw for kw in keywords.keys()]
    text = " ".join(kw for kw in keywords)

    try:
        lang = langdetect.detect(text)
    except:
        return keywords

    lemmatizer = LemmatizerFactory.get(lang)

    lemmatized_keywords = [lemmatizer.lemmatize(kw).lower() for kw in keywords]
    return lemmatized_keywords


def create_automated_keywords(docs: dict, num_clusters: int, num_keywords: int, default: bool, job=None) -> dict:
    flattened, vocab_frame, file_list, overall = load_data_from_frontend(docs)
    number_of_files = len(file_list)
    if len(docs) < 5:
        keywords = tfidf_vector_keywords(file_list, flattened, num_keywords)
    else:
        dist, tfidf_matrix, terms = tfidf_vector(flattened)

        if default:
            num_clusters_kmeans = silhoutteMethod(tfidf_matrix, number_of_files, mini_batch=True)
        else:
            num_clusters_kmeans = num_clusters

        keywords = kmeans_clustering(tfidf_matrix,
                          flattened,
                          terms,
                          file_list,
                          num_clusters_kmeans,
                          num_keywords,
                          mini_batch=True,
                          job = None)

    return keywords


def load_data(dir: str, unwanted_keywords: Set[str]):
    files = get_all_files(dir)

    vocabulary = []
    overall = []
    for file in files:

        meta, content = get_clean_content(file)
        if content is not None:
            vocabulary.append(content)

        # TODO why append the content as a list, when it itself is already a
        # list? is it rly okay that the content is None?
        overall.append([content])

    vocabulary_frame = pd.DataFrame({"words": vocabulary})

    return vocabulary, vocabulary_frame, files, overall


def load_data_from_frontend(docs: dict):
    filenames = [doc["id"] for doc in docs]
    texts = [doc["content"] for doc in docs]
    langs = [doc["language"] for doc in docs]
    lang = 0
    for i in langs:
        lang = i

    overall = [clean(text, lang) for text in texts]
    vocabulary = []

    vocabulary.extend(content for content in overall)

    vocab_frame = pd.DataFrame({"words": vocabulary})


    return vocabulary, vocab_frame, filenames, overall


nltk_load_lock = th.Lock()


def get_clean_content(file: str):
    # https://stackoverflow.com/questions/27433370/what-would-cause-wordnetcorpusreader-to-have-no-attribute-lazycorpusloader
    # not the best fix but it works
    nltk_load_lock.acquire()
    wordnet.ensure_loaded()
    nltk_load_lock.release()

    meta, content = extract(file)

    if content is not None:
        lang = meta["language"]
        content = clean(content, lang)

    return meta, content


def clean(content: str, lang: str) -> List[str]:
    content = clean_text(content, lang)
    content = clean_digits(content)
    content = clean_short_long_words(content)
    content = clean_unwanted_words(content)
    content = clean_alphanumericals(content)

    return content


def clean_text(content: str, lang: str) -> List[str]:
    content = "".join(ch for ch in content if ch not in punctuation)

    content = content.split()

    stopwords = StopwordFactory.get(lang)
    content = [word for word in content if word not in stopwords]

    lemmatizer = LemmatizerFactory.get(lang)
    content = [lemmatizer.lemmatize(word) for word in content]

    content = [word.lower() for word in content]

    return content

def clean_digits(content: List[str]) -> List[str]:
    return [word for word in content if not word.isdigit()]


def clean_short_long_words(content: List[str]) -> List[str]:
    return [word for word in content if len(word) > 3 and len(word)<12]


def clean_unwanted_words(content: List[str]) -> List[str]:
    return [word for word in content if word not in UNWANTED_KEYWORDS]

def clean_alphanumericals(content: List[str]) -> List[str]:
    return [word for word in content if word.isalpha()]


def get_all_files(dir: str) -> List[str]:
    datafiles = []
    for path, directories, files in os.walk(dir):
        datafiles.extend(os.path.join(path, file) for file in files)

    return datafiles


def extract(path: str) -> Tuple[dict, str]:
    file_extension = os.path.splitext(path)[-1]
    # TODO not really sure whether this should tika recognizes most formats
    if file_extension not in ALLOWED_EXTENSIONS:
        print(f"File extension not allowed for: {path}")
        return None, None

    data = parser.from_file(path, requestOptions={"timeout": 10000})
    if data is None:
        return None, None

    meta, content = data["metadata"], data["content"]
    meta["stream_size"] = os.path.getsize(path)

    if content is not None:
        try:
            meta["language"] = langdetect.detect(content)
        except:
            pass

    return meta, content

