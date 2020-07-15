from backend.solr import SolrDocuments, SolrDoc, config
docs = SolrDocuments(config.documents_solr)
docs.clear()
