# Built-in imports
import sys
import json
import sqlite3 as sql

# External imports
from flask import Flask
from flask import request
from flask import jsonify
from flask import g # for sqlite3
from flask_cors import CORS
import pandas as pd

DATABASE = 'jobs_db.sqlite3'

# Local imports
# from upwork_downloader import search_jobs

app = Flask(__name__)
CORS(app)

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


@app.route('/create_jobs_table', methods=['GET', 'POST'])
def create_table():
    try:
        conn = get_conn()
        cur = conn.cursor()
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS jobs (
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
                "client.feedback" INTEGER,
                "client.reviews_count" INTEGER,
                "client.jobs_posted" INTEGER,
                "client.payment_verification_status" TEXT,
                "client.past_hires" INTEGER,
                "client.country" TEXT,
                label TEXT
            )"""
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
                'client.feedback',
                'client.reviews_count',
                'client.jobs_posted',
                'client.payment_verification_status',
                'client.past_hires',
                'client.country'
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


@app.route('/get_all_jobs', methods = ['GET'])
def get_all_jobs():
    if request.args:
        limit = int(request.args.get('limit'))
        limit = limit if ((limit > 0) and (limit <1e6)) else 20

        offset = int(request.args.get('offset'))
        offset = offset if (offset >= 0 and offset <1e6) else 0
    try:
        cur = get_conn().cursor()        
        select_sql = f"SELECT * FROM jobs LIMIT {limit} OFFSET {offset}"
        cur.execute(select_sql)
        rows = cur.fetchall()
        data = [dict(row) for row in rows]
        msg = 'Success'
    
    except Exception as e:
        msg = f"Error in SELECT operation: {e}"
        print(msg)
        data = ''
    
    finally:
        return jsonify({'msg':msg, 'data':data})

@app.route('/update_job', methods = ['GET', 'POST'])
def update_job():
    
    if request.args:
        id = request.args.get('id')
        label = request.args.get('label')

    update_sql = "UPDATE jobs SET label=? WHERE id=?"

    try:
        conn = get_conn()
        cur = conn.cursor()        
        cur.execute(update_sql, (label, id))
        conn.commit()

        if cur.rowcount < 1:
            msg = 'Failed to update, does that id exist? (msg by Manuel)'
        else:
            msg = 'Success'

    except Exception as e:
        msg = f"Error in UPDATE operation: {e}"
        print(msg)
    
    finally:
        return jsonify({'msg':msg})


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)