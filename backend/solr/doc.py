import logging as log
from datetime import datetime
import os
import json

# if you activate this you will see why some fields are unknown and maybe can
# find the name of another metadata field to add to the solr parsers
# log.basicConfig(level=log.DEBUG)


class SolrDoc:
    """
    SolrDoc
    """

    def __init__(
        self,
        path: str,
        *tags: str,
        title: str = None,
        file_type: str = None,
        lang: str = None,
        size: str = None,
        creation_date: str = None,
        content: str = None,
    ):
        self.id = os.path.abspath(path)
        self.tags = list(tags)
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
    def from_hit(hit: dict):
        """
        Creates a SolrDoc from a search hit
        """
        return SolrDoc(
            hit["id"],
            *hit["tags"] if "tags" in hit else [],
            title=hit["title"],
            file_type=hit["type"],
            lang=hit["language"],
            size=hit["size"],
            creation_date=hit["creation_date"],
            content=hit["content"],
        )

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "tags": self.tags,
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


class FileContent:
    @staticmethod
    def from_result(res: dict) -> str:
        if "contents" in res:
            return res["contents"]

        log.debug("FileContent is unknown")
        return "unknown"


class Path:
    @staticmethod
    def from_result(res: dict) -> str:
        res = res["metadata"]
        if "stream_name" in res:
            return res["stream_name"][0]
        elif "recourcename" in res:
            return res["resourcename"][0]

        raise ValueError("Path could not be extracted => no id.")


class Title:
    @staticmethod
    def from_result(res: dict) -> str:
        res = res["metadata"]

        if "title" in res:
            return res["title"][0]
        elif "dc:title" in res:
            return res["dc:title"][0]

        log.debug(f"Title is unknown: {json.dumps(res, indent=2)}")
        return "unknown"


class Author:
    @staticmethod
    def from_result(res: dict) -> str:
        res = res["metadata"]

        if "Author" in res:
            return res["Author"][0]
        elif "meta:author" in res:
            return res["meta:author"][0]
        elif "creator" in res:
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

        if "stream_content_type" in res:
            t = res["stream_content_type"][0]
        elif "Content-Type" in res:
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

        if "stream_size" in res:
            return res["stream_size"][0]

        log.debug("FileSize is unknown.")
        return "unknown"


class Language:
    mapping = {"de-DE": "de", "en-US": "en"}

    @staticmethod
    def from_result(res: dict) -> str:
        res = res["metadata"]

        if "language" in res:
            lang = res["language"][0]
        elif "dc:language" in res:
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

        if "meta:creation-date" in res:  # this should persist through saving
            return res["meta:creation-date"][0]
        elif "date" in res:
            return res["date"][0]
        elif "Creation-Date" in res:
            return res["Creation-Date"][0]
        elif "dcterms:created" in res:
            return res["dcterms:created"][0]
        else:
            log.debug("CreationDate is unknown.")
            return str(datetime.now())
