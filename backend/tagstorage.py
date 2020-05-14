import pysolr

from typing import List
from urlpath import URL
import copy


class Tag:
    """
    Class representing an object in the TagStorage
    """

    def __init__(self, field: str, tag: str):
        # the name of the field where the tag is stored
        self.field = field
        self.tag = tag

    # makes castable to dict
    def __iter__(self):
        yield self.field, self.tag
        # id is the unique key, to avoid duplicates pass the tag as the id
        yield "id", self.tag


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

        # name of the storage field
        self.field = _conf.pop("field")
        # build the full url
        corename = _conf.pop("corename")
        _conf["url"] = str(URL(_conf["url"]) / corename)
        # connection to the solr instance
        self.con = pysolr.Solr(**_conf)

    def add(self, *tags: str) -> None:
        tags = [dict(Tag(self.field, tag)) for tag in tags]
        self.con.add(tags)

    def delete(self, *tags: str) -> None:
        self.con.delete(id=tags)

    @property
    def tags(self) -> List[str]:
        # search all
        result = self.con.search("*:*")
        # extract only the tag value
        tags = [hit[self.field][0] for hit in result]
        return tags

    def __contains__(self, tag: str) -> bool:
        query = f"{self.field}:{tag}"
        result = self.con.search(query)

        if not result:
            return False

        best_match = next(iter(result))
        return best_match["id"] == tag

    def clear(self):
        self.con.delete(q="*:*")
