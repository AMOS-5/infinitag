"""
Module handling the document metadata
"""
from datetime import datetime

class DocumentData:
    """
    Class encapsuling the metadata of a document file
    """

    def __init__(self, name: str, path: str, type: str, lang: str, size: int, createdAt: datetime):
        """
        Constructs a new DocumentData object

        :param name: Filename as string
        :param path: Filepath as string
        :param type: Filetype as string
        :param lang: Language of the document as string
        :param size: Size of the document as int
        :param createdAt: Creationdate of document as datetime object
        :return:
        """
        self.name = name
        self.path = path
        self.type = type
        self.lang = lang
        self.size = size
        self.createdAt = createdAt

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
            "createdAt" : self.createdAt.ctime()
        }