import json
import unittest
import io
import os
from werkzeug.datastructures import FileStorage
from flask_jsonpify import jsonify

# TODO hack to modify the config before the app gets initialized
# we should use a better fixture where the app gets initialized with our
# desired configurations
from backend.solr import config, SolrDoc, SolrHierarchy, SolrDocKeyword, SolrDocKeywordTypes

# reinit for test
config_keyword_model = config.keyword_model_solr
config_keyword_model["corename"] = "test_keyword_model"

config_keywords = config.keywords_solr
config_keywords["corename"] = "test_keywords"

config_docs = config.doc_storage_solr
config_docs["corename"] = "test_documents"

config_dims = config.dimensions_solr
config_dims["corename"] = "test_dimensions"

import app as application
from app import app


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        # the id will be the full_path "__contains__" can only be checked with the full path
        # this path is a mimic of our ec2 setup
        base = f"{os.getcwd()}/tests/test_docstorage_files/test"
        self.doc_types = ["pdf", "txt", "pptx", "docx"]
        self.doc_paths = [f"{base}.{doc_type}" for doc_type in self.doc_types]
        self.docs = [SolrDoc(path) for path in self.doc_paths]

    def test_home(self):
        tester = app.test_client(self)
        response = tester.get("/", content_type="html/text")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"Hello World!")

    def test_health(self):
        tester = app.test_client(self)
        response = tester.get("/health", content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data_response = json.loads(response.data)
        health = data_response["status"]
        self.assertEqual(health, "UP")

    def test_upload_file(self):
        if os.path.exists("./tmp/") == False:
            os.mkdir("./tmp")
        # delete file if it already exists
        if os.path.exists("./tmp/test_upload.test"):
            os.remove("./tmp/test_upload.test")
        self.assertFalse(os.path.exists("./tmp/test_upload.test"))

        tester = app.test_client(self)
        # send test file
        data = dict(fileKey=(io.BytesIO(b"abc"), "test_upload.test"))
        response = tester.post(
            "/upload",
            content_type="multipart/form-data",
            data=data,
            follow_redirects=True,
        )
        # check status code
        self.assertEqual(response.status_code, 200)
        # check file
        self.assertTrue(os.path.exists("./tmp/test_upload.test"))
        f = open("./tmp/test_upload.test", "r")
        content = f.read()
        f.close()
        self.assertEqual(content, "abc")

        # file got uploaded to solr?
        solr_doc_id = os.path.abspath("tmp/test_upload.test")
        self.assertTrue(solr_doc_id in application.solr.docs)

        # cleanup
        if os.path.exists("./tmp/test_upload.test"):
            os.remove("./tmp/test_upload.test")
        application.solr.docs.clear()

    def test_change_keywords(self):
        application.solr.docs.clear()
        application.solr.docs.add(self.docs[0])
        id = self.docs[0].id

        doc = application.solr.docs.get(id)
        self.assertEqual(doc.keywords, [])

        tester = app.test_client(self)
        data=json.dumps({
            "id":id,
            "keywords":[{"value": "a", "type": "MANUAL"}, {"value": "b", "type": "MANUAL"}, {"value": "c", "type": "MANUAL"}],
        })
        response=tester.patch('/changekeywords', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        doc = application.solr.docs.get(id)
        self.assertEqual(doc.keywords, [SolrDocKeyword(kw, SolrDocKeywordTypes.MANUAL) for kw in ["a", "b", "c"]])


    def test_documents(self):
        application.solr.docs.clear()
        application.solr.docs.add(*self.docs)
        tester = app.test_client(self)
        response = tester.get("/documents", content_type="application/json")
        self.assertEqual(response.status_code, 200)

        data_response = json.loads(response.data)
        self.assertIsNotNone(data_response)
        self.assertEqual(len(data_response), len(self.docs))


    def test_dimensions(self):
        application.solr.dimensions.clear()
        tester = app.test_client(self)
        data=json.dumps(dict(
            dim="test"
        ))
        response = tester.post("/dims", content_type="application/json", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(application.solr.dimensions.get()), 1)

        response = tester.get("/dims", content_type="application/json")
        self.assertEqual(response.status_code, 200)

        data_response = json.loads(response.data)
        self.assertIsNotNone(data_response)
        self.assertEqual(data_response, ["test"])

    def test_remove_dimension(self):
        application.solr.dimensions.clear()
        tester = app.test_client(self)

        application.solr.dimensions.add("a", "b", "c")
        response = tester.delete("/dims/b")
        self.assertEqual(response.status_code, 200)

        dims = application.solr.dimensions.get()
        self.assertEqual(dims, ["a", "c"])

    def test_keywords(self):
        application.solr.keywords.clear()
        tester = app.test_client(self)
        data=json.dumps(dict(
            key="test"
        ))
        response = tester.post("/keys", content_type="application/json", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(application.solr.keywords.get()), 1)

        response = tester.get("/keys", content_type="application/json")
        self.assertEqual(response.status_code, 200)

        data_response = json.loads(response.data)
        self.assertIsNotNone(data_response)
        self.assertEqual(data_response, ["test"])

    def test_remove_keyword(self):
        application.solr.keywords.clear()
        tester = app.test_client(self)

        application.solr.keywords.add("a", "b", "c")
        response = tester.delete("/keys/b")
        self.assertEqual(response.status_code, 200)

        keys = application.solr.keywords.get()
        self.assertEqual(keys, ["a", "c"])

    def test_keywordmodels(self):
        application.solr.keywordmodel.clear()
        tester = app.test_client(self)
        data=json.dumps(dict(
            id="test",
            hierarchy=[],
        ))
        response = tester.post("/models", content_type="application/json", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(application.solr.keywordmodel.get()), 1)

        response = tester.get("/models", content_type="application/json")
        self.assertEqual(response.status_code, 200)

        data_response = json.loads(response.data)
        self.assertIsNotNone(data_response)
        self.assertEqual(data_response, [{"id": "test", "hierarchy": "[]"}])

    def test_remove_keywordmodel(self):
        application.solr.keywordmodel.clear()
        tester = app.test_client(self)
        list = [None]*3
        for i in range(0, 3):
            list[i] = SolrHierarchy(str(i), [])
            application.solr.keywordmodel.add(list[i])

        response = tester.delete("/models/1")
        self.assertEqual(response.status_code, 200)

        del list[1]

        models = application.solr.keywordmodel.get()
        self.assertEqual(len(models), len(list))
        for i in range(0, len(models)):
            self.assertEqual(models[i].name, list[i].name)


if __name__ == "__main__":
    unittest.main()
