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

from flask_cors import CORS
from flask_jsonpify import jsonify
from flask import Flask, request, send_file, send_from_directory, safe_join
from werkzeug.utils import secure_filename
from utils.tagcloud import update_tagcloud

from argparse import ArgumentParser
import sys
import json
import time
from uuid import uuid4
import os
from pathlib import Path
import logging as log
import zipfile
import copy


from backend.service import SolrService, SolrMiddleware
from backend.service.tagging import (
    TaggingService,
    KWMJob,
    AutomatedTaggingJob
)
from backend.solr import (
    SolrDoc,
    SolrHierarchy,
    SolrDocKeyword,
    SolrDocKeywordTypes
)

from utils.data_preprocessing import create_automated_keywords

log.basicConfig(level=log.ERROR)

app = Flask(__name__)
tagging_service = TaggingService()
solr = SolrService()

app.wsgi_app = SolrMiddleware(app.wsgi_app, solr)
CORS(app)

if not os.path.exists("tmp"):
    os.mkdir("tmp")


@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/upload", methods=["POST", "PATCH", "PUT"])
def upload_file():
    """
    Handles the file upload post request by saving the file and adding it to the solr db
    :return: json object containing a success/error message
    """
    try:
        f = request.files["fileKey"]
        f_id = request.form['fid']
        file_name = secure_filename(f.filename)

        file_name = str("tmp" / Path(file_name))

        if request.method == "PUT":
            name, ext = os.path.splitext(str(file_name))
            base = os.path.basename(name)
            docs = solr.docs.search(f"id:*{base}*")
            if len(docs.docs) == 1:
                file_name = f"{name}_(1){ext}"
            else:
                largest = 1
                for doc in docs.docs:
                    id = doc['id']
                    suffix_start = id.rfind('(')
                    suffix_end = id.rfind(')')

                    if suffix_start > 0 and suffix_end > suffix_start:
                        number = id[suffix_start + 1: suffix_end]
                        try:
                            number = int(number)
                            if number > largest:
                                largest = number
                        except:
                            largest = 1
                file_name = f"{name}_({largest + 1}){ext}"

        doc = SolrDoc(file_name)
        if request.method == "POST":
            search_result = solr.docs.get(doc.id)
            if search_result is not None:
                return jsonify({
                    "message": "Document exists",
                    "id": doc.id,
                    "fid": f_id
                }), 207

    except Exception as e:
        return jsonify(f"Bad Request: {e}"), 400

    try:
        f.save(file_name)
    except Exception as e:
        return jsonify(f"Internal Server Error while saving file: {e}"), 500

    try:
        solr.docs.add(doc)
        doc = solr.docs.get(doc.id)

        keywords_before = {}
        keywords_after = doc.keywords
        solr.keyword_statistics.update(keywords_before, keywords_after)
    except Exception as e:
        return jsonify(f"Bad Gateway to solr: {e}"), 502

    print(f"Uploaded, saved and indexed file: {file_name}", file=sys.stdout)
    return jsonify(file_name + " was saved and indexed"), 200


@app.route("/download", methods=["POST"])
def download_files():
    """
    Handles the file download post request by sending the requested files.
    If multiple files are requested, they are combined to a zip file.
    :return: the requested file or a zip file
    """
    try:
        docs = request.json
        print(f"Downloading {len(docs)} files")
        if len(docs) == 1:
            return send_from_directory("tmp", filename=docs[0]["id"], as_attachment=True)
        else:
            zipf = zipfile.ZipFile('tmp/test.zip', 'w', zipfile.ZIP_DEFLATED)
            for doc in docs:
                zipf.write(os.path.join("tmp", doc["id"]), os.path.join("documents", doc["id"]))
            zipf.close()
            return send_from_directory("tmp", 'test.zip', as_attachment=True)
    except Exception as e:
        log.error(f"/download {e}")
        return jsonify(f"Error: {e}"), 400


@app.route("/changekeywords", methods=["PATCH"])
def change_keywords():
    """
    Handles the updating of keywords for a document
    :return: json object containing a success/error message
    """
    try:
        iDoc = request.json
        id = iDoc.get("id")
        keywords = iDoc.get("keywords")
    except Exception as e:
        return jsonify(f"Bad Request: {e}"), 400

    try:
        solDoc = solr.docs.get(id)
        keywords_before = copy.deepcopy(solDoc.keywords)
        keywords_after = {
            SolrDocKeyword(kw["value"], SolrDocKeywordTypes.from_str(kw["type"])) for kw in keywords
        }

        solDoc.keywords = keywords_after
        solr.docs.update(solDoc)

        solr.keyword_statistics.update(keywords_before, keywords_after)
    except Exception as e:
        log.error(f"/changekeywords {e}")
        return jsonify(f"Bad Gateway to solr: {e}"), 502

    print("changed keywords on file " + id + " to " + ",".join([kw.value for kw in solDoc.keywords]), file=sys.stdout)
    return jsonify("success"), 200


@app.route("/documents", methods=["GET"])
def get_documents():
    """
    Queries a given page from Solr and sends them to the front end

    :param page: The page number
    :param num_per_page: Number of entries per page
    :param sort_field: The field used for sorting (all fields in SolrDoc)
    :param sort_order: asc / desc
    :param search_term: string which should be searched for in Solr
    :return: json object containing the documents or an error message
    """
    try:
        page = int(request.args.get("page", 0))
        num_per_page = int(request.args.get("num_per_page", 10))
        sort_field = request.args.get("sort_field", "id")
        sort_order = request.args.get("sort_order", "asc")
        search_term = request.args.get("search_term", "")
        start_date = request.args.get("start_date", "")
        end_date = request.args.get("end_date", "")
        keywords_only = request.args.get("keywords_only", False)

        total_pages, docs = solr.docs.page(
            page,
            num_per_page,
            sort_field,
            sort_order,
            search_term,
            start_date,
            end_date,
            keywords_only
        )

        docs = [doc.as_dict() for doc in docs]
        res = jsonify(
            page=page,
            num_per_page=num_per_page,
            sort_field=sort_field,
            sort_order=sort_order,
            search_term=search_term,
            total_pages=total_pages,
            docs=docs
        )

        return res, 200
    except Exception as e:
        log.error(f"/documents {e}")
        return jsonify(f"Bad Gateway to solr: {e}"), 502


@app.route("/documents/<file_name>", methods=["DELETE"])
def delete_document(file_name):
    f = file_name
    docs = solr.docs.search(f"id:*{file_name}*")
    for doc in docs.docs:
        try:
            solr.docs.delete(doc['id'])
        except Exception as e:
            return jsonify({"message": "could not delete", "error": e}), 502

    return jsonify({"message": "success"}), 201


@app.route("/health")
def get_health():
    return jsonify({"status": "UP"})


@app.route("/dims", methods=["GET", "POST"])
def dimensions():
    """
    Handles GET and POST request for uncategorized dimensions
    :return: json object containing the uncategorized dimensions and/or a status message
    """
    if request.method == "GET":
        try:
            data = solr.dimensions.get()
            return jsonify(data), 200
        except Exception as e:
            return jsonify(f"internal error: {e}"), 500
    elif request.method == "POST":
        try:
            data = request.json.get("dim")
            solr.dimensions.add(data)
            return jsonify(data + " has been added to dimensions"), 200
        except Exception as e:
            log.error(f"/dims: {e}")
            return jsonify(f"/dims internal error: {e}"), 500


@app.route("/dims/<dim_id>", methods=["DELETE"])
def remove_dimension(dim_id):
    """
    Handles DELETE request for uncategorized dimensions
    :return: json object containing a status message
    """
    try:
        solr.dimensions.delete(dim_id)
        return jsonify(f"{dim_id} has been removed from dimensions"), 200
    except Exception as e:
        return jsonify(f"{dim_id} internal error: {e}"), 500


@app.route("/keys", methods=["GET", "POST"])
def keywords():
    """
    Handles GET and POST request for uncategorized keywords
    :return: json object containing the uncategorized keywords and/or a status message
    """
    if request.method == "GET":
        try:
            data = solr.keywords.get()
            return jsonify(data), 200
        except Exception as e:
            return jsonify(f"internal error: {e}"), 500
    elif request.method == "POST":
        try:
            data = request.json.get("key")
            solr.keywords.add(data)
            return jsonify(data + " has been added to keywords"), 200
        except Exception as e:
            log.error(f"/dims: {e}")
            return jsonify(f"/dims internal error: {e}"), 500


@app.route("/keys/<key_id>", methods=["DELETE"])
def remove_keyword(key_id):
    """
    Handles DELETE request for uncategorized keywords
    :return: json object containing a status message
    """
    try:
        solr.keywords.delete(key_id)
        return jsonify(f"{key_id} has been removed from keywords"), 200
    except Exception as e:
        return jsonify(f"{key_id} internal error: {e}"), 500



@app.route("/keywordlist", methods=["GET"])
def get_keywordlist():
    """
    Handles GET request for the list of all keywords
    Sends a list of all keywords, including both uncategorized ones and
    keywords in hierarchies.
    :return: json object containing all keywords with their respective kwm and parents
    """
    try:
        uncatKeywords = solr.keywords.get()
        data = [{"id": kw, "kwm": None, "parents": []} for kw in uncatKeywords]

        solrHierarchies = solr.keywordmodel.get()
        for hierarchy in solrHierarchies:
            keywords = hierarchy.get_keywords()
            for kw in keywords.keys():
                data.append({"id": kw, "kwm": hierarchy.name, "parents": keywords[kw]})

        return jsonify(data), 200
    except Exception as e:
        return jsonify(f"internal error: {e}"), 500


@app.route("/models", methods=["GET", "POST"])
def keywordmodels():
    """
    Handles GET and POST request for keyword models
    :return: json object containing the keyword models and/or a status message
    """
    if request.method == "GET":
        try:
            solrHierarchies = solr.keywordmodel.get()
            list = [hierarchy.as_dict() for hierarchy in solrHierarchies]
            return json.dumps(list), 200
        except Exception as e:
            return jsonify(f"internal error: {e}"), 500
    elif request.method == "POST":
        try:
            data = request.json
            solrHierarchy = SolrHierarchy(data.get("id"), data.get("hierarchy"), data.get("keywords"))
            solr.keywordmodel.add(solrHierarchy)
            return jsonify(
                solrHierarchy.name + " has been added to keywordmodels"), 200
        except Exception as e:
            log.error(f"/models: {e}")
            return jsonify(f"/models internal error: {e}"), 500


@app.route("/models/<model_id>", methods=["DELETE"])
def remove_keyword_model(model_id):
    """
    Handles DELETE request for keyword models
    :return: json object containing a status message
    """
    try:
        solr.keywordmodel.delete(model_id)
        return jsonify(f"{model_id} has been removed from keyword models"), 200
    except Exception as e:
        return jsonify(f"{model_id} internal error: {e}"), 500


@app.route("/stopServer", methods=["GET"])
def stop_server():
    shutdown = request.environ.get("werkzeug.server.shutdown")
    if shutdown is None:
        return jsonify(
            {"success": False, "message": "Server could not be shut down."})

    shutdown()
    return jsonify({"success": True, "message": "Server is shutting down..."})


@app.route("/apply", methods=["POST"])
def apply_tagging_method():
    """
    Endpoint for autotagging of documents.
    If the keyword model autotagging is choosen, the documents and the hierarchy
    are parsed and the keywords get applied. If no documents are given the
    keywords get applied to all documents
    :return: json object containing a status message
    """
    data = request.json
    docs = data["documents"]
    options = data["options"]
    job_id = data["jobId"]

    if options["applyToAllDocuments"]:
        res = solr.docs.search("*:*", rows=5000)
        doc_ids = [SolrDoc.from_hit(hit).id for hit in res]
    else:
        doc_ids = [doc["id"] for doc in docs]

    if data["taggingMethod"]["type"] == "KWM" and data["keywordModel"] is not None:
        print("Applying keyword model")
        kwm_data = data["keywordModel"]
        kwm = SolrHierarchy(kwm_data["id"], json.loads(kwm_data["hierarchy"]), kwm_data["keywords"])
        start_time = time.time()
        keywords = kwm.get_keywords()
        stop_time = time.time() - start_time
        print("time for extracting ", len(keywords), "keywords from hierarchy: ", "{:10.7f}".format(stop_time), "sec")

        job = KWMJob(keywords, job_id, solr, *doc_ids)
        tagging_service.add_job(job)
        job.start()


    else:
        num_clusters = options["numClusters"]
        num_keywords = options["numKeywords"]
        default = options["computeOptimal"]
        start_time = time.time()


        job = AutomatedTaggingJob(job_id=job_id,
                                  doc_ids=doc_ids,
                                  num_clusters=num_clusters,
                                  num_keywords=num_keywords,
                                  default = default,
                                  solr_service=solr)

        tagging_service.add_job(job)
        job.start()

        stop_time = time.time() - start_time

        print("Applying keywords took:", "{:10.7f}".format(stop_time))
    # Currently this code lags behind one apply tagging click tag (word) cloud
    # Has to placed at a better place
    update_tagcloud(path_to_save='frontend/src/assets/img')
    return jsonify({"status": 200})


@app.route("/job/<job_id>", methods=["GET", "DELETE"])
def get_job_status(job_id):
    job = tagging_service.get_job(job_id)
    if request.method == "GET":
        if job is None:
            return jsonify({"status": 209, "message": "TAGGING_JOB.NO_JOB"}), 209
        else:
            return jsonify({"status": 200, "message": job.status, "progress": job.progress, "timeRemaining": job.time_remaining}), 200
    elif request.method == "DELETE" and job is not None:
        tagging_service.cancel_job(job_id)
        return jsonify({"status": 200, "message": "TAGGING_JOB.CANCELED_JOB", "id": job_id}), 200


@app.route("/statistics", methods=["GET"])
def get_statistics():
    doc_stats = solr.statistics.docs()
    n_keywords = solr.statistics.keywords()
    n_keyword_models = solr.statistics.keywordmodel()
    return jsonify(
        n_total_docs=doc_stats.n_total,
        n_tagged_docs=doc_stats.n_tagged,
        n_untagged_docs=doc_stats.n_untagged,
        uploaded_last_7_days=doc_stats.last_7_days,
        uploaded_last_4_weeks=doc_stats.last_4_weeks,
        uploaded_last_12_months=doc_stats.last_12_months,
        uploaded_all_years=doc_stats.all_years,
        n_keywords=n_keywords,
        n_keyword_models=n_keyword_models,
    )

if __name__ == "__main__":

    parser = ArgumentParser(description="Infinitag Rest Server")
    parser.add_argument("--debug", type=bool, default=True)
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)
