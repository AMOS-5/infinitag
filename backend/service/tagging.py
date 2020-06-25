import time
from threading import Thread

from backend.solr import SolrDocStorage, SolrDoc, SolrDocKeyword, \
    SolrDocKeywordTypes
from utils.data_preprocessing import lemmatize_keywords, \
    create_automated_keywords


class TaggingJob:
    def __init__(self, job_id: str, status='started', progress=0):
        self.job_id = job_id
        self.status = status
        self.progress = progress


class KWMJob(Thread, TaggingJob):
    def __init__(self, keywords: dict, job_id, solr_docs: SolrDocStorage, *doc_ids: str):
        super().__init__()
        self.keywords = keywords
        self.doc_ids = doc_ids
        self.job_id = job_id
        self.solr_docs = solr_docs
        self.status = 'STARTED'
        self.progress = 0
        self.cancelled = False
        self.time_remaining = -1

    def run(self):
        """
        Applies a keyword model on every document in Solr.
        The idea is to search the content in Solr for the lemmatized_keyword if it is found
        the (normal)keyword and its parents are applied.

        :param keywords: dict of keywords and corresponding parents
        :param doc_ids:
        :param job_id
        :return:
        """
        self.status = 'TAGGING_JOB.LEMMA_START'
        lemmatized_keywords = lemmatize_keywords(self.keywords)
        self.status = 'TAGGING_JOB.LEMMA_END'
        self.progress = 20

        self.status = 'TAGGING_JOB.DOC_FIND'
        id_query = self.solr_docs.build_id_query(self.doc_ids)
        self.status = 'TAGGING_JOB.DOC_FOUND'
        changed_docs = {}
        self.status = 'TAGGING_JOB.APPLY_KWM'
        start_time = time.time()
        time_index = 0
        iteration_time = None
        idx = 0
        for lemmatized_keyword, (keyword, parents) in zip(
            lemmatized_keywords, self.keywords.items()
        ):
            if self.cancelled:
                break
            if idx == 0:
                progress_step = 80 / len(lemmatized_keywords)
            query = self.solr_docs.build_kwm_query(id_query, lemmatized_keyword)

            res = self.solr_docs.search(query)
            res = [SolrDoc.from_hit(hit) for hit in res]

            for doc in res:
                if self.cancelled:
                    break
                # check whether the doc was already updated
                if doc.id in changed_docs:
                    doc = changed_docs[doc.id]

                # update keywords
                doc.keywords.add(
                    SolrDocKeyword(keyword, SolrDocKeywordTypes.KWM))
                doc.keywords.update(
                    SolrDocKeyword(parent, SolrDocKeywordTypes.KWM)
                    for parent in parents
                )

                # store for bulk update
                changed_docs[doc.id] = doc
            if time_index == 0:
                end_time = time.time()
                iteration_time = end_time - start_time
                time_index = 1

            remaining_iterations = len(lemmatized_keywords) - idx
            idx += 1
            if iteration_time != - 1:
                self.time_remaining = iteration_time * remaining_iterations
            self.progress += progress_step
        changed_docs = changed_docs.values()
        self.status = 'TAGGING_JOB.DOC_UPDATE'
        self.solr_docs.update(*changed_docs)
        self.status = 'FINISHED'

    def stop(self):
        self.cancelled = True


class AutomatedTaggingJob(Thread, TaggingJob):
    def __init__(self, job_id: str, docs, solr_docs: SolrDocStorage):
        super().__init__()
        self.job_id = job_id
        self.docs = docs
        self.solr_docs = solr_docs
        self.status = 'STARTED'
        self.progress = 0
        self.cancelled = False
        self.time_remaining = -1

    def run(self):
        self.status = 'TAGGING_JOB.CREATE_KW'
        auto_keywords = create_automated_keywords(self.docs, self)
        self.status = 'TAGGING_JOB.KW_FOUND'

        doc_ids = auto_keywords.keys()
        docs = self.solr_docs.get(*doc_ids)
        self.status = 'TAGGING_JOB.APPLYING'
        start_time = time.time()
        time_index = 0
        iteration_time = None
        idx = 0
        for doc in docs:
            if self.cancelled:
                break
            if idx == 0:
                progress_step = self.progress / len(docs)

            new_keywords = auto_keywords[doc.id]
            doc.keywords.update(
                SolrDocKeyword(kw, SolrDocKeywordTypes.ML)
                for kw in new_keywords
            )

            if time_index == 0:
                end_time = time.time()
                iteration_time = end_time - start_time
                time_index = 1

            remaining_iterations = len(docs) - idx
            idx += 1
            if iteration_time != - 1:
                self.time_remaining = iteration_time * remaining_iterations
            self.progress += progress_step

        self.status = 'FINISHED'
        self.solr_docs.update(*docs)

    def stop(self):
        self.cancelled = True


class TaggingService:
    jobs = {}

    def __init__(self):
        pass

    def add_job(self, job: TaggingJob):
        self.jobs[job.job_id] = job

    def get_job(self, job_id):
        try:
            job = self.jobs[job_id]

            return job
        except KeyError:
            return None

    def cancel_job(self, job_id):
        job = self.get_job(job_id)
        if job is not None:
            job.stop()
            job.join()

