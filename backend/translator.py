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
