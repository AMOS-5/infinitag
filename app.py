from flask_cors import CORS
from flask_jsonpify import jsonify
from flask import Flask, request

from argparse import ArgumentParser
import sys
import os
import signal
from datetime import datetime, timedelta

from documentdata import DocumentData
from backend import config
from backend.tagstorage import SolrTagStorage

app = Flask(__name__)
CORS(app)
SOLR_TAGS = None


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/documents')
def get_documents():
    """
    Sends document data as json object to frontend.
    Right now only sends dummy data
    """
    list = []
    solr_tags = []
    if SOLR_TAGS is not None:
        # load tags from solr
        solr_tags = SOLR_TAGS.tags

    for i in range(0, 100):
        day = datetime.today() - timedelta(days=i, hours=i, minutes=i)
        tags = []

        # assign tags pseudo randomly
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


@app.route('/tags', methods=['GET', 'POST', 'DELETE'])
def tags():
    if request.method == 'GET':
        data = SOLR_TAGS.tags
        return jsonify(data)
    if request.method == 'POST':
        data = request.json.get('tag')
        SOLR_TAGS.add(data)
        return jsonify(data + " has been added to database"), 200


@app.route('/tags/<tag_id>', methods=['DELETE'])
def remove_tags(tag_id):

    return jsonify(tag_id + " will be removed from database"), 200


@app.route('/stopServer', methods=['GET'])
def stop_server():
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if shutdown is None:
        return jsonify({"success": False, "message": "Server could not be shut down."})

    shutdown()
    return jsonify({"success": True, "message": "Server is shutting down..."})


if __name__ == '__main__':
    SOLR_TAGS = SolrTagStorage(config.tag_storage)

    # add sample tags
    SOLR_TAGS.clear()
    SOLR_TAGS.add("test-tag-1", "test-tag-2", "test-tag-3")

    parser = ArgumentParser(description="Infinitag Rest Server")
    parser.add_argument("--debug", type=bool, default=True)
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)
