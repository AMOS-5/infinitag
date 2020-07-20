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
    "url": "http://18.235.6.254:8983/solr",
    # "url": "http://localhost:8983/solr",
    "always_commit": True,  # will instantly apply changes, maybe change later
}

keywords_solr = {
    "corename": "keywords",
    "url": "http://18.235.6.254:8983/solr",
    # "url": "http://localhost:8983/solr",
    "always_commit": True,  # will instantly apply changes, maybe change later
}

dimensions_solr = {
    "corename": "dimensions",
    "url": "http://18.235.6.254:8983/solr",
    # "url": "http://localhost:8983/solr",
    "always_commit": True,  # will instantly apply changes, maybe change later
}

documents_solr = {
    "corename": "documents",
    "url": "http://18.235.6.254:8983/solr",
    # "url": "http://localhost:8983/solr",
    "always_commit": True,  # will instantly apply changes, maybe change later
    # the translator uses the google translation api to detect and translate
    # the search terms. If you don't want that your search terms are translated
    # by google set the target lang array to be empty. See "googletrans" package
    # for more information on language codes.
    "translator_target_languages": ["de", "en"]
}

keyword_statistics_solr = {
    "corename": "keyword_statistics",
    "url": "http://18.235.6.254:8983/solr",
    # "url": "http://localhost:8983/solr",
    "always_commit": True,
}

file_storage = {
    "path": "~/filestorage"
}
