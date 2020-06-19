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
from flask import Flask, request
from werkzeug.utils import secure_filename

from argparse import ArgumentParser
import sys
import json
import time
from uuid import uuid4
import os

from backend.service import SolrService, SolrMiddleware
from backend.solr import SolrDoc, SolrHierarchy, SolrDocKeyword, \
    SolrDocKeywordTypes

from utils.tfidf_vector import tfidf_vector
from utils.k_means_cluster import kmeans_clustering

from utils.data_preprocessing import dataload_for_frontend

import logging as log

log.basicConfig(level=log.ERROR)

app = Flask(__name__)
solr = SolrService()
app.wsgi_app = SolrMiddleware(app.wsgi_app, solr)
CORS(app)


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

        if request.method == "PUT":
            name, ext = os.path.splitext(file_name)
            file_name = f"{name}_{uuid4()}{ext}"

        file_name = f"tmp/{file_name}"
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
    except Exception as e:
        return jsonify(f"Bad Gateway to solr: {e}"), 502

    print(f"Uploaded, saved and indexed file: {file_name}", file=sys.stdout)
    return jsonify(file_name + " was saved and indexed"), 200


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
        solDoc.keywords = [
            SolrDocKeyword(kw["value"], SolrDocKeywordTypes.from_str(kw["type"])) for kw in keywords
        ]
        solr.docs.update(solDoc)
    except Exception as e:
        print(e)
        return jsonify(f"Bad Gateway to solr: {e}"), 502

    print("changed keywords on file " + id + " to " + ",".join([kw.value for kw in solDoc.keywords]), file=sys.stdout)
    return jsonify("success"), 200


@app.route("/documents")
def get_documents():
    """
    Queries all documents form solr and sends them to the front end
    :return: json object containing the documents or an error message
    """
    try:
        # load docs from solr
        docs = solr.docs.search("*:*")
        res = [SolrDoc.from_hit(hit).as_dict() for hit in docs]
        return jsonify(res), 200
    except Exception as e:
        return jsonify(f"Bad Gateway to solr: {e}"), 502


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
            # print("kwm: " + data , file=sys.stdout)
            return json.dumps(list), 200
        except Exception as e:
            return jsonify(f"internal error: {e}"), 500
    elif request.method == "POST":
        try:
            data = request.json
            solrHierarchy = SolrHierarchy(data.get("id"), data.get("hierarchy"))
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


@app.route("/keywordmodels", methods=["GET"])
def keywordmodel():
    """
    Handles GET and POST request for keyword model
    :return: json object containing the keyword model and/or a status message
    """
    if request.method == "GET":
        res = []
        try:
            data = solr.keywordmodel.get()
            for model in data:
                modelDict = {"name": model.name, "hierarchy": model.hierarchy}
                res.append(modelDict)
            return jsonify(res), 200
        except Exception as e:
            return jsonify(f"internal error: {e}"), 500


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

    if data["keywordModel"] is not None and data["taggingMethod"]["type"] == "KWM":
        print("Applying keyword model")
        kwm_data = data["keywordModel"]
        kwm = SolrHierarchy(kwm_data["name"], kwm_data["hierarchy"])

        start_time = time.time()
        keywords = kwm.get_keywords()
        stop_time = time.time() - start_time

        #print("keywords: ", keywords)
        print("time for extracting ", len(keywords), "keywords from hierarchy: ", "{:10.7f}".format(stop_time), "sec")

        # apply kwm on all documents
        if "documents" not in data or len(data["documents"]) == 0:
            res = solr.docs.search("*:*")
            docs = [SolrDoc.from_hit(hit) for hit in res]
        else:
            docs_json = data["documents"]
            doc_ids = [doc['id'] for doc in docs_json]
            docs = solr.docs.get(*doc_ids)

            if not isinstance(docs, list):
                docs = [docs]
        print(docs)


        min = 10000000
        max = 0
        total = 0
        # apply keywords for each document and measure time
        for doc in docs:
            start_time = time.time()

            applied = doc.apply_kwm(keywords)
            if applied:
                solr.docs.update(doc)

            stop_time = time.time() - start_time
            if stop_time < min:
                min = stop_time
            if stop_time > max:
                max = stop_time
            total += stop_time

    else:
        docs = data["documents"]
        unwanted_keywords = {'patient', 'order', 'showed', 'exam', 'number', 'home', 'left', 'right', 'history', 'daily', 'instruction','interaction', 'fooddrug', 'time', 'override','unit','potentially', 'march', 'added'}
        flattened, vocab_frame, file_list, overall = dataload_for_frontend(docs,unwanted_keywords)
        dist, tfidf_matrix, terms = tfidf_vector(flattened)
        automated_tags = kmeans_clustering(tfidf_matrix, flattened, terms,file_list, 5, 5)

        for doc in docs:
            for file_names, keywords in automated_tags.items():
                if file_names == doc['id']:
                    print('doc[id]:', doc['id'])
                    print('file_names', file_names)
                    print('keywords_tag assigned:', keywords)
                    print('')

                    solDoc = solr.docs.get(doc['id'])
                    solDoc.keywords = [SolrDocKeyword(kw, SolrDocKeywordTypes.ML) for kw in keywords]
                    solr.docs.update(solDoc)

    return jsonify({"status": 200})


if __name__ == "__main__":

    #solr.docs.wipe_keywords()

    parser = ArgumentParser(description="Infinitag Rest Server")
    parser.add_argument("--debug", type=bool, default=True)
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)
