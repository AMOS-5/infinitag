from backend.solr import (
    SolrDocuments,
    SolrKeywords,
    SolrKeywordStatistics,
    SolrKeywordModel,
    config,
)

import sys
import click


@click.command()
@click.option(
    "--corename",
    "-c",
    multiple=True,
    help="Values: 'docs', 'statistics', 'dimensions', 'keywords', 'keywordmodel'",
)
def wipe(corename):
    for c in corename:
        if c == "docs":
            SolrDocuments(config.documents_solr).clear()
            if "statistics" not in corename:
                print(
                    "The state of the statistics core depends on the docs core. It is suggested to also wipe 'statistics'."
                )
        elif c == "statistics":
            SolrKeywordStatistics(config.keyword_statistics_solr, None).clear()
        elif c == "dimensions":
            SolrKeywords(config.dimensions_solr).clear()
        elif c == "keywords":
            SolrKeywords(config.keywords_solr).clear()
        elif c == "keywordmodel":
            SolrKeywordModel(config.keyword_model_solr).clear()


if __name__ == "__main__":
    # For further information see: https://www.youtube.com/watch?v=dQw4w9WgXcQ
    if len(sys.argv) == 1:
        wipe.main(["--help"])
    else:
        wipe()
