from flask import Flask
from flask_cors import CORS
from flask_jsonpify import jsonify
from flask import g
import pickle
from flask import Flask
from flask import request


app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/documents')
def get_documents():
    return jsonify({"documents": []})


@app.route('/health')
def get_health():
    return jsonify({"status": "UP"})





if __name__ == '__main__':
    app.run(debug=True)
