import pytest
import unittest
from backend.solr import SolrDocStorage, SolrDoc, SolrDocKeyword, SolrDocKeywordTypes


@pytest.mark.usefixtures("solr_docs")
class TestDocStorage(unittest.TestCase):
    def setUp(self):
        import os

        base = f"{os.getcwd()}/tests/test_docstorage_files/test"
        self.doc_types = ["pdf", "txt", "pptx", "docx"]

        self.doc_paths = [f"{base}.{doc_type}" for doc_type in self.doc_types]
        self.docs = [SolrDoc(path) for path in self.doc_paths]

    def test_add_and_search(self):
        self.solr_docs.add(*self.docs)

        added = self.solr_docs.search("*:*")
        self.assertEqual(len(added), len(self.docs))

    def test_delete(self):
        self.solr_docs.add(*self.docs)

        deleted = self.docs[0]

        self.solr_docs.delete(deleted.path)
        self.assertTrue(deleted.path not in self.solr_docs)

    def test_contains(self):
        self.solr_docs.add(*self.docs)

        for doc in self.docs:
            self.assertTrue(doc.path in self.solr_docs)

        not_existing = "/this/file/does/not/exist"
        self.assertTrue(not_existing not in self.solr_docs)

    def test_empty_keywords(self):
        doc = SolrDoc(self.doc_paths[0])
        self.solr_docs.add(doc)
        doc = self.solr_docs.get(doc.path)

        self.assertFalse(doc.keywords)

    def test_initial_keywords(self):
        kw1 = SolrDocKeyword("key1", SolrDocKeywordTypes.KWM)
        kw2 = SolrDocKeyword("key2", SolrDocKeywordTypes.KWM)

        doc = SolrDoc(self.doc_paths[0], kw1, kw2)
        self.solr_docs.add(doc)

        doc = self.solr_docs.get(doc.path)

        self.assertTrue(kw1 in doc.keywords)
        self.assertTrue(kw2 in doc.keywords)

    def test_update_keywords(self):
        kw1 = SolrDocKeyword("key1", SolrDocKeywordTypes.KWM)
        kw2 = SolrDocKeyword("key2", SolrDocKeywordTypes.KWM)
        kw3 = SolrDocKeyword("key3", SolrDocKeywordTypes.KWM)

        doc = SolrDoc(self.doc_paths[0], kw1, kw2)
        self.solr_docs.add(doc)

        doc = self.solr_docs.get(doc.path)
        doc.keywords.remove(kw1)
        doc.keywords.add(kw3)
        self.solr_docs.update(doc)

        doc = self.solr_docs.get(doc.path)
        self.assertTrue(kw1 not in doc.keywords)
        self.assertTrue(kw2 in doc.keywords)
        self.assertTrue(kw3 in doc.keywords)

    def test_correct_language_extraction(self):
        expected_lang = "en"

        # doc where tika can't parse the language
        doc = self.docs[3]
        self.solr_docs.add(doc)

        doc = self.solr_docs.get(doc.path)

        self.assertEqual(doc.lang, expected_lang)

    def test_pagination_sort_asc(self):
        self.solr_docs.add(*self.docs)

        expected_page1 = ["test.docx", "test.pdf"]
        _, docs = self.solr_docs.page(0, 2, "id", "asc")
        doc_ids = [doc.id for doc in docs]
        self.assertEqual(doc_ids, expected_page1)

        expected_page2 = ["test.pptx", "test.txt"]
        _, docs = self.solr_docs.page(1, 2, "id", "asc")
        doc_ids = [doc.id for doc in docs]
        self.assertEqual(doc_ids, expected_page2)

    def test_pagination_sort_desc(self):
        self.solr_docs.add(*self.docs)

        expected_page1 = ["test.txt", "test.pptx"]
        _, docs = self.solr_docs.page(0, 2, "id", "desc")
        doc_ids = [doc.id for doc in docs]
        self.assertEqual(doc_ids, expected_page1)

        expected_page2 = ["test.pdf", "test.docx"]
        _, docs = self.solr_docs.page(1, 2, "id", "desc")
        doc_ids = [doc.id for doc in docs]
        self.assertEqual(doc_ids, expected_page2)

    def test_total_num_pages(self):
        self.solr_docs.add(*self.docs)

        total_num_pages, _ = self.solr_docs.page(0, 1)
        self.assertEqual(total_num_pages, 4)

        total_num_pages, _ = self.solr_docs.page(0, 2)
        self.assertEqual(total_num_pages, 2)

        total_num_pages, _ = self.solr_docs.page(0, 3)
        self.assertEqual(total_num_pages, 2)

        total_num_pages, _ = self.solr_docs.page(0, 4)
        self.assertEqual(total_num_pages, 1)

    def test_pagination_sort_field_does_not_exist(self):
        with self.assertRaises(ValueError):
            self.solr_docs.page(0, 1, "not_existing_field", "asc")

    def test_pagination_search_term(self):
        self.solr_docs.add(*self.docs)

        try:
            self.solr_docs.page(search_term="asdf")
        except Exception as e:
            self.fail(f"Raised unexpected exception: {e}")

    def test_pagination_year_search(self):
        import datetime

        self.solr_docs.add(*self.docs)

        current_year = datetime.datetime.now().strftime("%Y")
        _, docs = self.solr_docs.page(search_term=current_year)

        self.assertEqual(len(docs), 4)

    def test_pagination_size_search(self):
        self.solr_docs.add(*self.docs)

        _, docs = self.solr_docs.page(search_term="8137")
        self.assertEqual(len(docs), 1)

    def test_doc_creation_date_changes_on_each_update(self):
        import time

        doc = self.docs[0]

        self.solr_docs.add(doc)
        doc_before = self.solr_docs.get(doc.id)

        time.sleep(5)

        self.solr_docs.update(doc)
        doc_after = self.solr_docs.get(doc.id)

        self.assertNotEqual(doc_before.creation_date, doc_after.creation_date)


if __name__ == "__main__":
    unittest.main()
