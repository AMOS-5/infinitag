from backend.solr import SolrDocStorage, SolrDoc, SolrDocKeyword, SolrDocKeywordTypes

import unittest
from pathlib import Path
import os


class DocStorageTestCase(unittest.TestCase):
    config = {
        "corename": "test_documents",
        # "url": "http://localhost:8983/solr/",
        "url": "http://ec2-52-87-180-131.compute-1.amazonaws.com:8983/solr",
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
        doc.keywords.append(kw3)
        SOLR_DOCS.update(doc)

        doc = SOLR_DOCS.get(doc.path)
        self.assertTrue(kw1 not in doc.keywords)
        self.assertTrue(kw2 in doc.keywords)
        self.assertTrue(kw3 in doc.keywords)


SOLR_DOCS = SolrDocStorage(DocStorageTestCase.config)

if __name__ == "__main__":
    unittest.main()
