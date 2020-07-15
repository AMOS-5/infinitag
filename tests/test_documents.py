import pytest
import unittest
from backend.solr import SolrDocuments, SolrDoc, SolrDocKeyword, SolrDocKeywordTypes


@pytest.fixture
def doc_with_keyword_in_content(solr_docs):
    doc_id = "doc_with_kw_in_content"
    doc = SolrDoc(
        doc_id,
        content="keyword",
        title="title",
        file_type="file_type",
        lang="lang",
        size=1,
    )
    solr_docs.update(doc)
    return doc_id


@pytest.fixture
def doc_with_keyword_in_keywords_field(solr_docs):
    doc_id = "doc_with_kw_in_kws"
    doc = SolrDoc(
        doc_id,
        SolrDocKeyword("keyword", SolrDocKeywordTypes.MANUAL),
        content="content",
        title="title",
        file_type="file_type",
        lang="lang",
        size=1,
    )
    solr_docs.update(doc)
    return doc_id


@pytest.fixture
def doc_paths():
    import os

    base = f"{os.getcwd()}/tests/test_files/test"
    doc_types = ["pdf", "txt", "pptx", "docx"]

    doc_paths = [f"{base}.{doc_type}" for doc_type in doc_types]
    return doc_paths


@pytest.fixture
def docs_in_solr(solr_docs, doc_paths):
    docs = [SolrDoc(path) for path in doc_paths]
    solr_docs.add(*docs)
    return docs


@pytest.fixture
def doc(docs_in_solr):
    return docs_in_solr[0]


@pytest.fixture
def kw1():
    return SolrDocKeyword("key1", SolrDocKeywordTypes.KWM)


@pytest.fixture
def kw2():
    return SolrDocKeyword("key2", SolrDocKeywordTypes.KWM)


@pytest.fixture
def kw3():
    return SolrDocKeyword("key3", SolrDocKeywordTypes.KWM)


@pytest.fixture
def doc_with_initial_keywords(solr_docs, doc_paths, kw1, kw2):
    doc = SolrDoc(doc_paths[0], kw1, kw2)
    solr_docs.add(doc)
    return doc


@pytest.fixture
def doc_where_tika_cant_find_language(docs_in_solr):
    return docs_in_solr[3]


@pytest.fixture
def doc_with_key1(solr_docs, doc_paths, kw1):
    doc = SolrDoc(doc_paths[0], kw1)
    solr_docs.add(doc)
    return doc


@pytest.fixture
def doc_with_key2(solr_docs, doc_paths, kw2):
    doc = SolrDoc(doc_paths[1], kw2)
    solr_docs.add(doc)
    return doc


@pytest.fixture
def doc_with_germany(solr_docs):
    doc_id = "doc_with_germany"
    doc = SolrDoc(
        doc_id,
        content="germany",
        title="title",
        file_type="file_type",
        lang="lang",
        size=1,
    )
    solr_docs.update(doc)
    return doc_id


@pytest.fixture
def doc_with_deutschland(solr_docs):
    doc_id = "doc_with_deutschland"
    doc = SolrDoc(
        doc_id,
        content="deutschland",
        title="title",
        file_type="file_type",
        lang="lang",
        size=1,
    )
    solr_docs.update(doc)
    return doc_id


@pytest.mark.usefixtures("solr_docs")
class TestDocuments:
    def test_add_and_search(self, docs_in_solr):
        added = self.solr_docs.search("*:*")
        assert len(added) == len(docs_in_solr)

    def test_delete(self, docs_in_solr):
        deleted = docs_in_solr[0]

        self.solr_docs.delete(deleted.path)
        assert deleted.path not in self.solr_docs

    def test_contains(self, docs_in_solr):
        for doc in docs_in_solr:
            assert doc.path in self.solr_docs

        not_existing = "/this/file/does/not/exist"
        assert not_existing not in self.solr_docs

    def test_empty_keywords(self, docs_in_solr):
        docs = self.solr_docs.get(*[doc.path for doc in docs_in_solr])
        for doc in docs:
            assert not doc.keywords

    def test_initial_keywords(self, doc_with_initial_keywords, kw1, kw2):
        doc = self.solr_docs.get(doc_with_initial_keywords.path)

        assert kw1 in doc.keywords
        assert kw2 in doc.keywords

    def test_update_keywords(self, doc_with_initial_keywords, kw1, kw2, kw3):
        doc = self.solr_docs.get(doc_with_initial_keywords.path)
        doc.keywords.remove(kw1)
        doc.keywords.add(kw3)
        self.solr_docs.update(doc)

        doc = self.solr_docs.get(doc.path)
        assert kw1 not in doc.keywords
        assert kw2 in doc.keywords
        assert kw3 in doc.keywords

    def test_correct_language_extraction(self, doc_where_tika_cant_find_language):
        doc = self.solr_docs.get(doc_where_tika_cant_find_language.path)
        assert doc.lang == "en"

    def test_pagination_sort_asc(self, docs_in_solr):
        expected_page1 = ["test.docx", "test.pdf"]
        _, docs = self.solr_docs.page(0, 2, "id", "asc")
        doc_ids = [doc.id for doc in docs]
        assert doc_ids == expected_page1

        expected_page2 = ["test.pptx", "test.txt"]
        _, docs = self.solr_docs.page(1, 2, "id", "asc")
        doc_ids = [doc.id for doc in docs]
        assert doc_ids == expected_page2

    def test_pagination_sort_desc(self, docs_in_solr):
        expected_page1 = ["test.txt", "test.pptx"]
        _, docs = self.solr_docs.page(0, 2, "id", "desc")
        doc_ids = [doc.id for doc in docs]
        assert doc_ids == expected_page1

        expected_page2 = ["test.pdf", "test.docx"]
        _, docs = self.solr_docs.page(1, 2, "id", "desc")
        doc_ids = [doc.id for doc in docs]
        assert doc_ids == expected_page2

    def test_total_num_pages(self, docs_in_solr):
        total_num_pages, _ = self.solr_docs.page(0, 1)
        assert total_num_pages == 4

        total_num_pages, _ = self.solr_docs.page(0, 2)
        assert total_num_pages == 2

        total_num_pages, _ = self.solr_docs.page(0, 3)
        assert total_num_pages == 2

        total_num_pages, _ = self.solr_docs.page(0, 4)
        assert total_num_pages == 1

    def test_pagination_sort_field_does_not_exist(self):
        with pytest.raises(ValueError):
            self.solr_docs.page(0, 1, "not_existing_field", "asc")

    def test_pagination_search_term(self, docs_in_solr):
        try:
            self.solr_docs.page(search_term="asdf")
        except Exception as e:
            self.fail(f"Raised unexpected exception: {e}")

    def test_pagination_year_search(self, docs_in_solr):
        import datetime

        current_year = datetime.datetime.now().strftime("%Y")
        _, docs = self.solr_docs.page(search_term=current_year)

        assert len(docs) == 4

    def test_pagination_size_search(self, docs_in_solr):
        _, docs = self.solr_docs.page(search_term="8137")
        assert len(docs) == 1

    def test_pagination_keywords_only_search(
        self, doc_with_keyword_in_content, doc_with_keyword_in_keywords_field
    ):
        _, docs = self.solr_docs.page(search_term="keyword", keywords_only=True)
        assert len(docs) == 1

    def test_pagination_not_keywords_only_search(
        self, doc_with_keyword_in_content, doc_with_keyword_in_keywords_field
    ):
        _, docs = self.solr_docs.page(search_term="keyword", keywords_only=False)
        assert len(docs) == 2

    def test_pagination_search_term_consists_of_multiple_words(
        self, doc_with_key1, doc_with_key2
    ):
        _, docs = self.solr_docs.page(search_term="key1 key2")
        assert len(docs) == 2

    def test_pagination_search_with_start_date(self, docs_in_solr):
        from datetime import datetime

        start_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        _, docs = self.solr_docs.page(start_date=start_date)
        assert len(docs) == 4

    def test_pagination_search_with_start_and_end_date(self, docs_in_solr):
        from datetime import datetime, timedelta

        start_date = datetime.utcnow() - timedelta(hours=2)
        end_date = start_date + timedelta(hours=4)

        _, docs = self.solr_docs.page(
            start_date=start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            end_date=end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        assert len(docs) == 4

    def test_doc_last_modified_date_changes_on_each_update(self, doc):
        import time
        import copy

        # wait and update to check the the modified date has changed
        time.sleep(5)
        self.solr_docs.update(copy.deepcopy(doc))
        doc_after = self.solr_docs.get(doc.id)

        assert doc.last_modified != doc_after.last_modified
        assert doc.creation_date == doc_after.creation_date

    def test_translation_search(self, doc_with_germany, doc_with_deutschland):
        _, docs = self.solr_docs.page(search_term="germany")
        assert len(docs) == 2

        _, docs = self.solr_docs.page(search_term="deutschland")
        assert len(docs) == 2

    def test_uploading_empty_documents(self):
        doc = SolrDoc("tests/test_files/empty_doc.txt")
        try:
            self.solr_docs.add(doc)
            doc = self.solr_docs.get(doc.id)

            assert doc.content == "unknown"
        except Exception as e:
            pytest.fail(f"Raised unexpected exception: {e}")
