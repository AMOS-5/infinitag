import unittest
from Scripts.preprocessing import MyNLP
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import os


class PreProcessingTestCase(unittest.TestCase):

    def test_cleantext(self):
        result = []
        obj = MyNLP('./testfiles')
        cwd = os.getcwd()
        dirname, filename = os.path.split(os.path.abspath(__file__))
        path = os.path.join(cwd, 'tests/testfiles/100-02.txt')
        fil = open(path, 'r', encoding="utf-8")
        text = fil.read()
        fil.close()
        result = obj.cleantext(text)
        self.assertNotIn(result, stopwords.words('english'))
        self.assertNotIn(result, string.punctuation)
        for word in result:
            self.assertNotIn(result, WordNetLemmatizer().lemmatize(word))




if __name__ == '__main__':
        unittest.main()
