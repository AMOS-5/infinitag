from backend.docstorage import SolrDocStorage

import unittest
from pathlib import Path
import os

class DocStorageTestCase(unittest.TestCase):
    """
    IMPORTANT:

    To run this tests you have to:
    1. Install Solr
    2. export SOLR_ROOT=PATH/TO/YOUR/SOLR/INSTALLATION
    """

    config = {
        "corename": "test_documents",
        # "url": "http://localhost:8983/solr/",
        "url": "http://ec2-52-87-180-131.compute-1.amazonaws.com:8983/solr",
        "always_commit": True,
        "debug": False,
    }

    def setUp(self):
        # the id will be the full_path "__contains__" can only be checked with the full path
        # this path is a mimic of our ec2 setup
        base = f"{os.getcwd()}/tests/test_docstorage_files/test"
        self.doc_types = ["pdf", "txt", "pptx", "docx"]
        self.docs = [f"{base}.{doc_type}" for doc_type in self.doc_types]

    def tearDown(self):
        SOLR_DOCS.clear()

    def test_add_and_search(self):
        SOLR_DOCS.add(*self.docs)

        added = SOLR_DOCS.search("*:*")
        self.assertEqual(len(added), len(self.docs))

    def test_delete(self):
        SOLR_DOCS.add(*self.docs)

        deleted = self.docs[0]

        SOLR_DOCS.delete(deleted)
        self.assertTrue(deleted not in SOLR_DOCS)

    def test_contains(self):
        SOLR_DOCS.add(*self.docs)

        for doc in self.docs:
            self.assertTrue(doc in SOLR_DOCS)

        not_existing = "this_file_does_not_exist"
        self.assertTrue(not_existing not in SOLR_DOCS)



# database connection & pipe for the testcases
SOLR_DOCS = SolrDocStorage(DocStorageTestCase.config)
SOLR_DOCS.clear()

if __name__ == "__main__":
    unittest.main()
