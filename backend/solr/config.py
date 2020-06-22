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

keyword_model_solr = {
    "corename": "keyword_model",
    "url": "http://ec2-3-86-180-141.compute-1.amazonaws.com:8983/solr",
    #"url": "http://localhost:8983/solr",
    "always_commit": True,  # will instantly apply changes, maybe change later
}

keywords_solr = {
    "corename": "keywords",
    "url": "http://ec2-3-86-180-141.compute-1.amazonaws.com:8983/solr",
    #"url": "http://localhost:8983/solr",
    "always_commit": True,  # will instantly apply changes, maybe change later
}

dimensions_solr = {
    "corename": "dimensions",
    "url": "http://ec2-3-86-180-141.compute-1.amazonaws.com:8983/solr",
    #"url": "http://localhost:8983/solr",
    "always_commit": True,  # will instantly apply changes, maybe change later
}

doc_storage_solr = {
    "corename": "documents",
    "url": "http://ec2-3-86-180-141.compute-1.amazonaws.com:8983/solr",
    #"url": "http://localhost:8983/solr",
    "always_commit": True,  # will instantly apply changes, maybe change later
}

file_storage = {
    "path": "~/filestorage"
}
