import pytest
import unittest
import json
import io
import os
from time import sleep

from werkzeug.datastructures import FileStorage
from flask_jsonpify import jsonify
import zipfile

from backend.solr import SolrDoc, SolrHierarchy, SolrDocKeyword, SolrDocKeywordTypes

@pytest.mark.usefixtures("app_fixture")
class TestController(unittest.TestCase):
    def setUp(self):
        from app import app
        self.app = app
        # the id will be the full_path "__contains__" can only be checked with the full path
        # this path is a mimic of our ec2 setup
        self.base = f"{os.getcwd()}/tests/test_files/test"
        self.doc_types = ["pdf", "txt", "pptx", "docx"]
        self.doc_paths = [f"{self.base}.{doc_type}" for doc_type in self.doc_types]
        self.docs = [SolrDoc(path) for path in self.doc_paths]

    def test_home(self):
        tester = self.app.test_client(self)
        response = tester.get("/", content_type="html/text")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"Hello World!")

    def test_health(self):
        tester = self.app.test_client(self)
        response = tester.get("/health", content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data_response = json.loads(response.data)
        health = data_response["status"]
        self.assertEqual(health, "UP")

    def test_upload_file(self):
        doc_path = "tmp/test_upload.test"

        # delete file if it already exists
        if os.path.exists(doc_path):
            os.remove(doc_path)
        self.assertFalse(os.path.exists(doc_path))

        tester = self.app.test_client(self)
        # send test file
        data = {
            'fileKey': (io.BytesIO(b"some random words"), "test_upload.test"),
            'fid': 'fid'
        }

        response = tester.post(
            "/upload",
            content_type="multipart/form-data",
            data=data,
            follow_redirects=True,
        )
        # check status code
        self.assertEqual(response.status_code, 200)
        # check file
        self.assertTrue(os.path.exists(doc_path))
        f = open(doc_path, "r")
        content = f.read()
        f.close()
        self.assertEqual(content, "some random words")

        # file got uploaded to solr?
        solr_doc_id = "test_upload.test"
        self.assertTrue(solr_doc_id in self.application.solr.docs)

        # cleanup
        if os.path.exists(doc_path):
            os.remove(doc_path)

    def test_download_file(self):
        file = open("tmp/test1.txt", "w")
        file.write("abc")
        file.close()

        tester = self.app.test_client(self)
        response = tester.post(
            "/download",
            data=json.dumps([{"id": "test1.txt"}]),
            content_type='application/json',
        )
        # check status code
        self.assertEqual(response.status_code, 200)

        #check file
        file = open("tmp/test1.txt", "rb")
        file.seek(0)
        self.assertEqual(response.data, file.read())
        file.close()

    def test_download_multiple_files(self):
        file = open("tmp/test1.txt", "w")
        file.write("abc")
        file.close()

        file = open("tmp/test2.txt", "w")
        file.write("def")
        file.close()

        tester = self.app.test_client(self)
        response = tester.post(
            "/download",
            data=json.dumps([{"id": "test1.txt"}, {"id": "test2.txt"}]),
            content_type='application/json',
        )
        # check status code
        self.assertEqual(response.status_code, 200)

        #check files
        zip = zipfile.ZipFile(io.BytesIO(response.data))
        test1_file = zip.open('documents/test1.txt')
        self.assertEqual(test1_file.read(), b"abc")
        test2_file = zip.open('documents/test2.txt')
        self.assertEqual(test2_file.read(), b"def")

    def test_change_keywords(self):
        self.application.solr.docs.add(self.docs[0])
        id = self.docs[0].id

        doc = self.application.solr.docs.get(id)
        self.assertEqual(doc.keywords, set())

        tester = self.app.test_client(self)
        data=json.dumps({
            "id":id,
            "keywords": [
                {"value": "a", "type": "MANUAL"},
                {"value": "b", "type": "MANUAL"},
                {"value": "c", "type": "MANUAL"}
            ],
        })
        response=tester.patch('/changekeywords', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        doc = self.application.solr.docs.get(id)
        self.assertEqual(doc.keywords, {SolrDocKeyword(kw, SolrDocKeywordTypes.MANUAL) for kw in ["a", "b", "c"]})

    def test_documents(self):
        self.application.solr.docs.add(*self.docs)
        tester = self.app.test_client(self)
        response = tester.get("/documents", content_type="application/json")
        self.assertEqual(response.status_code, 200)

        data_response = json.loads(response.data)
        self.assertIsNotNone(data_response)
        self.assertEqual(len(data_response["docs"]), len(self.docs))

    def test_dimensions(self):
        tester = self.app.test_client(self)
        data=json.dumps(dict(
            dim="test"
        ))
        response = tester.post("/dims", content_type="application/json", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.application.solr.dimensions.get()), 1)

        response = tester.get("/dims", content_type="application/json")
        self.assertEqual(response.status_code, 200)

        data_response = json.loads(response.data)
        self.assertIsNotNone(data_response)
        self.assertEqual(data_response, ["test"])

    def test_remove_dimension(self):
        tester = self.app.test_client(self)

        self.application.solr.dimensions.add("a", "b", "c")
        response = tester.delete("/dims/b")
        self.assertEqual(response.status_code, 200)

        dims = self.application.solr.dimensions.get()
        self.assertEqual(dims, ["a", "c"])

    def test_keywords(self):
        tester = self.app.test_client(self)
        data=json.dumps(dict(
            key="test"
        ))
        response = tester.post("/keys", content_type="application/json", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.application.solr.keywords.get()), 1)

        response = tester.get("/keys", content_type="application/json")
        self.assertEqual(response.status_code, 200)

        data_response = json.loads(response.data)
        self.assertIsNotNone(data_response)
        self.assertEqual(data_response, ["test"])

    def test_remove_keyword(self):
        tester = self.app.test_client(self)

        self.application.solr.keywords.add("a", "b", "c")
        response = tester.delete("/keys/b")
        self.assertEqual(response.status_code, 200)

        keys = self.application.solr.keywords.get()
        self.assertEqual(keys, ["a", "c"])

    def test_keywordmodels(self):
        tester = self.app.test_client(self)
        data=json.dumps(dict(
            id="test",
            hierarchy=[],
            keywords=[]
        ))
        response = tester.post("/models", content_type="application/json", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.application.solr.keywordmodel.get()), 1)

        response = tester.get("/models", content_type="application/json")
        self.assertEqual(response.status_code, 200)

        data_response = json.loads(response.data)
        self.assertIsNotNone(data_response)
        self.assertEqual(data_response, [{"id": "test", "hierarchy": "[]", "keywords": []}])

    def test_remove_keywordmodel(self):
        tester = self.app.test_client(self)
        list = [None]*3
        for i in range(0, 3):
            list[i] = SolrHierarchy(str(i), [], [])
            self.application.solr.keywordmodel.add(list[i])

        response = tester.delete("/models/1")
        self.assertEqual(response.status_code, 200)

        del list[1]

        models = self.application.solr.keywordmodel.get()
        self.assertEqual(len(models), len(list))
        for i in range(0, len(models)):
            self.assertEqual(models[i].name, list[i].name)

    def test_apply_tagging_method_kwm(self):
        data = json.dumps(dict(
            taggingMethod={'name': 'Keyword Model', 'type': 'KWM'},
            keywordModel={  'id': 'test',
                            'hierarchy': json.dumps([
                                {'item': 'test', 'nodeType': 'KEYWORD'},
                                {'item': 'text', 'nodeType': 'KEYWORD'},
                                {'item': 'faufm', 'nodeType': 'KEYWORD'},
                                ]),
                            'keywords': ['test', 'text', 'faufm'],
                         },
            documents=[{'id': "test.txt"}, {'id':"test.pdf"}],
            jobId='JOB-ID'
        ))

        self.application.solr.docs.add(*self.docs)

        tester = self.app.test_client(self)
        response = tester.post("/apply", content_type="application/json", data=data)
        self.assertEqual(response.status_code, 200)

        # Wait for thread to finish.
        sleep(10)

        doc = self.application.solr.docs.get("test.txt")
        keywords = self.application.solr.docs.get("test.txt").keywords
        expected = [
            SolrDocKeyword("text", SolrDocKeywordTypes.KWM),
            SolrDocKeyword("test", SolrDocKeywordTypes.KWM),
        ]
        self.assertEqual(sorted(keywords), sorted(expected))

        keywords = self.application.solr.docs.get("test.pdf").keywords
        expected = [
            SolrDocKeyword("faufm", SolrDocKeywordTypes.KWM),
        ]
        self.assertEqual(sorted(keywords), sorted(expected))

        keywords = self.application.solr.docs.get("test.docx").keywords
        expected = []
        self.assertEqual(sorted(keywords), sorted(expected))

        keywords = self.application.solr.docs.get("test.pptx").keywords
        expected = []
        self.assertEqual(sorted(keywords), sorted(expected))


if __name__ == "__main__":
    unittest.main()
