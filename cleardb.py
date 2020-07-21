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
