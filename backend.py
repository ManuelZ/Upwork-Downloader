# Built-in imports
import sys
import json
import sqlite3 as sql

# External imports
from flask import Flask
from flask import request
from flask import jsonify
from flask import g # for sqlite3
import pandas as pd

DATABASE = 'jobs_db.sqlite3'

# Local imports
# from upwork_downloader import search_jobs

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
     return json.dumps({'prediction': list(prediction)})

@app.route('/download', methods=['POST'])
def download():
    # search_jobs()
    return "Downloading..."

def get_conn():
    """
    From:
    https://flask.palletsprojects.com/en/rtd/patterns/sqlite3/
    """

    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sql.connect(DATABASE)
    conn.row_factory = sql.Row
    
    return conn


@app.teardown_appcontext
def close_connection(exception):
    """ From https://flask.palletsprojects.com/en/rtd/patterns/sqlite3/ """
    conn = getattr(g, '_database', None)
    if conn is not None:
        conn.close()


@app.route('/create_table', methods=['GET', 'POST'])
def create_table():
    try:
        conn = get_conn()
        cur = conn.cursor()
        create_table_sql = """CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            snippet TEXT NOT NULL,
            job_type TEXT NOT NULL,
            budget INTEGER NOT NULL,
            job_status TEXT NOT NULL,
            category2 TEXT NOT NULL,
            subcategory2 TEXT NOT NULL,
            url TEXT NOT NULL,
            workload TEXT,
            duration TEXT,
            date_created TEXT,
            skills TEXT,
            client_feedback INTEGER,
            client_reviews_count INTEGER,
            client_jobs_posted INTEGER,
            client_payment_verification_status TEXT,
            client_past_hires INTEGER,
            client_country TEXT
        );"""
        cur.execute(create_table_sql)
        conn.commit()
        msg = 'Table created'
    except Exception as e:
        msg = 'Error when creating table'
    finally:
        return jsonify({"msg": msg})


@app.route('/add_record', methods = ['POST'])
def add_record():
    """ Modified from: https://pythonbasics.org/flask-sqlite/"""

    if request.method == 'POST':
        try:
            conn = get_conn()
            cur = conn.cursor()
            
            fields = [
                'id',
                'title',
                'snippet',
                'job_type',
                'budget',
                'job_status',
                'category2',
                'subcategory2',
                'url',
                'workload',
                'duration',
                'date_created',
                'skills',
                'client_feedback',
                'client_reviews_count',
                'client_jobs_posted',
                'client_payment_verification_status',
                'client_past_hires',
                'client_country'
            ]
            
            # Construct the SQL request
            insert_sql = "INSERT INTO jobs ({}) VALUES ({})".format(
                ','.join(fields),
                ','.join(['?'] * 19)
            )
            
            # Extract the data from the POST
            data = [request.form[f] for f in fields]

            # Execute the SQL request
            cur.execute(insert_sql, data)
            conn.commit()
            msg = "Record successfully added"
        
        except Exception as e:
            conn.rollback()
            print(e)
            msg = "Error in insert operation"
        
        finally:
            return jsonify({'msg':msg})


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)