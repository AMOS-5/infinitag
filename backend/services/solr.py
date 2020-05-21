from backend.docstorage import SolrDocStorage
from backend.tagstorage import SolrTagStorage
from backend import config


class SolrService:
    INITIALIZED = False
    SOLR_TAGS = None
    SOLR_DOCS = None

    def __init__(self):
        self.initialize_solr()

    def initialize_solr(self):
        self.SOLR_TAGS = SolrTagStorage(config.tag_storage_solr)
        self.SOLR_DOCS = SolrDocStorage(config.doc_storage_solr)

        # add sample tags
        self.SOLR_TAGS.clear()
        self.INITIALIZED = True

    def get_tags(self):
        return self.SOLR_TAGS

    def get_docs(self):
        return self.SOLR_DOCS

