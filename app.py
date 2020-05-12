from flask_cors import CORS
from flask_jsonpify import jsonify
from flask import Flask, request

import sys
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
        doc = DocumentData(
            name="test"+str(i)+".pdf",
            path="./test"+str(i)+".pdf",
            type="pdf",
            lang="de",
            size=200+i,
            createdAt=day
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
        data = [{"name": "automobile"}, {"name": "BMW"}, {"name": "sedan"}]
        return jsonify(data), 200
    if request.method == 'POST':
        data = request.json.get('name')
        return jsonify(data + " will be added to database"), 500
    if request.method == 'DELETE':
        data = request.json.get('name')
        return jsonify(data + " will be deleted from database"), 500


if __name__ == '__main__':
    app.run(debug=True)
