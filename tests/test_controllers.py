import json
import unittest
import io
import os
from werkzeug.datastructures import FileStorage

# TODO hack to modify the config before the app gets initialized
# we should use a better fixture where the app gets initialized with our
# desired configurations
from backend.solr import config, SolrDoc

# reinit for test
config_keyword_model = config.keyword_model_solr
config_keyword_model["corename"] = "test_keyword_model"

config_keywords = config.keywords_solr
config_keywords["corename"] = "test_keywords"

config_docs = config.doc_storage_solr
config_docs["corename"] = "test_documents"

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

    def test_change_tags(self):
        application.solr.docs.clear()
        application.solr.docs.add(self.docs[0])
        id = self.docs[0].id

        doc = application.solr.docs.get(id)
        self.assertEqual(doc.keywords, [])

        tester = app.test_client(self)
        data=json.dumps({
            "id":id,
            "keywords":["a", "b", "c"],
        })
        response=tester.patch('/changetags', data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        doc = application.solr.docs.get(id)
        self.assertEqual(doc.keywords, ["a", "b", "c"])


    def test_documents(self):
        application.solr.docs.clear()
        application.solr.docs.add(*self.docs)
        tester = app.test_client(self)
        response = tester.get("/documents", content_type="application/json")
        self.assertEqual(response.status_code, 200)

        data_response = json.loads(response.data)
        self.assertIsNotNone(data_response)
        self.assertEqual(len(data_response), len(self.docs))


if __name__ == "__main__":
    unittest.main()
