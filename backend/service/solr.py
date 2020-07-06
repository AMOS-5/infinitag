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
from backend.service.tagging import TaggingService
from backend.solr import (
    SolrKeywordModel,
    SolrKeywords,
    SolrDocStorage,
    SolrKeywordStatistics,
    SolrStatistics,
    config,
)


class SolrService:
    INITIALIZED = False

    def __init__(self):
        self.initialize_solr()

    def initialize_solr(self):
        self.SOLR_KEYWORD_MODEL = SolrKeywordModel(config.keyword_model_solr)
        self.SOLR_KEYWORDS = SolrKeywords(config.keywords_solr)
        self.SOLR_DIMENSIONS = SolrKeywords(config.dimensions_solr)
        self.SOLR_DOCS = SolrDocStorage(config.doc_storage_solr)
        self.SOLR_KEYWORD_STATISTICS = SolrKeywordStatistics(
            config.keyword_statistics_solr, self.docs
        )
        self.SOLR_STATISTICS = SolrStatistics(
            self.docs, self.keywordmodel, self.keyword_statistics
        )

        self.INITIALIZED = True

    @property
    def keywordmodel(self):
        return self.SOLR_KEYWORD_MODEL

    @property
    def kwm(self):
        return self.keywordmodel

    @property
    def keywords(self):
        return self.SOLR_KEYWORDS

    @property
    def dimensions(self):
        return self.SOLR_DIMENSIONS

    @property
    def docs(self):
        return self.SOLR_DOCS

    @property
    def keyword_statistics(self):
        return self.SOLR_KEYWORD_STATISTICS

    @property
    def statistics(self):
        return self.SOLR_STATISTICS


__all__ = ["SolrService"]
