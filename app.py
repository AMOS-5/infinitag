from flask_cors import CORS
from flask_jsonpify import jsonify
from flask import Flask

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


if __name__ == '__main__':
    app.run(debug=True)
