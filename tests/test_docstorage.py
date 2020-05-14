from backend.docstorage import SolrDocStorage

import unittest
from pathlib import Path


class DocStorageTestCase(unittest.TestCase):
    """
    IMPORTANT:

    The testfiles depend on our filestorage. As filestorage we use on our EC2 instance
    ~/filestorage/docstorage_test. If you want to run the tests locally, you have to add the testfiles
    to ~/filestorage/docstorage_test on Linux/Mac. For Windows it depends what 'Path.home()' returns
    for you.
    """

    config = {
        "corename": "test_documents",
        # can safely be set when our test runs in deployment
        "url": "http://localhost:8983/solr/",
        # "url": "http://ec2-52-205-45-244.compute-1.amazonaws.com:8983/solr",
        "always_commit": True,
        "debug": False,
    }

    def setUp(self):
        # the id will be the full_path "__contains__" can only be checked with the full path
        # this path is a mimic of our ec2 setup
        base = f"{Path.home()}/filestorage/docstorage_test/test"
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

        added = SOLR_DOCS.search("*:*")

        deleted = self.docs[0]

        SOLR_DOCS.delete(deleted)
        self.assertTrue(deleted not in SOLR_DOCS)

    def test_contains(self):
        SOLR_DOCS.add(*self.docs)

        added = SOLR_DOCS.search("*:*")
        for doc in self.docs:
            self.assertTrue(doc in SOLR_DOCS)

        SOLR_DOCS.clear()

        not_existing = "this_file_does_not_exist"
        self.assertTrue(not_existing not in SOLR_DOCS)



# database connection & pipe for the testcases
SOLR_DOCS = SolrDocStorage(DocStorageTestCase.config)
SOLR_DOCS.clear()

if __name__ == "__main__":
    unittest.main()
