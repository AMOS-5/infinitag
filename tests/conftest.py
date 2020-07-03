import pytest
from pytest_solr.factories import solr_process, solr_core

from backend.solr import (
    SolrDocStorage,
    SolrKeywords,
    SolrKeywordModel,
)

solr_process = solr_process(
    executable="./downloads/solr-8.5.1/bin/solr",
    host="localhost",
    port=8983,
    core="test_documents",
    version="8.5.1",
    timeout=60,
)


solr_docs_core = solr_core("solr_process", "test_documents_core")
solr_keywords_core = solr_core("solr_process", "test_keywords_core")
solr_keyword_model_core = solr_core("solr_process", "test_keyword_model_core")


@pytest.fixture(scope="function")
def solr_docs(request, solr_docs_core):
    config = {
        "corename": "test_documents_core",
        "url": "http://localhost:8983/solr/",
        "always_commit": True,
    }

    request.cls.solr_docs = SolrDocStorage(config)
    request.cls.solr_docs.clear()
    yield
    request.cls.solr_docs.clear()


@pytest.fixture(scope="function")
def solr_keywords(request, solr_keywords_core):
    config = {
        "corename": "test_keywords_core",
        "url": "http://localhost:8983/solr/",
        "always_commit": True,
    }

    request.cls.solr_keywords = SolrKeywords(config)
    request.cls.solr_keywords.clear()
    yield
    request.cls.solr_keywords.clear()


@pytest.fixture(scope="function")
def solr_keyword_model(request, solr_keyword_model_core):
    config = {
        "corename": "test_keyword_model_core",
        "url": "http://localhost:8983/solr/",
        "always_commit": True,
    }

    request.cls.solr_keyword_model = SolrKeywordModel(config)
    request.cls.solr_keyword_model.clear()
    yield
    request.cls.solr_keyword_model.clear()
