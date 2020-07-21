# InfiniTag Copyright © 2020 AMOS-5
# Permission is hereby granted,
# free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions: The above copyright notice and this
# permission notice shall be included in all copies or substantial portions
# of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
# NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.

from googletrans import Translator as GoogleTrans
from typing import List, Set


class Translator:
    def __init__(self, target_languages: List[str]):
        self.target_languages = target_languages
        self.translator = GoogleTrans()

    def translate(self, words: List[str]) -> Set[str]:
        """
        Translates a list of words into the target languages with which the Translator
        was initialized.

        :param words: List of words to translate in the target languages
        :return: Translation results without context to which language they belong
        """
        res = set(words)
        for lang in self.target_languages:
            translated = self.translator.translate(words, src="auto", dest=lang)
            res.update(word.text for word in translated)

        return res


__all__ = ["Translator"]
