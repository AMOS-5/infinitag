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
import langdetect


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
        _, self.id = os.path.split(path)
        self.keywords = set(keywords)
        self.title = title
        self.file_type = file_type
        self.lang = lang
        self.size = size
        self.creation_date = creation_date
        self.content = content

        # current fix for windows / linux agnostic stuff. The doc can always be deleted with is's
        # id, and the full path is only used for extraction
        try:
            self.full_path = os.path.abspath(path)
        # in case the path does not exist, this is okay since all docs normally are on the ec2
        except Exception as e:
            pass

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
            keywords = {SolrDocKeyword.from_str(kw) for kw in hit["keywords"]}

        return SolrDoc(
            hit["id"],
            *keywords,
            title=hit["title"],
            file_type=hit["type"],
            lang=hit["language"],
            size=hit["size"],
            creation_date=hit["creation_date"],
            content=hit["content"],
        )

    def as_dict(self, keywords_as_str: bool = False) -> dict:
        return {
            "id": self.id,
            "keywords": [
                kw.as_str() if keywords_as_str else kw.as_dict() for kw in self.keywords
            ],
            "title": self.title,
            "type": self.file_type,
            "language": self.lang,
            "size": self.size,
            "creation_date": self.creation_date,
            "content": self.content,
        }

    @property
    def path(self):
        # alias for id
        return self.id


def exists_and_not_empty(res: dict, field: str) -> bool:
    return field in res and res[field]


class FileContent:
    @staticmethod
    def from_result(res: dict) -> str:
        if exists_and_not_empty(res, "contents"):
            return " ".join(word for word in res["contents"])

        log.debug("FileContent is unknown")
        return "unknown"


class Path:
    @staticmethod
    def from_result(res: dict) -> str:
        res = res["metadata"]
        if exists_and_not_empty(res, "stream_name"):
            return res["stream_name"]
        elif exists_and_not_empty(res, "recourcename"):
            return res["resourcename"]

        raise ValueError("Path could not be extracted => no id.")


class Title:
    @staticmethod
    def from_result(res: dict) -> str:
        res = res["metadata"]

        if exists_and_not_empty(res, "resourceName"):
            fname = res["resourceName"]

            # it can happen that multiple file types are found during extraction
            # then this will be a list, the first entry will probably be the
            # most dominant e.g. pptx dominant the rest will be png etc.
            if isinstance(fname, list):
                fname = fname[0]

            # sometimes the title gets uploaded as bytes, make b'TITLE' => TITLE
            matched_bytes = re.match("b'(.+)'", fname)
            if matched_bytes is not None:
                fname = matched_bytes[1]

            return fname

        log.debug(f"Title is unknown: {json.dumps(res, indent=2)}")


        return "unknown"


class Author:
    @staticmethod
    def from_result(res: dict) -> str:
        res = res["metadata"]

        if exists_and_not_empty(res, "Author"):
            return res["Author"]
        elif exists_and_not_empty(res, "meta:author"):
            return res["meta:author"]
        elif exists_and_not_empty(res, "creator"):
            return res["creator"]
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
            t = res["stream_content_type"]
        elif exists_and_not_empty(res, "Content-Type"):
            t = res["Content-Type"]
        else:
            t = "unknown"

        # TODO how to treat multiple detected file types, probably
        # everything here should be ignored and only the extension
        # of the file should be used
        if isinstance(t, list):
            t = t[0]

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
            return res["stream_size"]

        log.debug("FileSize is unknown.")
        return 0


class Language:
    mapping = {
        "de-de": "de",
        "de": "de",
        "en-us": "en",
        "en": "en",
        "ja-jp": "ja",
        "ar-iq": "ar",
    }

    @staticmethod
    def from_result(res: dict) -> str:
        content = res["contents"]
        res = res["metadata"]

        if exists_and_not_empty(res, "language"):
            lang = res["language"]
        elif exists_and_not_empty(res, "dc:language"):
            lang = res["dc:language"]
        else:  # language could not be extracted by tika
            scontent = " ".join(word for word in content)
            lang = langdetect.detect(scontent)

        lang = lang.lower()

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
            return res["meta:creation-date"]
        elif exists_and_not_empty(res, "date"):
            return res["date"]
        elif exists_and_not_empty(res, "Creation-Date"):
            return res["Creation-Date"]
        elif exists_and_not_empty(res, "dcterms:created"):
            return res["dcterms:created"]
        else:
            log.debug("CreationDate is unknown.")
            return str(datetime.now())


__all__ = ["SolrDoc", "SolrDocKeyword", "SolrDocKeywordTypes"]

