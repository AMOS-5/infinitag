import unittest
from documentdata import DocumentData
import json


class DocumentTestCase(unittest.TestCase):
    def test_asDict(self):
        doc = DocumentData(name="test.pdf", path="./test.pdf",type="pdf",lang="de",size=20,createdAt="1.5.2020")
        dict = {
            "name" : "test.pdf",
            "path" : "./test.pdf",
            "type" : "pdf",
            "lang" : "de",
            "size" : 20,
            "createdAt" : "1.5.2020"
        }
        self.assertDictEqual(doc.asDict(), dict)
        
if __name__ == '__main__':
    unittest.main()
