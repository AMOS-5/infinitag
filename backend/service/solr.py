from backend.solr import SolrDocStorage, SolrKeywordModel, config


class SolrService:
    INITIALIZED = False
    SOLR_KEYWORD_MODEL = None
    SOLR_DOCS = None

    def __init__(self):
        self.initialize_solr()

    def initialize_solr(self):
        self.SOLR_KEYWORD_MODEL = SolrKeywordModel(config.keyword_model_solr)
        self.SOLR_DOCS = SolrDocStorage(config.doc_storage_solr)
        self.INITIALIZED = True

    @property
    def keywordmodel(self):
        return self.SOLR_KEYWORD_MODEL

    @property
    def kwm(self):
        return self.SOLR_KEYWORD_MODEL

    @property
    def docs(self):
        return self.SOLR_DOCS
