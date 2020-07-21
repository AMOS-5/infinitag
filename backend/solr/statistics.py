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
    SolrKeywordModel,
    SolrDocuments,
    SolrKeywords,
    SolrDocKeyword,
)

from typing import Set, List, Generator, Tuple
import itertools as it
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


def pairwise(iterable):
    a, b = it.tee(iterable)
    next(b, None)
    return zip(a, b)


class SolrKeywordStatistics(SolrKeywords):
    """
    Keeps track of the number of distinct keywords which are active (attached) to
    documents in Solr
    """

    def __init__(self, config: dict, solr_docs: SolrDocuments):
        super().__init__(config)
        self.solr_docs = solr_docs

    def update(
        self, keywords_before: Set[SolrDocKeyword], keywords_after: Set[SolrDocKeyword]
    ) -> None:
        """
        Performs an update to the Solr core by:
        - adding new keywords
        - deleting keywords IF they are not attached to a document in Solr

        :param keywords_before: The keywords before the update
        :param keywords_after: The keywords after the update
        :return:
        """
        keywords_before = {kw.value for kw in keywords_before}
        keywords_after = {kw.value for kw in keywords_after}

        distinct_keywords = keywords_before ^ keywords_after

        keywords_to_add = [kw for kw in distinct_keywords if kw in keywords_after]
        if keywords_to_add:
            self.add(*keywords_to_add)

        delete_candidates = (kw for kw in distinct_keywords if kw in keywords_before)
        keywords_to_delete = self._keywords_to_delete(delete_candidates)
        if keywords_to_delete:
            self.delete(*keywords_to_delete)

    def _keywords_to_delete(
        self, delete_candidates: Generator[str, None, None]
    ) -> List[str]:
        keywords_to_delete = []
        for kw in delete_candidates:
            keyword_in_docs = self.solr_docs.search(f"keywords:{kw}", rows=1).hits
            if not keyword_in_docs:
                keywords_to_delete.append(kw)

        return keywords_to_delete

    def keywords(self, rows: int=100) -> List[str]:
        res = self.con.search("*:*", rows=rows)
        return [hit["id"] for hit in res]

class DocStatistics:
    def __init__(self):
        self.n_total = None
        self.n_tagged = None
        self.n_untagged = None
        self.last_7_days = None
        self.last_4_weeks = None
        self.last_12_months = None
        self.all_years = None


class SolrDocStatistics:
    def __init__(self, solr_docs: SolrDocuments):
        self.solr_docs = solr_docs

    def statistics(self) -> DocStatistics:
        ret = DocStatistics()
        ret.n_total, ret.n_tagged, ret.n_untagged = self._n_doc_statistics()
        ret.last_7_days = self._last_7_days()
        ret.last_4_weeks = self._last_4_weeks()
        ret.last_12_months = self._last_12_months()
        ret.all_years = self._all_years()
        return ret

    def _n_doc_statistics(self) -> Tuple[int, int, int]:
        n_total = self.solr_docs.con.search("*:*", rows=1).hits
        n_untagged = self.solr_docs.con.search("-keywords:[* TO *]", rows=1).hits
        n_tagged = n_total - n_untagged
        return n_total, n_tagged, n_untagged

    def _last_7_days(self) -> List[int]:
        now = datetime.utcnow()
        begin_today = self._reset_hours(now)

        daylie_frames = [now, begin_today]
        # subtract n days to build the frames
        daylie_frames.extend(begin_today - timedelta(days=days) for days in range(1, 7))
        # since we build the frames from the future into the past, reverse them now
        daylie_frames = reversed(daylie_frames)

        # create a list of intervals with (start1, end1), (start2, end2)
        # where start2 = end1 + 1 second
        search_intervals = self._create_search_intervals(daylie_frames)
        return self._get_docs_in_intervals(search_intervals)

    def _last_4_weeks(self) -> List[int]:
        now = datetime.utcnow()
        weekday = date.today().weekday()
        prev_monday = self._reset_hours(now - timedelta(days=weekday))

        weekly_frames = [now, prev_monday]
        weekly_frames.extend(
            prev_monday - timedelta(weeks=weeks) for weeks in range(1, 4)
        )
        weekly_frames = reversed(weekly_frames)

        search_intervals = self._create_search_intervals(weekly_frames)
        return self._get_docs_in_intervals(search_intervals)

    def _last_12_months(self) -> List[int]:
        now = self._now()
        begin_month = self._reset_month(now)

        # build the frames for last 12 months
        monthly_frames = [now, begin_month]
        monthly_frames.extend(
            begin_month - relativedelta(months=months) for months in range(1, 12)
        )
        monthly_frames = reversed(monthly_frames)

        search_intervals = self._create_search_intervals(monthly_frames)
        return self._get_docs_in_intervals(search_intervals)

    def _all_years(self) -> List[int]:
        now = self._now()

        # querry all past years and begin from 2020
        yearly_frames = [
            datetime(year, 1, 1, 0, 0, 0) for year in range(2020, now.year + 1)
        ]
        yearly_frames.append(now)

        search_intervals = self._create_search_intervals(yearly_frames)
        return self._get_docs_in_intervals(search_intervals)

    def _time_query(self, start: str, end: str) -> str:
        return f"creation_date:[ {start} TO {end} ]"

    def _time_to_solr(self, time: datetime) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _get_docs_in_intervals(
        self, search_intervals: List[Tuple[str, str]]
    ) -> List[int]:
        return [
            self.solr_docs.con.search(self._time_query(start, end), rows=1).hits
            for start, end in search_intervals
        ]

    def _create_search_intervals(self, time_frames: List[datetime]) -> List[str]:
        search_intervals = []
        for start, end in pairwise(time_frames):
            # make the end of the current distinct from the beginning of the next
            # to avoid documents being counter for both intervals
            end -= timedelta(seconds=1)
            search_intervals.append(
                (self._time_to_solr(start), self._time_to_solr(end))
            )

        return search_intervals

    def _reset_year(self, date: datetime) -> datetime:
        date = datetime(date.year, 1, 1, 0, 0, 0)
        return date

    def _reset_month(self, date: datetime) -> datetime:
        date = datetime(date.year, date.month, 1, 0, 0, 0)
        return date

    def _reset_hours(self, date: datetime) -> datetime:
        date = datetime(date.year, date.month, date.day, 0, 0, 0)
        return date

    def _now(self) -> datetime:
        # will be patched in tests
        return datetime.utcnow()


class SolrStatistics:
    """
    Provides an API for statistics related to Solr
    """

    def __init__(
        self,
        solr_docs: SolrDocuments,
        solr_keywordmodel: SolrKeywordModel,
        solr_keyword_statistics: SolrKeywordStatistics,
    ):
        self.solr_doc_statistics = SolrDocStatistics(solr_docs)
        self.solr_keywordmodel = solr_keywordmodel
        self.solr_keyword_statistics = solr_keyword_statistics

    def docs(self) -> DocStatistics:
        """
        Returns staticstics related to the documents core

        :return: tuple(total documents, documents tagged, documents untagged)
        """
        return self.solr_doc_statistics.statistics()

    def keywords(self) -> int:
        """
        Returns statistics related to keywords
        :return: number of distinct keywords attached to documents
        """
        return self.solr_keyword_statistics.con.search("*:*", rows=1).hits

    def keywordmodel(self) -> int:
        """
        Returns statistics related to keywordmodels
        :return: number of keywordmodels
        """
        return self.solr_keywordmodel.con.search("*:*", rows=1).hits


__all__ = ["SolrKeywordStatistics", "SolrStatistics"]
