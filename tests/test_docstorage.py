from backend.solr import SolrDocStorage, SolrDoc, SolrDocKeyword, SolrDocKeywordTypes

import unittest
from pathlib import Path
import os


class DocStorageTestCase(unittest.TestCase):
    config = {
        "corename": "test_documents",
        # "url": "http://localhost:8983/solr/",
        "url": "http://ec2-3-86-180-141.compute-1.amazonaws.com:8983/solr",
        "always_commit": True,
    }

    def setUp(self):
        SOLR_DOCS.clear()
        # the id will be the full_path "__contains__" can only be checked with the full path
        # this path is a mimic of our ec2 setup
        base = f"{os.getcwd()}/tests/test_docstorage_files/test"
        self.doc_types = ["pdf", "txt", "pptx", "docx"]
        self.doc_paths = [f"{base}.{doc_type}" for doc_type in self.doc_types]
        self.docs = [SolrDoc(path) for path in self.doc_paths]

    def tearDown(self):
        SOLR_DOCS.clear()

    def test_pagination_sort_asc(self):
        SOLR_DOCS.add(*self.docs)

        expected_page1 = ["test.docx", "test.pdf"]
        _, docs = SOLR_DOCS.page(0, 2, "id", "asc")
        doc_ids = [doc.id for doc in docs]
        self.assertEqual(doc_ids, expected_page1)

        expected_page2 = ["test.pptx", "test.txt"]
        _, docs = SOLR_DOCS.page(1, 2, "id", "asc")
        doc_ids = [doc.id for doc in docs]
        self.assertEqual(doc_ids, expected_page2)

    def test_pagination_sort_desc(self):
        SOLR_DOCS.add(*self.docs)

        expected_page1 = ["test.txt", "test.pptx"]
        _, docs = SOLR_DOCS.page(0, 2, "id", "desc")
        doc_ids = [doc.id for doc in docs]
        self.assertEqual(doc_ids, expected_page1)

        expected_page2 = ["test.pdf", "test.docx"]
        _, docs = SOLR_DOCS.page(1, 2, "id", "desc")
        doc_ids = [doc.id for doc in docs]
        self.assertEqual(doc_ids, expected_page2)

    def test_total_num_pages(self):
        SOLR_DOCS.add(*self.docs)

        total_num_pages, _ = SOLR_DOCS.page(0, 1)
        self.assertEqual(total_num_pages, 4)

        total_num_pages, _ = SOLR_DOCS.page(0, 2)
        self.assertEqual(total_num_pages, 2)

        total_num_pages, _ = SOLR_DOCS.page(0, 3)
        self.assertEqual(total_num_pages, 2)

        total_num_pages, _ = SOLR_DOCS.page(0, 4)
        self.assertEqual(total_num_pages, 1)

    def test_pagination_sort_field_does_not_exist(self):
        with self.assertRaises(ValueError):
            SOLR_DOCS.page(0, 1, "not_existing_field", "asc")

    def test_add_and_search(self):
        SOLR_DOCS.add(*self.docs)

        added = SOLR_DOCS.search("*:*")
        self.assertEqual(len(added), len(self.docs))

    def test_delete(self):
        SOLR_DOCS.add(*self.docs)

        deleted = self.docs[0]

        SOLR_DOCS.delete(deleted.path)
        self.assertTrue(deleted.path not in SOLR_DOCS)

    def test_contains(self):
        SOLR_DOCS.add(*self.docs)

        for doc in self.docs:
            self.assertTrue(doc.path in SOLR_DOCS)

        not_existing = "/this/file/does/not/exist"
        self.assertTrue(not_existing not in SOLR_DOCS)

    def test_empty_keywords(self):
        doc = SolrDoc(self.doc_paths[0])
        SOLR_DOCS.add(doc)
        doc = SOLR_DOCS.get(doc.path)

        self.assertFalse(doc.keywords)

    def test_initial_keywords(self):
        kw1 = SolrDocKeyword("key1", SolrDocKeywordTypes.KWM)
        kw2 = SolrDocKeyword("key2", SolrDocKeywordTypes.KWM)

        doc = SolrDoc(self.doc_paths[0], kw1, kw2)
        SOLR_DOCS.add(doc)

        doc = SOLR_DOCS.get(doc.path)

        self.assertTrue(kw1 in doc.keywords)
        self.assertTrue(kw2 in doc.keywords)

    def test_update_keywords(self):
        kw1 = SolrDocKeyword("key1", SolrDocKeywordTypes.KWM)
        kw2 = SolrDocKeyword("key2", SolrDocKeywordTypes.KWM)
        kw3 = SolrDocKeyword("key3", SolrDocKeywordTypes.KWM)

        doc = SolrDoc(self.doc_paths[0], kw1, kw2)
        SOLR_DOCS.add(doc)

        doc = SOLR_DOCS.get(doc.path)
        doc.keywords.remove(kw1)
        doc.keywords.add(kw3)
        SOLR_DOCS.update(doc)

        doc = SOLR_DOCS.get(doc.path)
        self.assertTrue(kw1 not in doc.keywords)
        self.assertTrue(kw2 in doc.keywords)
        self.assertTrue(kw3 in doc.keywords)

    def test_correct_language_extraction(self):
        expected_lang = "en"

        # doc where tika can't parse the language
        doc = self.docs[3]
        SOLR_DOCS.add(doc)

        doc = SOLR_DOCS.get(doc.path)

        self.assertEqual(doc.lang, expected_lang)


SOLR_DOCS = SolrDocStorage(DocStorageTestCase.config)

if __name__ == "__main__":
    unittest.main()
