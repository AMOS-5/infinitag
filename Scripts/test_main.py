import unittest
from Scripts.app import app
import json


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

    def test_documents(self):
        tester = app.test_client(self)
        response = tester.get('/documents', content_type="application/json")
        self.assertEqual(response.status_code, 200)

        data_response = json.loads(response.data)
        documents = data_response['documents']
        self.assertIsNotNone(documents)


if __name__ == '__main__':
    unittest.main()

