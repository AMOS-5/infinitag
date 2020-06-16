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
stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()
from tika import parser,detector,language
import io
from pptx import Presentation


def cleantext(doc):

    stop_word_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punct_free = ''.join(ch for ch in stop_word_free if ch not in exclude)
    cleaned_text = " ".join(lemma.lemmatize(word) for word in punct_free.split())

    return cleaned_text


def data_load(dir, unwanted_keywords,extensions_allowed):

    # done: txt,pdf,email,pptx,docx, html,xml,ods
    filenames =[]
    txts = {}
    overall = []
    count = 0
    for path, directories, files in os.walk(dir):
        for file in files:
            count += 1
            paths = os.path.join(path, file)
            extension = os.path.splitext(paths)[1]
            print("\n\nFile extension: " + extension)
            print("file type: " + detector.from_file(paths))
            print(file)
            filenames.append(file)

            file_data = parser.from_file(paths,requestOptions={'timeout': 300})
            text_meta = file_data['metadata']
            texts = file_data['content']

            if (text_meta is None):
                 print ("File meta-data not recognized") #by apache tika

            if (extension == ".pptx"):
                # If PPT files are too large then the content is None. As an alternative, we can use Presentation library to read PPT files fro now
                prs = Presentation(paths)
                print(paths)
                print("If PPT files are too large then the content is None. As an alternative, we can use Presentation library to read PPT files fro now")
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
                new_lists = [items for items in new_list if items not in unwanted_keywords]
                overall.append([new_lists])

    flattened = [val for sublist in overall for val in sublist]
    vocab_frame = pd.DataFrame({'words': flattened})
    print('there are ' + str(vocab_frame.shape[0]) + ' items in vocab_frame')

    return flattened, vocab_frame, filenames,overall

