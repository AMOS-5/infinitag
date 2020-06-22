def apply_kwm(self, keywords: dict) -> bool:
        """
        Applies a keyword model given by all its keywords with their parents on this document.

        :param dict of keywords and parents:
        :return: whether the keywords in the document were updated
        """
        new_keywords = SolrKeywordFinder.find(self, keywords)

        if new_keywords:
            self.keywords = new_keywords

        return bool(new_keywords)

class SolrKeywordFinder:
    @staticmethod
    def find(doc: SolrDoc, keywords: dict) -> List[SolrDocKeyword]:
        """
        Finds all keywords from the dict that appear in the document and
        returns them together with the already added ones
        :param doc: document to be searched in
        :param keywords: keywords with their parents
        :return: list of all keywords
        """
        content = SolrKeywordFinder._parse_doc(doc)
        new_keywords = SolrKeywordFinder._find(content, keywords)

        if not new_keywords:
            return []

        new_keywords = {
            SolrDocKeyword(kw, SolrDocKeywordTypes.KWM) for kw in new_keywords
        }
        old_keywords = doc.keywords
        new_keywords.update(old_keywords)

        return list(new_keywords)

    @staticmethod
    def _parse_doc(doc: SolrDoc) -> Set[str]:
        """
        Parses the title and the content of a document into a set
        :param doc:
        :return: the content of a document wordwise in a set
        """
        parsed = set()
        delims = " |\n|\t|;|,|:|\.|\?|!|\(|\)|\{|\}|\[|\]|<|>|\\\\|/|=|\"|'"
        parsed.update([str.lower() for str in re.split(delims, doc.title)])
        parsed.update([str.lower() for str in re.split(delims, doc.content)])
        return parsed

    @staticmethod
    def _find(content: Set[str], keywords: dict) -> Set[str]:
        """
        Finds all keywords in the set of words and returns them as well as their parents
        :param content: set of words
        :param keywords: dict of keywords
        :return: set of found keywords
        """
        found_keywords = set()

        for kw in list(keywords.keys()):
            if kw in content:
                # print("found ", kw, " parents: ", keywords[kw], file=sys.stdout)
                found_keywords.add(kw)
                for parent in keywords[kw]:
                    found_keywords.add(parent)
                # print("found kw: ", found_keywords, file=sys.stdout)

        return found_keywords

    @staticmethod
    def _is_dimension(hierarchy: dict) -> bool:
        return hierarchy["nodeType"] == "DIMENSION"

    @staticmethod
    def _is_keyword(hierarchy: dict) -> bool:
        return hierarchy["nodeType"] == "KEYWORD"

    @staticmethod
    def _has_children(hierarchy: dict) -> bool:
        return "children" in hierarchy

    @staticmethod
    def _get_children(hierarchy: dict) -> list:
        return hierarchy["children"]

    @staticmethod
    def _get_keyword(hierarchy: dict) -> str:
        return hierarchy["item"]
