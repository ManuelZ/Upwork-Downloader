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
import upwork

# Local imports
from config import DATABASE
from config import SEARCH_TERMS
from config import TABLE_NAME
from upwork_downloader import load_api_key
from upwork_downloader import load_access_token
from upwork_downloader import search_jobs
from upwork_downloader import add_records


app = Flask(__name__)
CORS(app)


@app.route('/predict', methods=['POST'])
def predict():
     pass


@app.route('/download', methods=['POST'])
def download():
    api_key, api_key_secret = load_api_key()

    access_token, access_token_secret = load_access_token()
    
    client_config = upwork.Config({
        'consumer_key': api_key,
        'consumer_secret': api_key_secret,
        'access_token': access_token,
        'access_token_secret': access_token_secret
    })

    client = upwork.Client(client_config)

    # Will save jobs in a csv file defined in config.py
    jobs = search_jobs(SEARCH_TERMS)
    add_records(jobs)


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
            CREATE TABLE {} (
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
                date_created TIMESTAMP_TZ,
                skills TEXT,
                "client.feedback" INTEGER,
                "client.reviews_count" INTEGER,
                "client.jobs_posted" INTEGER,
                "client.payment_verification_status" TEXT,
                "client.past_hires" INTEGER,
                "client.country" TEXT,
                label TEXT
            )"""
        create_table_sql = create_table_sql.format(TABLE_NAME)
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
            insert_sql = "INSERT INTO {} ({}) VALUES ({})".format(
                TABLE_NAME,
                ','.join(fields),
                ','.join(['?'] * len(fields))
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


@app.route('/get_jobs', methods = ['GET'])
def get_jobs():
    if request.args:
        limit = int(request.args.get('limit'))
        limit = limit if ((limit > 0) and (limit <1e6)) else 20

        offset = int(request.args.get('offset'))
        offset = offset if (offset >= 0 and offset <1e6) else 0

        filters = request.args.get('filter', '')
        if filters != '':
            active_filter = ','.join(f'"{f.lower().title()}"' for f in filters.split(','))
        else:
            active_filter = ''
    else:
        msg = 'Missing parameters in the request'
        
        return jsonify({'msg': msg})
    
    try:
        cur = get_conn().cursor()        
        select_sql = f'SELECT * FROM {TABLE_NAME} WHERE label IN ({active_filter}) ORDER BY strftime("%Y-%m-%dT%H:%M:%SZ", date_created) DESC LIMIT {limit} OFFSET {offset}'
        cur.execute(select_sql)
        rows = cur.fetchall()
        data = [dict(row) for row in rows]
        data = sorted(data, key=lambda k: k['date_created'])
        msg = 'Success'
    
    except Exception as e:
        msg = f"Error in SELECT operation: {e}"
        print(msg)
        data = ''
    
    finally:
        return jsonify({'msg':msg, 'data':data})


@app.route('/count_jobs', methods = ['GET'])
def count_jobs():
    
    count_sql = f"SELECT COUNT(*) from {TABLE_NAME} WHERE label NOT IN ('Uncategorized')"

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(count_sql)
        rows = cur.fetchall()
        data = [dict(row) for row in rows]
        msg = data[0]['COUNT(*)']
        
    except Exception as e:
        msg = f"Error in query: {e}"
    
    finally:
        return jsonify({'msg':msg})



@app.route('/update_job', methods = ['GET', 'POST'])
def update_job():
    
    if request.args:
        id = request.args.get('id')
        label = request.args.get('label')

    update_sql = f"UPDATE {TABLE_NAME} SET label=? WHERE id=?"

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