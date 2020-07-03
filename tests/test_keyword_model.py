import pytest
import unittest
import time
import os

from backend.solr import (
    SolrKeywordModel,
    SolrKeywords,
    SolrHierarchy,
    SolrDocStorage,
    SolrDoc,
    SolrDocKeyword,
    SolrDocKeywordTypes,
)


@pytest.mark.usefixtures("solr_keywords")
class TestKeywords(unittest.TestCase):
    def test_add_and_clear(self):
        self.solr_keywords.add("keyword1", "keyword2")

        added = self.solr_keywords.get()
        self.assertTrue("keyword1" in added)
        self.assertTrue("keyword2" in added)

        self.solr_keywords.clear()
        self.assertEqual(len(self.solr_keywords.get()), 0)

    def test_uniqueness(self):
        self.solr_keywords.add("keyword1", "keyword1", "keyword1")
        self.solr_keywords.add("keyword1")

        added = self.solr_keywords.get()
        self.assertEqual(len(added), 1)
        self.assertTrue("keyword1" in added)

    def test_contains(self):
        self.solr_keywords.add("keyword1")

        self.assertTrue("keyword1" in self.solr_keywords)
        self.assertTrue("keyword2" not in self.solr_keywords)

    def test_delete(self):
        self.solr_keywords.add("keyword1", "keyword2")
        self.solr_keywords.delete("keyword1")

        keywords = self.solr_keywords.get()
        self.assertEqual(len(keywords), 1)
        self.assertTrue("keyword2" in keywords)

    def test_huge_keyword_amount(self):
        keywords = [f"keyword{i}" for i in range(5000)]
        self.solr_keywords.add(*keywords)

        time.sleep(3)  # give solr some time to process

        added = self.solr_keywords.get()
        self.assertEqual(len(added), 5000)


@pytest.mark.usefixtures("solr_keyword_model")
class TestKeywordModelHierarchy(unittest.TestCase):
    def setUp(self):
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
            keywords=["germany", "uk", "bavaria", "badenwürtemberg", "scotland", "wales"]
        )
        # fmt: on

    def test_add_hierarchy(self):
        self.solr_keyword_model.add(self.country_hierarchy)
        self.assertTrue(self.country_hierarchy.name in self.solr_keyword_model)

    def test_get_hierarchy(self):
        self.solr_keyword_model.add(self.country_hierarchy)
        country_hierarchy = self.solr_keyword_model.get()[0]

        self.assertEqual(country_hierarchy.name, self.country_hierarchy.name)
        self.assertEqual(country_hierarchy.hierarchy, self.country_hierarchy.hierarchy)

    def test_update_hierarchy(self):
        self.solr_keyword_model.add(self.country_hierarchy)
        country_hierarchy = self.solr_keyword_model.get()[0]

        # add another city
        germany = country_hierarchy["germany"]
        germany["states"].append("berlin")
        self.solr_keyword_model.update(country_hierarchy)

        # requery and check whether we updated
        country_hierarchy = self.solr_keyword_model.get()[0]
        germany = country_hierarchy["germany"]
        self.assertTrue("berlin" in germany["states"])


@pytest.mark.usefixtures("solr_docs")
class TestKeywordModelApply(unittest.TestCase):
    def setUp(self):
        # fmt: off
        self.doc = SolrDoc(
            f"{os.getcwd()}/path.txt",
            title="title",
            file_type="txt",
            lang="en",
            size=3,
            creation_date="2019-06-14T12:05:00Z",
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
            ],
            keywords=["key1", "key11", "key12", "key2"]
        )
        # fmt: on

    def test_lowest_dimension_found(self):
        self.doc.content = "key11 and some other stuff"
        self.solr_docs.update(self.doc)

        expected = [
            SolrDocKeyword("key1", SolrDocKeywordTypes.KWM),
            SolrDocKeyword("key11", SolrDocKeywordTypes.KWM),
        ]

        self.solr_docs.apply_kwm(self.hierarchy.get_keywords())

        self.doc = self.solr_docs.get(self.doc.id)
        self.assertEqual(sorted(self.doc.keywords), sorted(expected))

    def test_above_lowest_dimension_found(self):
        self.doc.content = "key1 and some other stuff"
        self.solr_docs.update(self.doc)

        expected = [SolrDocKeyword("key1", SolrDocKeywordTypes.KWM)]

        self.solr_docs.apply_kwm(self.hierarchy.get_keywords())

        self.doc = self.solr_docs.get(self.doc.id)
        self.assertEqual(list(self.doc.keywords), expected)

    def test_everything_found(self):
        self.doc.content = "key1 key11 key12 key2 and some other stuff"
        self.solr_docs.update(self.doc)

        expected = [
            SolrDocKeyword("key1", SolrDocKeywordTypes.KWM),
            SolrDocKeyword("key11", SolrDocKeywordTypes.KWM),
            SolrDocKeyword("key12", SolrDocKeywordTypes.KWM),
            SolrDocKeyword("key2", SolrDocKeywordTypes.KWM),
        ]

        self.solr_docs.apply_kwm(self.hierarchy.get_keywords())

        self.doc = self.solr_docs.get(self.doc.id)
        self.assertEqual(sorted(self.doc.keywords), sorted(expected))

    def test_dimension_ignored(self):
        self.doc.content = "dim1 and some other stuff"
        self.solr_docs.update(self.doc)

        expected = set()

        self.solr_docs.apply_kwm(self.hierarchy.get_keywords())

        self.doc = self.solr_docs.get(self.doc.id)
        self.assertEqual(self.doc.keywords, expected)

    def test_no_duplicate_keywords(self):
        self.doc.keywords = [SolrDocKeyword("key1", SolrDocKeywordTypes.KWM)]
        self.doc.content = "key1 and some other stuff"
        self.solr_docs.update(self.doc)

        self.solr_docs.apply_kwm(self.hierarchy.get_keywords())

        self.doc = self.solr_docs.get(self.doc.id)
        self.assertEqual(len(self.doc.keywords), 1)


if __name__ == "__main__":
    unittest.main()
