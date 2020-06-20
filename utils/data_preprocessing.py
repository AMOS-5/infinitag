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
import os
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import pandas as pd
from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer("english")
stop = set(stopwords.words("english"))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()
from tika import parser, detector, language
import io
from pptx import Presentation

# TODO fix missing extensions
ALLOWED_EXTENSIONS = [
    '.txt',
    '.pdf',
    '.eml',
    '.docx',
    '.html',
    '.xml',
    '.ods',
    '.doc',
    '.ppt',
    '.pptx'
    '.xls',
    '.text'
]

UNWANTED_KEYWORDS = {
    'patient',
    'order',
    'showed',
    'exam',
    'number',
    'home',
    'left',
    'right',
    'history',
    'daily',
    'instruction',
    'interaction',
    'fooddrug',
    'time',
    'override',
    'unit',
    'potentially',
    'march',
    'added'
}



def load_data(dir: str, unwanted_keywords: Set[str])
    files = get_all_files(dir)

    vocabulary = []
    overall = []
    for file in files:
        meta, content = get_clean_content(file)

        if content is not None:
            vocabulary.extend(content)

        # TODO why append the content as a list, when it itself is already a
        # list? is it rly okay that the content is None?
        overall.append([content])

    vocabulary_frame = pd.DataFrame({"words": vocabulary})

    return vocabulary, vocabulary_frame, files, overall

def get_clean_content(file: str):
    meta, content = extract(file)

    if content is not None:
        content = clean(content)

    return meta, content


def clean(content: str) -> str:
    content = clean_text(content)
    content = clean_digits(content)
    content = clean_short_words(content)
    content = clean_unwanted_words(content)

    return content

def clean_text(content: str):
    stop_word_free = " ".join(i for i in doc.lower().split() if i not in stop)
    punct_free = "".join(ch for ch in stop_word_free if ch not in exclude)
    cleaned_text = " ".join(lemma.lemmatize(word) for word in punct_free.split())

    return cleaned_text


def clean_digits(content: List[str]) -> List[str]:
    return [word for word in content if not word.isdigit()]


def clean_short_words(content: List[str]) -> List[str]:
    return [word for word in content if len(word) > 3]


def clean_unwanted_words(content: List[str]) -> List[str]:
    return [word for word in content if word not in UNWANTED_KEYWORDS]


def get_all_files(dir: str) -> List[str]:
    files = []
    for path, directories, files in os.walk(dir):
        files.extend(os.path.join(path, file) for file in files)

    return files


def extract(path: str) -> Tuple[dict, str]:
    file_extension = os.path.splitext(path)[-1]
    if file_extension not in ALLOWED_EXTENSIONS:
        print(f"File extension not allowed for: {path}")
        return None, None

    data = parser.from_file(path, requestOptions={"timeout": 300})
    meta, content = data["metadata"], data["content"]

    # If PPT files are too large then the content is None.
    # As an alternative, we can use Presentation library to read PPT files for now
    if content is None and file_extension == ".pptx":
        content = _parse_big_ppt(path)

    return meta, content


def _extract_big_ppt(path: str) -> str:
    prs = Presentation(path)

    content = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                content.append(shape.text)

    return content


def data_load(dir, unwanted_keywords, extensions_allowed):

    # done: txt,pdf,email,pptx,docx, html,xml,ods
    filenames = []
    txts = {}
    overall = []

    for path, directories, files in os.walk(dir):
        for file in files:
            paths = os.path.join(path, file)
            extension = os.path.splitext(paths)[1]
            print("\n\nFile extension: " + extension)
            print("file type: " + detector.from_file(paths))
            print(file)
            filenames.append(file)

            file_data = parser.from_file(paths, requestOptions={"timeout": 300})
            text_meta = file_data["metadata"]
            texts = file_data["content"]

            if text_meta is None:
                print("File meta-data not recognized")  # by apache tika

            if extension == ".pptx":
                # If PPT files are too large then the content is None. As an alternative, we can use Presentation library to read PPT files fro now
                prs = Presentation(paths)
                print(paths)
                print(
                    "If PPT files are too large then the content is None. As an alternative, we can use Presentation library to read PPT files fro now"
                )
                info = []
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            powerpoint_text = shape.text
                            info.append(powerpoint_text)

                txts[paths] = str(info)

            elif extension in extensions_allowed:
                txts[paths] = str(texts)

            else:
                print("\n file format not recognized \n")

            doc_clean = [cleantext(txts[paths]).split()]

            for i in doc_clean:
                new_items = [item for item in i if not item.isdigit()]
                new_list = [test for test in new_items if (len(test) > 3)]
                new_lists = [
                    items for items in new_list if items not in unwanted_keywords
                ]
                overall.append([new_lists])

    flattened = [val for sublist in overall for val in sublist]
    vocab_frame = pd.DataFrame({"words": flattened})
    print("there are " + str(vocab_frame.shape[0]) + " items in vocab_frame")

    return flattened, vocab_frame, filenames, overall


def dataload_for_frontend(docs, unwanted_keywords):  # extensions_allowed)
    # extensions_allowed = ['.txt', '.pdf', '.eml', '.docx', '.html', '.xml',
    #'.ods', '.doc', '.ppt', '.xls', '.text']

    filenames = []
    count = 0
    overall = []
    for doc in docs:
        count += 1
        paths = doc["id"]
        print("")
        print("Loop:", count)
        print("paths:", paths)
        filenames.append(paths)
        extension = doc["type"]
        print("extension:", extension)

        texts = doc["content"]
        # for text in texts:
        #    # print(str(text))
        doc_clean = [cleantext(texts).split()]
        # print('doc_clean', doc_clean)
        for i in doc_clean:
            new_items = [item for item in i if not item.isdigit()]
            new_list = [test for test in new_items if (len(test) > 3)]
            new_lists = [items for items in new_list if items not in unwanted_keywords]
            overall.append([new_lists])

    flattened = [val for sublist in overall for val in sublist]
    # print(flattened)
    vocab_frame = pd.DataFrame({"words": flattened})
    print("there are " + str(vocab_frame.shape[0]) + " items in vocab_frame")
    return flattened, vocab_frame, filenames, overall
