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
from backend.solr import (
    SolrKeywordModel,
    SolrDocStorage,
    SolrKeywords,
    SolrDocKeyword,
)

from typing import Set, List, Generator


class SolrKeywordStatistics(SolrKeywords):
    def __init__(self, config: dict, solr_docs: SolrDocStorage):
        super().__init__(config)
        self.solr_docs = solr_docs

    def update(
        self, keywords_before: Set[SolrDocKeyword], keywords_after: Set[SolrDocKeyword]
    ) -> None:
        keywords_before = {kw.value for kw in keywords_before}
        keywords_after = {kw.value for kw in keywords_after}

        distinct_keywords = keywords_before ^ keywords_after

        keywords_to_add = [kw for kw in distinct_keywords if kw in keywords_after]
        if keywords_to_add:
            self.add(*keywords_to_add)

        delete_candidates = (kw for kw in distinct_keywords if kw in keywords_before)
        keywords_to_delete = self._keywords_to_delete(delete_candidates)
        if keywords_to_delete:
            self.delete(*keywords_to_delete)

    def _keywords_to_delete(self, delete_candidates: Generator[str, None, None]) -> List[str]:
        keywords_to_delete = []
        for kw in delete_candidates:
            keyword_in_docs = self.solr_docs.search(f"keywords:{kw}", rows=1).hits
            if not keyword_in_docs:
                keywords_to_delete.append(kw)

        return keywords_to_delete


class SolrStatistics:
    def __init__(
        self,
        solr_docs: SolrDocStorage,
        solr_keywordmodel: SolrKeywordModel,
        solr_keyword_statistics: SolrKeywordStatistics,
    ):
        self.solr_docs = solr_docs
        self.solr_keywordmodel = solr_keywordmodel
        self.solr_keyword_statistics = solr_keyword_statistics

    def docs(self):
        n_total = self.solr_docs.con.search("*:*", rows=1).hits
        # where keywords field empty
        n_untagged = self.solr_docs.con.search("-keywords:[* TO *]").hits
        n_tagged = n_total - n_untagged
        return n_total, n_tagged, n_untagged

    def keywords(self):
        return self.solr_keyword_statistics.con.search("*:*", rows=1).hits

    def keywordmodel(self):
        return self.solr_keywordmodel.con.search("*:*", rows=1).hits


__all__ = ["SolrKeywordStatistics", "SolrStatistics"]
