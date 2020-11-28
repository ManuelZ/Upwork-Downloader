# Built-in imports
import sqlite3 as sql

# External imports
from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template, send_from_directory
from flask import g # for sqlite3
from flask_cors import CORS
import upwork

# Local imports
from src.config import DATABASE
from src.config import SEARCH_TERMS
from src.config import TABLE_NAME
from src.config import TIMESTAMP_FORMAT
from src.upwork_downloader import load_api_key
from src.upwork_downloader import load_access_token
from src.upwork_downloader import search_jobs
from src.upwork_downloader import add_records
from src.learner import predict_unlabeled_jobs
from src.exceptions import CredentialsNotFoundError


app = Flask(
    __name__, 
    template_folder = "../..//upwork-downloader-ui/build",
    static_folder   = "../../upwork-downloader-ui/build/static",
)

CORS(app)


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


@app.route('/predict', methods=['POST'])
def predict():
    body = request.get_json()
    retrain = True if body.get('retrain') == "true" else False
    window_days = body.get('window', 2)
    jobs, report = predict_unlabeled_jobs(retrain=retrain, n_jobs=20, window_days=window_days)
    jobs = [job.to_dict() for job in jobs]
    return jsonify({'msg': jobs, 'report':report.to_string()})


@app.route('/download', methods=['POST'])
def download():
    try:
        api_key, api_key_secret = load_api_key()
    except CredentialsNotFoundError as e:
        import os
        return jsonify({'msg': os.listdir("./data")})        

    access_token, access_token_secret = load_access_token()
    
    client_config = upwork.Config({
        'consumer_key': api_key,
        'consumer_secret': api_key_secret,
        'access_token': access_token,
        'access_token_secret': access_token_secret
    })

    client = upwork.Client(client_config)

    jobs = search_jobs(client, SEARCH_TERMS)
    add_records(jobs)

    return jsonify({'msg':"Done"})


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


@app.route('/get_jobs', methods = ['GET'])
def get_jobs():
    if request.args:
        try:
            limit = int(request.args.get('limit'))
            limit = limit if ((limit > 0) and (limit <1e6)) else 20

            offset = int(request.args.get('offset'))
            offset = offset if (offset >= 0 and offset <1e6) else 0

            filters = request.args.get('filter', '')
            if filters != '':
                active_filter = ','.join(f'"{f.lower().title()}"' for f in filters.split(','))
            else:
                active_filter = ''
        except Exception as e:
            msg = f"Trouble when parsing the given arguments:\n{e}"
            print(msg)
            return jsonify({'msg': msg})
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

# This will be used to return the react app
@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
    