import json
import unittest
import io
import os
from werkzeug.datastructures import FileStorage

from app import app

class BasicTestCase(unittest.TestCase):
    def test_home(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'Hello World!')

    def test_health(self):
        tester = app.test_client(self)
        response = tester.get('/health', content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data_response = json.loads(response.data)
        health = data_response['status']
        self.assertEqual(health, "UP")

    def test_upload_file(self):
        #delete file if it already exists
        if os.path.exists("./tmp/test_upload.test"):
            os.remove("./tmp/test_upload.test")
        self.assertFalse(os.path.exists("./tmp/test_upload.test"))

        tester = app.test_client(self)
        #send test file
        data = dict(fileKey=(io.BytesIO(b'abc'), "test_upload.test"))
        response = tester.post('/upload', content_type='multipart/form-data', data=data, follow_redirects=True)
        #check status code
        self.assertEqual(response.status_code, 200)
        data_response = json.loads(response.data)
        self.assertEquals(data_response, "test_upload.test was saved")
        #check file
        self.assertTrue(os.path.exists("./tmp/test_upload.test"))
        f = open("./tmp/test_upload.test", "r")
        content = f.read()
        f.close()
        self.assertEqual(content, "abc")

        #cleanup
        if os.path.exists("./tmp/test_upload.test"):
            os.remove("./tmp/test_upload.test")

    def test_documents(self):
        tester = app.test_client(self)
        response = tester.get('/documents', content_type="application/json")
        self.assertEqual(response.status_code, 200)

        data_response = json.loads(response.data)
        self.assertIsNotNone(data_response)


if __name__ == '__main__':
    unittest.main()
