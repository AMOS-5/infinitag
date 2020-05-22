from flask_cors import CORS
from flask_jsonpify import jsonify
from flask import Flask, request
from werkzeug.utils import secure_filename

from argparse import ArgumentParser
import sys

from datetime import datetime, timedelta

from backend.services.solr import SolrService
from backend.documentdata import DocumentData
from backend import middleware


app = Flask(__name__)
solr_service = SolrService()
app.wsgi_app = middleware.SolrMiddleware(app.wsgi_app, solr_service)
CORS(app)
SOLR_TAGS = solr_service.get_tags()
SOLR_DOCS = solr_service.get_docs()


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
        if SOLR_DOCS is not None:
            print(f'Pushing to Solr: {file_name}' , file=sys.stdout)
            SOLR_DOCS.add(file_name)
            print(f'Uploaded and saved file: {file_name}' , file=sys.stdout)
        else:
            print('File only uploaded.')

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
    if SOLR_TAGS is not None:
        # load docs from solr
        solr_docs = SOLR_DOCS.search("*:*")

        for result in solr_docs:
            try:
                doc = DocumentData.from_result(result)
                list.append(doc.as_dict())
                #for tag in doc.tags:
                #    SOLR_TAGS.add(tag)
            except Exception as e:
                print(e, file=sys.stderr)
                return jsonify(f"internal error: {e}"), 500

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

    parser = ArgumentParser(description="Infinitag Rest Server")
    parser.add_argument("--debug", type=bool, default=True)
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)
