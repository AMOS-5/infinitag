from backend.solr import SolrKeywordModel, SolrKeywords, SolrHierarchy

import unittest
import time

test_config_keywords = {
    "corename": "test_keywords",
    # "url": "http://localhost:8983/solr/",
    "url": "http://ec2-52-87-180-131.compute-1.amazonaws.com:8983/solr/",
    "always_commit": True,
}
test_config_keyword_model = {
    "corename": "test_keyword_model",
    # "url": "http://localhost:8983/solr/",
    "url": "http://ec2-52-87-180-131.compute-1.amazonaws.com:8983/solr/",
    "always_commit": True,
}

SOLR_KEYWORDS = SolrKeywords(test_config_keywords)
SOLR_KEYWORD_MODEL = SolrKeywordModel(test_config_keyword_model)


class TestKeywords(unittest.TestCase):
    def setUp(self):
        SOLR_KEYWORDS.clear()

    def tearDown(self):
        SOLR_KEYWORDS.clear()

    def test_add_and_clear(self):
        SOLR_KEYWORDS.add("keyword1", "keyword2")

        added = SOLR_KEYWORDS.get()
        self.assertTrue("keyword1" in added)
        self.assertTrue("keyword2" in added)

        SOLR_KEYWORDS.clear()
        self.assertEqual(len(SOLR_KEYWORDS.get()), 0)

    def test_uniqueness(self):
        SOLR_KEYWORDS.add("keyword1", "keyword1", "keyword1")
        SOLR_KEYWORDS.add("keyword1")

        added = SOLR_KEYWORDS.get()
        self.assertEqual(len(added), 1)
        self.assertTrue("keyword1" in added)

    def test_contains(self):
        SOLR_KEYWORDS.add("keyword1")

        self.assertTrue("keyword1" in SOLR_KEYWORDS)
        self.assertTrue("keyword2" not in SOLR_KEYWORDS)

    def test_delete(self):
        SOLR_KEYWORDS.add("keyword1", "keyword2")
        SOLR_KEYWORDS.delete("keyword1")

        keywords = SOLR_KEYWORDS.get()
        self.assertEqual(len(keywords), 1)
        self.assertTrue("keyword2" in keywords)

    def test_huge_keyword_amount(self):
        keywords = [f"keyword{i}" for i in range(5000)]
        SOLR_KEYWORDS.add(*keywords)

        time.sleep(3)  # give solr some time to process

        added = SOLR_KEYWORDS.get()
        self.assertEqual(len(added), 5000)


class TestKeywordModelHierarchy(unittest.TestCase):
    def setUp(self):
        SOLR_KEYWORD_MODEL.clear()

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
        SOLR_KEYWORD_MODEL.clear()

    def test_add_hierarchies(self):
        SOLR_KEYWORD_MODEL.add(self.country_hierarchy)
        self.assertTrue(self.country_hierarchy.name in SOLR_KEYWORD_MODEL)

    def test_get_hierarchy(self):
        SOLR_KEYWORD_MODEL.add(self.country_hierarchy)
        country_hierarchy = SOLR_KEYWORD_MODEL.get()[0]

        self.assertEqual(country_hierarchy.name, self.country_hierarchy.name)
        self.assertEqual(country_hierarchy.hierarchy, self.country_hierarchy.hierarchy)

    def test_update_hierarchy(self):
        SOLR_KEYWORD_MODEL.add(self.country_hierarchy)
        country_hierarchy = SOLR_KEYWORD_MODEL.get()[0]

        # add another city
        germany = country_hierarchy["germany"]
        germany["states"].append("berlin")
        SOLR_KEYWORD_MODEL.update(country_hierarchy)

        # requery and check whether we updated
        country_hierarchy = SOLR_KEYWORD_MODEL.get()[0]
        germany = country_hierarchy["germany"]
        self.assertTrue("berlin" in germany["states"])


if __name__ == "__main__":
    unittest.main()
