from flask_cors import CORS
from flask_jsonpify import jsonify
from flask import Flask, request
from werkzeug.utils import secure_filename

from argparse import ArgumentParser
import sys

from datetime import datetime, timedelta

from backend.service import SolrService, SolrMiddleware
from backend.solr import SolrDoc


import logging as log

log.basicConfig(level=log.ERROR)

app = Flask(__name__)
solr = SolrService()
app.wsgi_app = SolrMiddleware(app.wsgi_app, solr)
CORS(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles the file upload post request by saving the file and adding it to the solr db
    :return: json object containing a success/error message
    """
    try:
        f = request.files['fileKey']
        file_name = f"tmp/{secure_filename(f.filename)}"
        f.save(file_name)

        if solr.docs is not None:
            # doc = SolrDoc(file_name, "tag1", "tag2")
            doc = SolrDoc(file_name)
            solr.docs.add(doc)
            print(f'Uploaded and saved file: {file_name}', file=sys.stdout)
        else:
            print('File only uploaded.')

        return jsonify(file_name + " was saved"), 200
    except Exception as e:
        print(str(e), file=sys.stderr)
        return jsonify(f"internal error: {e}"), 500


@app.route('/changetags', methods=['PATCH'])
def change_tags():
    try:
        iDoc = request.json
        path = iDoc.get('id')
        tags = iDoc.get('tags')
        print('changing tags on file ' + path + ' to ' + ','.join(tags) , file=sys.stdout)


        return jsonify("success"), 200
    except Exception as e:
        print(str(e), file=sys.stderr)
        return jsonify("error: " + str(e)), 500

@app.route('/documents')
def get_documents():
    if solr.docs is not None:
        try:
            # load docs from solr
            res = solr.docs.search("*:*")
            res = [SolrDoc.from_hit(hit).as_dict() for hit in res]
            response = (jsonify(res), 200)
        except Exception as e:
            log.error(f"/documents: {e}")
            response = (jsonify(f"/documents internal error: {e}"), 500)

    return response


@app.route('/health')
def get_health():
    return jsonify({"status": "UP"})


@app.route('/tags', methods=['GET', 'POST'])
def tags():
    if request.method == 'GET':
        try:
            data = solr.tags.tags
            return jsonify(data), 200
        except Exception as e:
            return jsonify(f"internal error: {e}"), 500
    elif request.method == 'POST':
        try:
            data = request.json.get('tag')
            solr.tags.add(data)
            return jsonify(data + " has been added"), 200
        except Exception as e:
            log.error(f"/documents: {e}")
            return jsonify(f"/tags internal error: {e}"), 500


@app.route('/tags/<tag_id>', methods=['DELETE'])
def remove_tags(tag_id):
    try:
        solr.tags.delete(tag_id)
        return jsonify(f"{tag_id} has been removed"), 200
    except Exception as e:
        return jsonify(f"{tag_id} internal error: {e}"), 500


@app.route('/stopServer', methods=['GET'])
def stop_server():
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if shutdown is None:
        return jsonify({"success": False, "message": "Server could not be shut down."})

    shutdown()
    return jsonify({"success": True, "message": "Server is shutting down..."})


if __name__ == '__main__':

    parser = ArgumentParser(description="Infinitag Rest Server")
    parser.add_argument("--debug", type=bool, default=True)
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)
