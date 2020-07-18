from backend.service import SolrService

from wordcloud import WordCloud
from os import path

def update_tagcloud(path_to_save: str, solr_service: SolrService) -> None:
    max_words = 1000

    keywords = solr_service.keyword_statistics.keywords(rows=max_words)
    keywords_str = " ".join(kw for kw in keywords)

    if len(keywords) > 0:
        wordcloud = WordCloud(
            width=1200,
            height=700,
            max_font_size=100,
            max_words=max_words,
            background_color="white",
        ).generate(keywords_str)

        wordcloud.to_file(path.join(path_to_save, "tag_cloud.png"))
