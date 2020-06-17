from backend.solr import (
    SolrKeywordModel,
    SolrKeywords,
    SolrHierarchy,
    SolrDoc,
    SolrDocKeyword,
    SolrDocKeywordTypes,
)
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


class TestKeywordModelApply(unittest.TestCase):
    def setUp(self):
        # fmt: off
        self.doc = SolrDoc(
            "path",
            title="title"
        )

        self.hierarchy = SolrHierarchy(
            name="name",
            hierarchy=[
                {
                    "item": "dim1",
                    "nodeType": "DIMENSION",
                    "children": [
                        {
                            "item": "key1",
                            "nodeType": "KEYWORD",
                            "children": [
                                {
                                    "item": "dim11",
                                    "nodeType": "DIMENSION",
                                    "children": [
                                        {
                                            "item": "key11",
                                            "nodeType": "KEYWORD"
                                        },
                                        {
                                            "item": "key12",
                                            "nodeType": "KEYWORD"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "item": "key2",
                            "nodeType": "KEYWORD",
                            "children": [
                                {
                                    "item": "dim21",
                                    "nodeType": "DIMENSION"
                                }
                            ]
                        }
                    ]
                }
            ]
        )
        # fmt: on

    def test_lowest_dimension_found(self):
        self.doc.content = "key11 and some other stuff"
        expected = [
            SolrDocKeyword("key1", SolrDocKeywordTypes.KWM),
            SolrDocKeyword("key11", SolrDocKeywordTypes.KWM),
        ]

        self.doc.apply_kwm(self.hierarchy.get_keywords())
        self.assertEqual(sorted(self.doc.keywords), sorted(expected))

    def test_above_lowest_dimension_found(self):
        self.doc.content = "key1 and some other stuff"
        expected = [SolrDocKeyword("key1", SolrDocKeywordTypes.KWM)]

        self.doc.apply_kwm(self.hierarchy.get_keywords())
        self.assertEqual(self.doc.keywords, expected)

    def test_everything_found(self):
        self.doc.content = "key1 key11 key12 key2 and some other stuff"
        expected = [
            SolrDocKeyword("key1", SolrDocKeywordTypes.KWM),
            SolrDocKeyword("key11", SolrDocKeywordTypes.KWM),
            SolrDocKeyword("key12", SolrDocKeywordTypes.KWM),
            SolrDocKeyword("key2", SolrDocKeywordTypes.KWM),
        ]

        self.doc.apply_kwm(self.hierarchy.get_keywords())
        self.assertEqual(sorted(self.doc.keywords), sorted(expected))

    def test_dimension_ignored(self):
        self.doc.content = "dim1 and some other stuff"
        expected = list()

        self.doc.apply_kwm(self.hierarchy.get_keywords())
        self.assertEqual(self.doc.keywords, expected)

    def test_no_duplicate_keywords(self):
        self.doc.keywords = [SolrDocKeyword("key1", SolrDocKeywordTypes.KWM)]
        self.doc.content = "key1 and some other stuff"

        self.doc.apply_kwm(self.hierarchy.get_keywords())
        self.assertEqual(len(self.doc.keywords), 1)


    def test_parsing(self):
        self.doc.content = "key1,key11;key12    key2/and some other stuff"
        expected = [
            SolrDocKeyword("key1", SolrDocKeywordTypes.KWM),
            SolrDocKeyword("key11", SolrDocKeywordTypes.KWM),
            SolrDocKeyword("key12", SolrDocKeywordTypes.KWM),
            SolrDocKeyword("key2", SolrDocKeywordTypes.KWM),
        ]

        self.doc.apply_kwm(self.hierarchy.get_keywords())
        self.assertEqual(sorted(self.doc.keywords), sorted(expected))

if __name__ == "__main__":
    unittest.main()
