# Built-in imports
import sys
import json

# External imports
from flask import Flask
from flask import request
import pandas as pd

# Local imports
from UpworkDownloader import search_jobs

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
     return json.dumps({'prediction': list(prediction)})

@app.route('/download', methods=['POST'])
def download():
    # search_jobs()
    return "Downloading..."

    
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)