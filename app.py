from flask_cors import CORS
from flask_jsonpify import jsonify
from flask import Flask, request
from werkzeug.utils import secure_filename

from argparse import ArgumentParser
import sys
import os
import signal
from datetime import datetime, timedelta

from documentdata import DocumentData
from backend import config
from backend.tagstorage import SolrTagStorage
from backend.docstorage import SolrDocStorage

app = Flask(__name__)
CORS(app)
SOLR_TAGS = None


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        f = request.files['fileKey']
        file_name = secure_filename(f.filename)

        print(request.form['test'], file=sys.stdout)

        f.save('~/filestorage/' + file_name)
        SOLR_DOCS.add('~/filestorage/' + file_name)
        print('Uploaded and saved file: ' + file_name, file=sys.stdout)
        return jsonify(file_name + " was saved"), 200
    except Exception as e:
        print(str(e), file=sys.stderr)
        return jsonify("error: " + str(e)), 500


@app.route('/documents')
def get_documents():
    """
    Sends document data as json object to frontend.
    Right now only sends dummy data
    """
    list = []
    solr_tags = []
    day = datetime.today()
    if SOLR_TAGS is not None:
        # load tags from solr
        solr_tags = SOLR_TAGS.tags
        solr_docs = SOLR_DOCS.search("*:*")

        for result in solr_docs:
            try:
                tags = result['author'] + result['title']
                doc = DocumentData(
                    name=result['title'],
                    path=result['id'],
                    type=result['stream_content_type'],
                    lang='de',
                    size=result['stream_size'],
                    createdAt=day,
                    tags=tags
                )
                list.append(doc.as_dict())
            except:
                return jsonify("internal error"), 500
    for i in range(0, 100):

        tags = []

        for tag_idx in range(0, len(solr_tags)):
            if(i % (tag_idx+2) == 0):
                tags.append(solr_tags[tag_idx])

        doc = DocumentData(
            name="test"+str(i)+".pdf",
            path="./test"+str(i)+".pdf",
            type="pdf",
            lang="de",
            size=200+i,
            createdAt=day,
            tags=tags
        )
        list.append(doc.as_dict())

    jsonstr = jsonify(list)
    return jsonstr


@app.route('/health')
def get_health():
    return jsonify({"status": "UP"})


@app.route('/tags', methods=['GET', 'POST'])
def tags():
    if request.method == 'GET':
        try:
            data = SOLR_TAGS.tags
            return jsonify(data)
        except:
            return jsonify("internal error"), 500
    if request.method == 'POST':
        try:
            data = request.json.get('tag')
            SOLR_TAGS.add(data)
            return jsonify(data + " has been added"), 200
        except:
            return jsonify("internal error"), 500


@app.route('/tags/<tag_id>', methods=['DELETE'])
def remove_tags(tag_id):
    try:
        SOLR_TAGS.delete(tag_id)
        return jsonify(tag_id + "has been removed"), 200
    except:
        return jsonify(tag_id + "internal error"), 500


@app.route('/stopServer', methods=['GET'])
def stop_server():
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if shutdown is None:
        return jsonify({"success": False, "message": "Server could not be shut down."})

    shutdown()
    return jsonify({"success": True, "message": "Server is shutting down..."})


if __name__ == '__main__':

    SOLR_TAGS = SolrTagStorage(config.tag_storage_solr)
    SOLR_DOCS = SolrDocStorage(config.doc_storage_solr)
    # add sample tags
    SOLR_TAGS.clear()
    SOLR_TAGS.add("test-tag-1", "test-tag-2", "test-tag-3")

    parser = ArgumentParser(description="Infinitag Rest Server")
    parser.add_argument("--debug", type=bool, default=True)
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)
