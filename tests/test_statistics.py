import pytest
import unittest
from pathlib import Path
import logging as log
import json
import io

log.basicConfig(level=log.ERROR)

from backend.solr import SolrDoc, SolrDocKeyword, SolrDocKeywordTypes

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

