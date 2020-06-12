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

from .doc import SolrDoc
from .keywordmodel import SolrHierarchy

import pysolr

import os
import logging as log
from typing import List, Union
from pathlib import Path
from urlpath import URL
import copy
import json


# TODO setup a logging class discuss with everyone before
try:
    os.mkdir("./log")
except:
    # dir exists
    pass


# log.basicConfig(level=log.INFO)
# log.basicConfig(level=log.ERROR)


class SolrDocStorage:
    """
    Provides functionality to strore / modify and retrive documents
    from Solr
    """

    def __init__(self, config: dict):
        # we'll modify the original configuration
        _conf = copy.deepcopy(config)

        # build the full url
        self.corename = _conf.pop("corename")
        self.url = URL(_conf["url"]) / self.corename
        _conf["url"] = str(self.url)
        # connection to the solr instance
        self.con = pysolr.Solr(**_conf)

    def add(self, *docs: SolrDoc) -> bool:
        """
        Adds documents to Solr
        """
        extracted_data = self._extract(*docs)
        docs = [
            SolrDoc.from_extract(doc, res).as_dict()
            for doc, res in zip(docs, extracted_data)
        ]
        self.con.add(docs)

    def _extract(self, *docs: SolrDoc) -> List[dict]:
        """
        Extracts the content / metadata of files
        """
        return [self.__extract(doc) for doc in docs]

    def __extract(self, doc: SolrDoc) -> dict:
        with open(doc.id, "rb") as f:
            res = self.con.extract(f)
            return res

    def get(self, *docs: str) -> Union[SolrDoc, List[SolrDoc]]:
        docs = [self._get(doc) for doc in docs]
        return docs[0] if len(docs) == 1 else docs

    def _get(self, doc: str) -> SolrDoc:
        # TODO don't know 100% whether this can fail or not
        query = f"id:*{doc}"

        res = self.con.search(query)
        hit = self._get_hit(res, doc)
        if hit is None:
            return None

        return SolrDoc.from_hit(hit)

    def update(self, *docs: SolrDoc):
        self.con.add([doc.as_dict() for doc in docs])

    # query syntax = Solr
    def search(self, query: str, max_results: int = 300) -> dict:
        return self.con.search(query, rows=max_results)

    def delete(self, *docs: str) -> None:
        # the id of a doc corresponds to the path where it is stored (or where it was
        # indexed from), in our case our filestorage
        self.con.delete(id=docs)

    def __contains__(self, doc: str) -> bool:
        query = f"id:*{doc}"
        res = self.con.search(query)
        hit = self._get_hit(res, doc)
        return hit is not None

    def clear(self):
        self.con.delete(q="*:*")

    def _get_hit(self, res: dict, doc: str) -> dict:
        for hit in res:
            if hit["id"] == doc:
                return hit

        return None


__all__ = ["SolrDocStorage"]
