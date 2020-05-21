"""
Module handling the document metadata
"""
from datetime import datetime
from typing import List

import sys
import re

class DocumentData:
    """
    Class encapsuling the metadata of a document file
    """

    def __init__(self, name: str, path: str, type: str, lang: str, size: int, createdAt: datetime, tags: List[str]):
        """
        Constructs a new DocumentData object

        :param name: Filename as string
        :param path: Filepath as string
        :param type: Filetype as string
        :param lang: Language of the document as string
        :param size: Size of the document as int
        :param createdAt: Creationdate of document as datetime object
        :param tags: Tags as a list of strings
        :return:
        """
        self.name = name
        self.path = path
        self.type = type
        self.lang = lang
        self.size = size
        self.createdAt = createdAt
        self.tags = tags

    @classmethod
    def documentdata_from_result(cls, result: dict):
        """
        Constructs a new DocumentData object from a dict returned by a solr search

        :param result: dict given by solr
        :return: DocumentData object
        """
        name = 'no name'
        path = 'no path'
        type = 'no type'
        lang = 'no lang'
        size = 'no size'
        createdAt = datetime.today()
        tags = []

        if 'title' in result:
            name = result['title']
        elif 'dc_title' in result:
            name = result['dc_title']

        if 'id' in result:
            path = result['id']
        
        if 'stream_content_type' in result:
            type = result['stream_content_type']
        
        if 'language' in result:
            lang = result['language']

        if 'stream_size' in result:
            size=result['stream_size']
        
        if 'date' in result:
            createdAt=datetime.strptime(result['date'][0], '%Y-%m-%dT%H:%M:%SZ')

        if 'keywords' in result:
            tags = re.split(',|;', result['keywords'][0])
       
        return cls(
            name=name,
            path=path,
            type=type,
            lang=lang,
            size=size,
            createdAt=createdAt,
            tags=tags
        )

    def as_dict(self):
        """
        Inserts relevant member variables into a dictionary and returns it
        (calls .ctime() on datetime variables to convert them to strings)
        :return: dictionary with variable names as keys
        """
        return {
            "name" : self.name,
            "path" : self.path,
            "type" : self.type,
            "lang" : self.lang,
            "size" : self.size,
            "createdAt" : self.createdAt.ctime(),
            "tags" : self.tags
        }