import unittest
from utils.data_preprocessing import clean_text
from nltk.corpus import stopwords
import string
import os


class DataPreProcessingTestCase(unittest.TestCase):

    def test_dataload_and_preprocess(self):

        #File Path
        dir = r"\testfiles\100-02.txt"
        unwanted = ['md','po','patient']
        cwd = os.getcwd()
        overall=[]

        #load file
        dirname, filename = os.path.split(os.path.abspath(__file__))
        path = os.path.join(dirname, filename)
        fil = open(path, 'r', encoding="latin")
        text = fil.read()
        fil.close()

        #Store result
        result = [clean_text(filename).split()]


        #Unit test for stopwords and punctuation
        for item in result:
            for word in item:
                self.assertNotIn(word, stopwords.words('english'))
                self.assertNotIn(word, string.punctuation)

        #Unit test for digit, shortwords check and unwanted words
        for i in result:
            new_items = [item for item in i if not item.isdigit()]
            for num in new_items:
                self.assertNotIn("1", num)

            new_list = [test for test in new_items if (len(test) > 3)]
            for word in new_list:
                self.assertNotIn("was", word)

            new_lists = [items for items in new_list if items not in unwanted]
            for word in new_lists:
                self.assertNotIn("patient", word)

            overall.append([new_lists])

        flattened = [val for sublist in overall for val in sublist]

        return

if __name__ == '__main__':
        unittest.main()
