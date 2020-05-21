class SolrMiddleware(object):
    def __init__(self, app, solr_service):
        self.app = app
        self.solr_service = solr_service

    def __call__(self, environment, start_response):
        if not self.solr_service.INITIALIZED:
            try:
                self.solr_service.initialize_solr()
            except:
                pass

        return self.app(environment, start_response)
