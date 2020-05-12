from flask_cors import CORS
from flask_jsonpify import jsonify
from flask import Flask, request
from argparse import ArgumentParser
import sys
import os
import signal
from datetime import datetime, timedelta

from documentdata import DocumentData


app = Flask(__name__)
CORS(app)


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
    for i in range(0, 1000):
        day = datetime.today() - timedelta(days=i, hours=i, minutes=i)
        tags = []
        if i % 2 == 0:
            tags.append("test-tag-1")
        if i % 3 == 0:
            tags.append("test-tag-2")
        if i % 4 == 0:
            tags.append("test-tag-3")
        
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
