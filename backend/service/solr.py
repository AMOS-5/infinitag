from backend.solr import SolrDocStorage, SolrTagStorage, config


class SolrService:
    INITIALIZED = False
    SOLR_TAGS = None
    SOLR_DOCS = None

    def __init__(self):
        self.initialize_solr()

    def initialize_solr(self):
        self.SOLR_TAGS = SolrTagStorage(config.tag_storage_solr)
        self.SOLR_DOCS = SolrDocStorage(config.doc_storage_solr)
        self.INITIALIZED = True

    @property
    def tags(self):
        return self.SOLR_TAGS

    @property
    def docs(self):
        return self.SOLR_DOCS
