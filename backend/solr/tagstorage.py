import pysolr

from typing import List
from urlpath import URL
import copy


class Tag:
    """
    Class representing an object in the TagStorage
    """

    def __init__(self, tag: str):
        # the name of the field where the tag is stored
        self.tag = tag

    def as_dict(self):
        return {"id": self.tag}


class TagStorage:
    def add(self, *tags: str) -> None:
        """
        Adds tags to the TagStorage

        :param tags: List of tags
        :return:
        """
        ...

    def delete(self, *tags: str) -> None:
        """
        Deletes tags from the TagStorage

        :param tags: List of tags
        :return:
        """

    @property
    def tags(self) -> List[str]:
        """
        Returns the tags stored in the TagStorage

        :return: List of tags
        """
        ...

    def __contains__(self, tag: str) -> bool:
        """
        Checks whether a tag is present in the TagStorage

        :param tag: Tag to be tested
        :return:
        """
        ...


class SolrTagStorage(TagStorage):
    def __init__(self, config: dict):
        # we'll modify the original configuration
        _conf = copy.deepcopy(config)

        # build the full url
        corename = _conf.pop("corename")
        _conf["url"] = str(URL(_conf["url"]) / corename)
        # connection to the solr instance
        self.con = pysolr.Solr(**_conf)

    def add(self, *tags: str) -> None:
        tags = [Tag(tag).as_dict() for tag in tags]
        self.con.add(tags)

    def delete(self, *tags: str) -> None:
        self.con.delete(id=tags)

    @property
    def tags(self) -> List[str]:
        # search all max results = 5k currently
        result = self.con.search("*:*", rows=5000)
        # extract only the tag value
        tags = [hit["id"] for hit in result]
        return tags

    def __contains__(self, tag: str) -> bool:
        query = f"id:*{tag}"
        res = self.con.search(query)
        hit = self._get_hit(res, tag)
        return hit is not None

    def clear(self):
        self.con.delete(q="*:*")

    def _get_hit(self, res: dict, tag: str) -> dict:
        for hit in res:
            if hit["id"] == tag:
                return hit["id"]

        return None

