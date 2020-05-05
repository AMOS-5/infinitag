from flask import Flask
from flask_cors import CORS
from flask_jsonpify import jsonify

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
    #doc1 = DocumentData(name="test.pdf", path="./test.pdf",type="pdf",lang="de",size=20,createdAt="1.5.2020")
    #doc2 = DocumentData(name="abc.txt", path="./abc.txt",type="txt",lang="en",size=30,createdAt="11.5.1999")
    list = []
    for i in range(0, 1000):
        day = datetime.today() - timedelta(days=i, hours=i, minutes=i)
        doc = DocumentData( 
            name="test"+str(i)+".pdf",
            path="./test"+str(i)+".pdf",
            type="pdf",
            lang="de",
            size=200-i,
            createdAt=day
        )
        list.append(doc.as_dict())
    
    jsonstr = jsonify(list)
    return jsonstr


@app.route('/health')
def get_health():
    return jsonify({"status": "UP"})


if __name__ == '__main__':
    app.run(debug=True)
