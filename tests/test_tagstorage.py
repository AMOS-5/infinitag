from backend.solr import SolrTagStorage

import unittest
import time

class TagStorageTestCase(unittest.TestCase):
    config = {
        "corename": "test_tags",
        # "url": "http://localhost:8983/solr/",
        "url": "http://ec2-52-87-180-131.compute-1.amazonaws.com:8983/solr/",
        "always_commit": True,
    }

    def setUp(self):
        SOLR_TAGS.clear()

    def tearDown(self):
        SOLR_TAGS.clear()

    def test_add_and_clear(self):
        SOLR_TAGS.add("tag1", "tag2")

        added = SOLR_TAGS.tags
        self.assertTrue("tag1" in added)
        self.assertTrue("tag2" in added)

        SOLR_TAGS.clear()
        self.assertEqual(len(SOLR_TAGS.tags), 0)

    def test_uniqueness(self):
        SOLR_TAGS.add("tag1", "tag1", "tag1")
        SOLR_TAGS.add("tag1")

        added = SOLR_TAGS.tags
        self.assertEqual(len(added), 1)
        self.assertTrue("tag1" in added)

    def test_contains(self):
        SOLR_TAGS.add("tag1")

        self.assertTrue("tag1" in SOLR_TAGS)
        self.assertTrue("tag2" not in SOLR_TAGS)

    def test_delete(self):
        SOLR_TAGS.add("tag1", "tag2")
        SOLR_TAGS.delete("tag1")

        tags = SOLR_TAGS.tags
        self.assertEqual(len(tags), 1)
        self.assertTrue("tag2" in tags)

    def test_huge_tag_amount(self):
        tags = [f"tag{i}" for i in range(5000)]
        SOLR_TAGS.add(*tags)

        time.sleep(3) # give solr some time to process

        added = SOLR_TAGS.tags
        self.assertEqual(len(added), 5000)

# database connection for the testcases
SOLR_TAGS = SolrTagStorage(TagStorageTestCase.config)

if __name__ == "__main__":
    unittest.main()
