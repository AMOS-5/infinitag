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
    except Exception as e:
        return jsonify(f"Bad Request: {e}"), 400

    try:
        f.save(file_name)
    except Exception as e:
        return jsonify(f"Internal Server Error while saving file: {e}"), 500

    try:
        doc = SolrDoc(file_name)
        solr.docs.add(doc)
    except Exception as e:
        return jsonify(f"Bad Gateway to solr: {e}"), 502

    print(f'Uploaded, saved and indexed file: {file_name}', file=sys.stdout)
    return jsonify(file_name + " was saved and indexed"), 200



@app.route('/changetags', methods=['PATCH'])
def change_tags():
    try:
        iDoc = request.json
        id = iDoc.get('id')
        tags = iDoc.get('tags')
    except Exception as e:
        return jsonify(f"Bad Request: {e}"), 400

    try:
        solDoc = solr.SOLR_DOCS.get_doc(id)
        solDoc.tags = tags
        solr.SOLR_DOCS.update(solDoc)
    except Exception as e:
        return jsonify(f"Bad Gateway to solr: {e}"), 502

    print('changed tags on file ' + id + ' to ' + ','.join(tags) , file=sys.stdout)
    return jsonify("success"), 200


@app.route('/documents')
def get_documents():
    try:
        # load docs from solr
        res = solr.docs.search("*:*")
        res = [SolrDoc.from_hit(hit).as_dict() for hit in res]
        return jsonify(res), 200
    except Exception as e:
        return jsonify(f"Bad Gateway to solr: {e}"), 502



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

dims_arr = ["country", "state", "city"]
keys_arr = ["germany", "bavaria", "erlangen"]

@app.route('/dims', methods=['GET', 'POST'])
def dims():
    if request.method == 'GET':
        try:
            data = dims_arr
            #TODO query here
            return jsonify(data), 200
        except Exception as e:
            return jsonify(f"internal error: {e}"), 500
    elif request.method == 'POST':
        try:
            data = request.json.get('dim')
            #TODO add here
            dims_arr.append(data)
            log.critical(f"/dim: {data}")
            return jsonify(data + " has been added"), 200
        except Exception as e:
            log.error(f"/dims: {e}")
            return jsonify(f"/dims internal error: {e}"), 500


@app.route('/dims/<dim_id>', methods=['DELETE'])
def remove_dim(dim_id):
    try:
        #TODO delete here
        dims_arr.remove(dim_id)
        return jsonify(f"{dim_id} has been removed"), 200
    except Exception as e:
        return jsonify(f"{dim_id} internal error: {e}"), 500

@app.route('/keys', methods=['GET', 'POST'])
def keys():
    if request.method == 'GET':
        try:
            data = keys_arr
            #TODO query here
            return jsonify(data), 200
        except Exception as e:
            return jsonify(f"internal error: {e}"), 500
    elif request.method == 'POST':
        try:
            data = request.json.get('key')
            #TODO add here
            keys_arr.append(data)
            log.critical(f"/key: {data}")
            return jsonify(data + " has been added"), 200
        except Exception as e:
            log.error(f"/dims: {e}")
            return jsonify(f"/dims internal error: {e}"), 500


@app.route('/keys/<key_id>', methods=['DELETE'])
def remove_key(key_id):
    try:
        #TODO delete here
        keys_arr.remove(key_id)
        return jsonify(f"{key_id} has been removed"), 200
    except Exception as e:
        return jsonify(f"{key_id} internal error: {e}"), 500

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
