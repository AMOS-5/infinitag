import pysolr

from typing import List
from urlpath import URL
import copy
import json


class SolrTag:
    """
    Class representing an object in the TagStorage
    """

    def __init__(self, tag: str):
        # the name of the field where the tag is stored
        self.tag = tag

    def as_dict(self) -> dict:
        return {"id": self.tag}

    @staticmethod
    def from_hit(hit: dict) -> str:
        return hit["id"]


class SolrHierarchy:
    def __init__(self, name: str, hierarchy: dict):
        self.name = name
        self.hierarchy = hierarchy

    def as_dict(self) -> dict:
        return {"id": self.name, "hierarchy": json.dumps(self.hierarchy)}

    def __getitem__(self, k: str):
        return self.hierarchy[k]

    def __setitem__(self, k, v):
        self.hierarchy[k] = v

    @staticmethod
    def from_hit(hit: dict) -> "SolrHierarchy":
        name = hit["id"]
        unicode_hierarchy = SolrHierarchy._unicode(hit["hierarchy"][0])
        hierarchy = json.loads(unicode_hierarchy)
        return SolrHierarchy(name, hierarchy)

    @staticmethod
    def _unicode(hierarchy: str) -> str:
        """
        Interprets escape characters to apply unicode encoding
        """
        return bytes(hierarchy, "utf-8").decode("unicode_escape")


class SolrKeywordModel:
    def __init__(self, config: dict):
        # we'll modify the original configuration
        _conf = copy.deepcopy(config)

        # build the full url
        corename = _conf.pop("corename")
        _conf["url"] = str(URL(_conf["url"]) / corename)
        # connection to the solr instance
        self.con = pysolr.Solr(**_conf)

    def add_tags(self, *tags: str) -> None:
        tags = [SolrTag(tag).as_dict() for tag in tags]
        self.con.add(tags)

    @property
    def tags(self) -> List[str]:
        # search all max results = 5k currently
        result = self.con.search("*:*", rows=5000)
        # extract only the tag value
        tags = [SolrTag.from_hit(hit) for hit in result]
        return tags

    def delete_tags(self, *tags: str) -> None:
        self.con.delete(id=tags)

    def add_hierarchies(self, *hierarchies: SolrHierarchy) -> None:
        self.con.add([hierarchy.as_dict() for hierarchy in hierarchies])

    def update_hierarchies(self, *hierarchies: SolrHierarchy) -> None:
        self.add_hierarchies(*hierarchies)

    @property
    def hierarchies(self) -> List[SolrHierarchy]:
        res = self.con.search("hierarchy:*", rows=5000)
        return [SolrHierarchy.from_hit(hit) for hit in res]

    def delete_hierarchies(self, *hierarchy_names: str) -> None:
        self.con.delete(id=hierarchy_names)

    def clear(self):
        self.con.delete(q="*:*")

    def __contains__(self, tag: str) -> bool:
        """
        Checks whether the given tag/id is in the storage
        """
        query = f"id:*{tag}"
        res = self.con.search(query)
        hit = self._get_hit(res, tag)
        return hit is not None

    def _get_hit(self, res: dict, tag: str) -> dict:
        for hit in res:
            if hit["id"] == tag:
                return hit["id"]

        return None
