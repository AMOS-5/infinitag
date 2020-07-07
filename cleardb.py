from backend.solr import SolrDocStorage, SolrDoc, config
docs = SolrDocStorage(config.doc_storage_solr)
docs.clear()
