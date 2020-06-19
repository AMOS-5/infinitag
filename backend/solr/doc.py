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

from .keywordmodel import SolrHierarchy

import logging as log
from datetime import datetime
import os
import json
from typing import Set, List
import enum
import re
import sys


# if you activate this you will see why some fields are unknown and maybe can
# find the name of another metadata field to add to the solr parsers
# log.basicConfig(level=log.DEBUG)


class SolrDocKeywordTypes(enum.Enum):
    """
    Enum representing the applied keyword types
    """
    KWM = 1
    ML = 2
    MANUAL = 3

    @staticmethod
    def from_str(s: str) -> "SolrDocKeywordTypes":
        return getattr(SolrDocKeywordTypes, s)


class SolrDocKeyword:
    """
    Class representing a keyword applied to a document
    """

    def __init__(self, value: str, type_: SolrDocKeywordTypes):
        self.value = value
        self.type = type_

    def as_dict(self) -> dict:
        return {"value": self.value, "type": self.type.name}

    def as_str(self) -> str:
        return json.dumps(self.as_dict())

    @staticmethod
    def from_str(hit: str) -> "SolrDocKeyword":
        hit = json.loads(hit)
        value = hit["value"]
        type_ = SolrDocKeywordTypes.from_str(hit["type"])
        return SolrDocKeyword(value, type_)

    def __eq__(self, other: "SolrDocKeyword") -> bool:
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(f"{self.value}{self.type.name}")

    def __lt__(self, other: "SolrDocKeyword") -> bool:
        if self.value == other.value:
            return self.type < other.type

        return self.value < other.value


class SolrDoc:
    """
    Class representing a document in Solr
    """

    def __init__(
        self,
        path: str,
        *keywords: SolrDocKeyword,
        title: str = None,
        file_type: str = None,
        lang: str = None,
        size: str = None,
        creation_date: str = None,
        content: str = None,
    ):
        self.id = os.path.abspath(path)
        self.keywords = list(keywords)
        self.title = title
        self.file_type = file_type
        self.lang = lang
        self.size = size
        self.creation_date = creation_date
        self.content = content

    @staticmethod
    def from_extract(doc: "SolrDoc", res: dict) -> "SolrDoc":
        """
        Populates a SolrDoc with extraction results performed by Solr/Tika.
        """
        doc.title = Title.from_result(res)
        doc.file_type = FileType.from_result(res)
        doc.lang = Language.from_result(res)
        doc.size = FileSize.from_result(res)
        doc.creation_date = CreationDate.from_result(res)
        doc.content = FileContent.from_result(res)
        return doc

    @staticmethod
    def from_hit(hit: dict) -> "SolrDoc":
        """
        Creates a SolrDoc from a search hit
        :param hit:
        :return:
        """

        keywords = []
        if "keywords" in hit:
            keywords = [SolrDocKeyword.from_str(kw) for kw in hit["keywords"]]

        return SolrDoc(
            hit["id"],
            *keywords,
            title=hit["title"][0],
            file_type=hit["type"][0],
            lang=hit["language"][0],
            size=hit["size"][0],
            creation_date=hit["creation_date"][0],
            content=hit["content"][0],
        )

    def as_dict(self, keywords_as_str: bool = False) -> dict:
        return {
            "id": self.id,
            "keywords": [kw.as_str() if keywords_as_str else kw.as_dict() for kw in self.keywords],
            "title": self.title,
            "type": self.file_type,
            "language": self.lang,
            "size": self.size,
            "creation_date": self.creation_date,
            "content": self.content,
        }



    def apply_kwm(self, keywords: dict) -> bool:
        """
        Applies a keyword model given by all its keywords with their parents on this document.

        :param dict of keywords and parents:
        :return: whether the keywords in the document were updated
        """
        new_keywords = SolrKeywordFinder.find(self, keywords)

        if new_keywords:
            self.keywords = new_keywords

        return bool(new_keywords)

    @property
    def path(self):
        # alias for id
        return self.id


class SolrKeywordFinder:
    @staticmethod
    def find(doc: SolrDoc, keywords: dict) -> List[SolrDocKeyword]:
        """
        Finds all keywords from the dict that appear in the document and
        returns them together with the already added ones
        :param doc: document to be searched in
        :param keywords: keywords with their parents
        :return: list of all keywords
        """
        content = SolrKeywordFinder._parse_doc(doc)
        new_keywords = SolrKeywordFinder._find(content, keywords)

        if not new_keywords:
            return []

        new_keywords = {
            SolrDocKeyword(kw, SolrDocKeywordTypes.KWM) for kw in new_keywords
        }
        old_keywords = doc.keywords
        new_keywords.update(old_keywords)

        return list(new_keywords)

    @staticmethod
    def _parse_doc(doc: SolrDoc) -> Set[str]:
        """
        Parses the title and the content of a document into a set
        :param doc:
        :return: the content of a document wordwise in a set
        """
        parsed = set()
        delims = " |\n|\t|;|,|:|\.|\?|!|\(|\)|\{|\}|\[|\]|<|>|\\\\|/|=|\"|\'"
        parsed.update([str.lower() for str in re.split(delims, doc.title)])
        parsed.update([str.lower() for str in re.split(delims, doc.content)])
        return parsed

    @staticmethod
    def _find(content: Set[str], keywords: dict) -> Set[str]:
        """
        Finds all keywords in the set of words and returns them as well as their parents
        :param content: set of words
        :param keywords: dict of keywords
        :return: set of found keywords
        """
        found_keywords = set()

        for kw in list(keywords.keys()):
            if kw in content:
                #print("found ", kw, " parents: ", keywords[kw], file=sys.stdout)
                found_keywords.add(kw)
                for parent in keywords[kw]:
                    found_keywords.add(parent)
                #print("found kw: ", found_keywords, file=sys.stdout)

        return found_keywords

    @staticmethod
    def _is_dimension(hierarchy: dict) -> bool:
        return hierarchy["nodeType"] == "DIMENSION"

    @staticmethod
    def _is_keyword(hierarchy: dict) -> bool:
        return hierarchy["nodeType"] == "KEYWORD"

    @staticmethod
    def _has_children(hierarchy: dict) -> bool:
        return "children" in hierarchy

    @staticmethod
    def _get_children(hierarchy: dict) -> list:
        return hierarchy["children"]

    @staticmethod
    def _get_keyword(hierarchy: dict) -> str:
        return hierarchy["item"]


def exists_and_not_empty(res: dict, field: str) -> bool:
    return field in res and res[field][0]


class FileContent:
    @staticmethod
    def from_result(res: dict) -> str:
        if exists_and_not_empty(res, "contents"):
            return res["contents"]

        log.debug("FileContent is unknown")
        return "unknown"


class Path:
    @staticmethod
    def from_result(res: dict) -> str:
        res = res["metadata"]
        if exists_and_not_empty(res, "stream_name"):
            return res["stream_name"][0]
        elif exists_and_not_empty(res, "recourcename"):
            return res["resourcename"][0]

        raise ValueError("Path could not be extracted => no id.")


class Title:
    @staticmethod
    def from_result(res: dict) -> str:
        res = res["metadata"]

        if exists_and_not_empty(res, "title") and res["title"][0]:
            return res["title"][0]
        elif exists_and_not_empty(res, "dc:title"):
            return res["dc:title"][0]
        elif exists_and_not_empty(res, "stream_name"):
            stream_name = res["stream_name"][0]
            return os.path.basename(stream_name)

        log.debug(f"Title is unknown: {json.dumps(res, indent=2)}")


        return "unknown"


class Author:
    @staticmethod
    def from_result(res: dict) -> str:
        res = res["metadata"]

        if exists_and_not_empty(res, "Author"):
            return res["Author"][0]
        elif exists_and_not_empty(res, "meta:author"):
            return res["meta:author"][0]
        elif exists_and_not_empty(res, "creator"):
            return res["creator"][0]
        else:
            log.debug("Author is unknown.")
            return "unknown"


class FileType:
    type_mapping = {
        "application/pdf": "pdf",
        "text/plain": "txt",
        "application/octet-stream": "octet-stream",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
        "application/vnd.oasis.opendocument.presentation": "odp",
        "unknown": "unknown",
    }

    @staticmethod
    def from_result(res: dict) -> str:
        res = res["metadata"]

        if exists_and_not_empty(res, "stream_content_type"):
            t = res["stream_content_type"][0]
        elif exists_and_not_empty(res, "Content-Type"):
            t = res["Content-Type"][0]
        else:
            t = "unknown"

        if t not in FileType.type_mapping:
            log.debug(f"Found missing type: {t}")
            return t
        elif "unknown" in t:
            log.debug("Filetype is unknown.")
            return t

        return FileType.type_mapping[t]


class FileSize:
    @staticmethod
    def from_result(res: dict) -> str:
        res = res["metadata"]

        if exists_and_not_empty(res, "stream_size"):
            return res["stream_size"][0]

        log.debug("FileSize is unknown.")
        return "unknown"


class Language:
    mapping = {"de-DE": "de", "en-US": "en"}

    @staticmethod
    def from_result(res: dict) -> str:
        res = res["metadata"]

        if exists_and_not_empty(res, "language"):
            lang = res["language"][0]
        elif exists_and_not_empty(res, "dc:language"):
            lang = res["dc:language"][0]
        else:
            lang = "unknown"

        if lang not in Language.mapping:
            log.debug(f"LANGUAGE UNKNOWN / NOT FOUND: {json.dumps(res, indent=3)}")
            return lang

        return Language.mapping[lang]


class CreationDate:
    @staticmethod
    def from_result(res: dict) -> str:
        res = res["metadata"]

        if exists_and_not_empty(
            res, "meta:creation-date"
        ):  # this should persist through saving
            return res["meta:creation-date"][0]
        elif exists_and_not_empty(res, "date"):
            return res["date"][0]
        elif exists_and_not_empty(res, "Creation-Date"):
            return res["Creation-Date"][0]
        elif exists_and_not_empty(res, "dcterms:created"):
            return res["dcterms:created"][0]
        else:
            log.debug("CreationDate is unknown.")
            return str(datetime.now())


__all__ = ["SolrDoc", "SolrDocKeyword", "SolrDocKeywordTypes"]

