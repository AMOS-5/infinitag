import pytest
import unittest
from unittest.mock import patch

from pathlib import Path
import logging as log
import json
import io
import datetime as dt
from datetime import datetime, timedelta

log.basicConfig(level=log.ERROR)

from backend.solr import (
    SolrDoc,
    SolrDocKeyword,
    SolrDocKeywordTypes,
    SolrDocStatistics,
    DocStatistics,
)

POST_MULTIPART = {"content_type": "multipart/form-data", "follow_redirects": True}
POST_JSON = {"content_type": "application/json"}

BASE_PATH = Path("tests/test_docstorage_files")


def doc_from_id(doc_id):
    with open(str(BASE_PATH / doc_id), "rb") as f:
        return {"fileKey": (io.BytesIO(f.read()), doc_id), "fid": "fid"}


def upload_doc(client, doc):
    client.post("/upload", data=doc, **POST_MULTIPART)


@pytest.fixture
def client():
    from app import app as flask_app

    test_client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()
    yield test_client
    ctx.pop()


@pytest.fixture
def doc_with_meta_keywords(client):
    doc_id = "test_with_meta_keywords.pdf"
    doc = doc_from_id(doc_id)
    upload_doc(client, doc)
    return doc_id


@pytest.fixture
def doc_with_2_keywords(doc_with_meta_keywords):
    return doc_with_meta_keywords


@pytest.fixture
def example_doc(doc_with_meta_keywords):
    return example_doc


@pytest.fixture
def doc_with_0_keywords_1(client):
    doc_id = "test.pdf"
    doc = doc_from_id(doc_id)
    upload_doc(client, doc)
    return doc_id


@pytest.fixture
def doc_with_0_keywords_2(client):
    doc_id = "test.docx"
    doc = doc_from_id(doc_id)
    upload_doc(client, doc)
    return doc_id


@pytest.fixture
def doc1_has_kw1(doc_with_meta_keywords):
    return doc_with_meta_keywords


@pytest.fixture
def doc2_has_kw1(client, doc_with_0_keywords_1, solr_docs):
    doc2 = solr_docs.get(doc_with_0_keywords_1)
    doc2.keywords.add(SolrDocKeyword("keyword1", SolrDocKeywordTypes.MANUAL))
    client.patch("/changekeywords", data=json.dumps(doc2.as_dict()), **POST_JSON)
    return doc2.id


@pytest.fixture
def num_keywordmodels_2(solr_keyword_model):
    solr_keyword_model.con.add({"id": "id1"})
    solr_keyword_model.con.add({"id": "id2"})


@pytest.fixture
def solr_doc_statistics(solr_docs):
    return SolrDocStatistics(solr_docs)


def push_docs_in_interval(solr_docs, solr_doc_statistics, docs_per_interval, dates):
    for docs_this_interval, date in zip(docs_per_interval, dates):
        creation_date = date + timedelta(hours=1)
        solr_docs.con.add(
            [
                {
                    "id": f"name{docs_this_interval}{id}",
                    "creation_date": solr_doc_statistics._time_to_solr(creation_date),
                }
                for id in range(docs_this_interval)
            ]
        )


@pytest.fixture
def docs_for_last_7_days(solr_docs, solr_doc_statistics):
    now = datetime.utcnow()
    prev = now
    dates = [now]
    dates.extend(prev - timedelta(days=days) for days in range(1, 7))

    docs_per_day = [1, 2, 3, 4, 5, 6, 7]
    push_docs_in_interval(solr_docs, solr_doc_statistics, docs_per_day, reversed(dates))


@pytest.fixture
def docs_for_last_4_weeks(solr_docs, solr_doc_statistics):
    now = datetime.utcnow()
    weekday = dt.date.today().weekday()
    prev_monday = solr_doc_statistics._reset_hours(now - timedelta(days=weekday))
    dates = [now, prev_monday]
    dates.extend(prev_monday - timedelta(weeks=weeks) for weeks in range(1, 4))

    docs_per_week = [1, 2, 3, 4]
    push_docs_in_interval(
        solr_docs, solr_doc_statistics, docs_per_week, reversed(dates)
    )


@pytest.fixture
def docs_for_this_year(solr_docs, solr_doc_statistics):
    # patch utcnow such the we can test whether unquerried months
    # are correctly returned with 0's
    solr_doc_statistics._now = lambda: datetime(2020, 11, 2, 0, 0, 0)

    dates = [datetime(2020, month, 1, 0, 0, 0) for month in range(1, 12)]

    docs_per_month = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] # 0 will be added
    push_docs_in_interval(solr_docs, solr_doc_statistics, docs_per_month, dates)


@pytest.fixture
def docs_for_last_2_years(solr_docs, solr_doc_statistics):
    # patch utcnow to be in year 2021 hence include docs from 2021 and 2020
    solr_doc_statistics._now = lambda: datetime(2021, 3, 1, 0, 0, 0)

    dates = [datetime(2020, 2, 1, 0, 0, 0), datetime(2021, 2, 1, 0, 0, 0)]
    docs_per_year = [1, 2]
    push_docs_in_interval(solr_docs, solr_doc_statistics, docs_per_year, dates)


@pytest.mark.usefixtures("app_fixture")
class TestStatistics:
    def test_meta_keywords_added_on_upload(self, doc_with_meta_keywords):
        assert "keyword1" in self.solr_keyword_statistics
        assert "keyword2" in self.solr_keyword_statistics

    def test_keyword_added(self, client, doc_with_meta_keywords):
        doc = self.solr_docs.get(doc_with_meta_keywords)
        doc.keywords.add(SolrDocKeyword("keyword3", SolrDocKeywordTypes.MANUAL))

        client.patch("/changekeywords", data=json.dumps(doc.as_dict()), **POST_JSON)

        assert "keyword3" in self.solr_keyword_statistics

    def test_keyword_deleted(self, client, doc_with_2_keywords):
        doc = self.solr_docs.get(doc_with_2_keywords)
        doc.keywords.remove(SolrDocKeyword("keyword2", SolrDocKeywordTypes.META))

        client.patch("/changekeywords", data=json.dumps(doc.as_dict()), **POST_JSON)

        assert "keyword1" in self.solr_keyword_statistics
        assert "keyword2" not in self.solr_keyword_statistics

    def test_keyword_added_and_deleted(self, client, doc_with_2_keywords):
        doc = self.solr_docs.get(doc_with_2_keywords)
        doc.keywords.add(SolrDocKeyword("keyword3", SolrDocKeywordTypes.MANUAL))
        doc.keywords.remove(SolrDocKeyword("keyword2", SolrDocKeywordTypes.META))

        client.patch("/changekeywords", data=json.dumps(doc.as_dict()), **POST_JSON)

        assert "keyword1" in self.solr_keyword_statistics
        assert "keyword2" not in self.solr_keyword_statistics
        assert "keyword3" in self.solr_keyword_statistics

    def test_keyword_deleted_but_keyword_still_attached_to_another_doc(
        self, client, doc1_has_kw1, doc2_has_kw1
    ):
        # setup: 2 documents with the same keyword
        # idea: when the keyword gets deleted from one document it should still persist
        # in the statistics core
        doc = self.solr_docs.get(doc1_has_kw1)
        doc.keywords = set()
        client.patch("/changekeywords", data=json.dumps(doc.as_dict()), **POST_JSON)

        assert "keyword1" in self.solr_keyword_statistics

    def test_docs_in_last_7_days(self, solr_doc_statistics, docs_for_last_7_days):
        docs_stats = solr_doc_statistics._last_7_days()
        for docs_per_day, expected_docs_per_day in zip(docs_stats, range(1, 7)):
            assert docs_per_day == expected_docs_per_day

    def test_docs_in_last_4_weeks(self, solr_doc_statistics, docs_for_last_4_weeks):
        docs_stats = solr_doc_statistics._last_4_weeks()
        for docs_per_week, expected_docs_per_week in zip(docs_stats, range(1, 5)):
            assert docs_per_week == expected_docs_per_week

    def test_docs_in_this_year(self, solr_doc_statistics, docs_for_this_year):
        docs_stats = solr_doc_statistics._this_year()

        for docs_per_month, expected_docs_per_month in zip(
            docs_stats[:-1], range(1, 12)
        ):
            assert docs_per_month == expected_docs_per_month

        # unquerried month got correctly added
        assert docs_stats[-1] == 0

    def test_docs_in_all_years(self, solr_doc_statistics, docs_for_last_2_years):
        docs_stats = solr_doc_statistics._all_years()
        for docs_per_year, expected_docs_per_year in zip(docs_stats, [1, 2]):
            assert docs_per_year == expected_docs_per_year

    def test_statistics(
        self,
        client,
        doc_with_2_keywords,
        doc_with_0_keywords_1,
        doc_with_0_keywords_2,
        num_keywordmodels_2,
    ):
        res = client.get("/statistics", **POST_JSON)
        data = json.loads(res.data)

        assert res.status_code == 200
        assert data["n_total_docs"] == 3
        assert data["n_tagged_docs"] == 1
        assert data["n_untagged_docs"] == 2
        assert data["n_keywords"] == 2
        assert data["n_keyword_models"] == 2

