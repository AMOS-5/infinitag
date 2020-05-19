from backend.tagstorage import SolrTagStorage

import unittest


class TagStorageTestCase(unittest.TestCase):
    config = {
        "field": "tag",
        "corename": "test_tags",
        # "url": "http://localhost:8983/solr/",
        "url": "http://ec2-52-87-180-131.compute-1.amazonaws.com:8983/solr/",
        "always_commit": True,
    }

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


# database connection for the testcases
SOLR_TAGS = SolrTagStorage(TagStorageTestCase.config)

if __name__ == "__main__":
    unittest.main()
