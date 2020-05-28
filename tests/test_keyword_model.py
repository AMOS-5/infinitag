from backend.solr import SolrKeywordModel, SolrHierarchy

import unittest
import time

test_config = {
    "corename": "test_keyword_model",
    # "url": "http://localhost:8983/solr/",
    "url": "http://ec2-52-87-180-131.compute-1.amazonaws.com:8983/solr/",
    "always_commit": True,
}


class TestKeywordModelTags(unittest.TestCase):
    def setUp(self):
        SOLR_KEYWORDS.clear()

    def tearDown(self):
        SOLR_KEYWORDS.clear()

    def test_add_and_clear(self):
        SOLR_KEYWORDS.add_tags("tag1", "tag2")

        added = SOLR_KEYWORDS.tags
        self.assertTrue("tag1" in added)
        self.assertTrue("tag2" in added)

        SOLR_KEYWORDS.clear()
        self.assertEqual(len(SOLR_KEYWORDS.tags), 0)

    def test_uniqueness(self):
        SOLR_KEYWORDS.add_tags("tag1", "tag1", "tag1")
        SOLR_KEYWORDS.add_tags("tag1")

        added = SOLR_KEYWORDS.tags
        self.assertEqual(len(added), 1)
        self.assertTrue("tag1" in added)

    def test_contains(self):
        SOLR_KEYWORDS.add_tags("tag1")

        self.assertTrue("tag1" in SOLR_KEYWORDS)
        self.assertTrue("tag2" not in SOLR_KEYWORDS)

    def test_delete(self):
        SOLR_KEYWORDS.add_tags("tag1", "tag2")
        SOLR_KEYWORDS.delete_tags("tag1")

        tags = SOLR_KEYWORDS.tags
        self.assertEqual(len(tags), 1)
        self.assertTrue("tag2" in tags)

    def test_huge_tag_amount(self):
        tags = [f"tag{i}" for i in range(5000)]
        SOLR_KEYWORDS.add_tags(*tags)

        time.sleep(3)  # give solr some time to process

        added = SOLR_KEYWORDS.tags
        self.assertEqual(len(added), 5000)


class TestKeywordModelHierarchy(unittest.TestCase):
    def setUp(self):
        SOLR_KEYWORDS.clear()

        # fmt: off
        self.country_hierarchy = SolrHierarchy(
            name="country",
            hierarchy={
                "germany": {
                    "states": [
                        "bavaria",
                        "badenwürtemberg"
                    ]
                },
                "uk": {
                    "states": [
                        "scotland",
                        "wales"
                    ]
                },
            },
        )
        # fmt: on

    def tearDown(self):
        SOLR_KEYWORDS.clear()

    def test_add_hierarchies(self):
        SOLR_KEYWORDS.add_hierarchies(self.country_hierarchy)
        self.assertTrue(self.country_hierarchy.name in SOLR_KEYWORDS)

    def test_get_hierarchy(self):
        SOLR_KEYWORDS.add_hierarchies(self.country_hierarchy)
        country_hierarchy = SOLR_KEYWORDS.hierarchies[0]

        self.assertEqual(country_hierarchy.name, self.country_hierarchy.name)
        self.assertEqual(country_hierarchy.hierarchy, self.country_hierarchy.hierarchy)

    def test_update_hierarchy(self):
        SOLR_KEYWORDS.add_hierarchies(self.country_hierarchy)
        country_hierarchy = SOLR_KEYWORDS.hierarchies[0]

        # add another city
        germany = country_hierarchy["germany"]
        germany["states"].append("berlin")
        SOLR_KEYWORDS.update_hierarchies(country_hierarchy)

        # requery and check whether we updated
        country_hierarchy = SOLR_KEYWORDS.hierarchies[0]
        germany = country_hierarchy["germany"]
        self.assertTrue("berlin" in germany["states"])


# database connection for the testcases
SOLR_KEYWORDS = SolrKeywordModel(test_config)

if __name__ == "__main__":
    unittest.main()
