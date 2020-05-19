import unittest
from backend.documentdata import DocumentData
from datetime import datetime

class DocumentTestCase(unittest.TestCase):
    def test_asDict(self):
        doc = DocumentData(
            name="test.pdf",
            path="./test.pdf",
            type="pdf",
            lang="de",
            size=20,
            createdAt=datetime(year=2020, month=5, day=1, hour=12, minute=11, second=10),
            tags=[]
        )
        dict = {
            "name" : "test.pdf",
            "path" : "./test.pdf",
            "type" : "pdf",
            "lang" : "de",
            "size" : 20,
            "createdAt" : 'Fri May  1 12:11:10 2020',
            "tags": []
        }
        self.assertDictEqual(doc.as_dict(), dict)


if __name__ == '__main__':
    unittest.main()
