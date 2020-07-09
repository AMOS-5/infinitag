import pytest
from pytest_solr.factories import solr_process, solr_core

from backend.solr import (
    SolrDocuments,
    SolrKeywords,
    SolrKeywordModel,
    SolrKeywordStatistics,
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
solr_dimensions_core = solr_core("solr_process", "test_dimensions_core")
solr_keyword_statistics_core = solr_core("solr_process", "test_keyword_statistics_core")


@pytest.fixture(scope="function")
def solr_docs(request, solr_docs_core):
    config = {
        "corename": "test_documents_core",
        "url": "http://localhost:8983/solr/",
        "always_commit": True,
        "translator_target_languages": ["de", "en"]
    }

    request.cls.solr_docs = SolrDocuments(config)
    request.cls.solr_docs.clear()
    yield request.cls.solr_docs
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
    yield request.cls.solr_keyword_model
    request.cls.solr_keyword_model.clear()


@pytest.fixture(scope="function")
def solr_dimensions(request, solr_dimensions_core):
    config = {
        "corename": "test_dimensions_core",
        "url": "http://localhost:8983/solr/",
        "always_commit": True,
    }

    request.cls.solr_dimensions = SolrKeywords(config)
    request.cls.solr_dimensions.clear()
    yield
    request.cls.solr_dimensions.clear()


@pytest.fixture(scope="function")
def solr_keyword_statistics(request, solr_keyword_statistics_core, solr_docs):
    config = {
        "corename": "test_keyword_statistics_core",
        "url": "http://localhost:8983/solr/",
        "always_commit": True,
    }

    request.cls.solr_keyword_statistics = SolrKeywordStatistics(
        config, request.cls.solr_docs
    )
    request.cls.solr_keyword_statistics.clear()
    yield
    request.cls.solr_keyword_statistics.clear()


@pytest.fixture(scope="function")
def app_fixture(
    request,
    solr_docs,
    solr_keywords,
    solr_keyword_model,
    solr_dimensions,
    solr_keyword_statistics,
):
    from backend.solr import config

    # reinit for test
    config_keyword_model = config.keyword_model_solr
    config_keyword_model["corename"] = "test_keyword_model_core"
    config_keyword_model["url"] = "http://localhost:8983/solr"

    config_keywords = config.keywords_solr
    config_keywords["corename"] = "test_keywords_core"
    config_keywords["url"] = "http://localhost:8983/solr"

    config_docs = config.documents_solr
    config_docs["corename"] = "test_documents_core"
    config_docs["url"] = "http://localhost:8983/solr"

    config_dims = config.dimensions_solr
    config_dims["corename"] = "test_dimensions_core"
    config_dims["url"] = "http://localhost:8983/solr"

    config_kw_stat = config.keyword_statistics_solr
    config_kw_stat["corename"] = "test_keyword_statistics_core"
    config_kw_stat["url"] = "http://localhost:8983/solr"

    # will initialize the application with the test config
    import app as application

    request.cls.application = application
