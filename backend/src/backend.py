# Built-in imports
import sqlite3 as sql
import os

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
from src.upwork_downloader import insert_records_into_db
from src.upwork_downloader import get_job_invitees
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


@app.teardown_appcontext
def close_connection(exception):
    """ From https://flask.palletsprojects.com/en/rtd/patterns/sqlite3/ """
    conn = getattr(g, '_database', None)
    if conn is not None:
        conn.close()


@app.route('/predict', methods=['POST'])
def predict():
    """
    Return unlabeled jobs with a predicted class label.
    """

    body = request.get_json()

    classes_to_predict = body.get('to_predict')
    retrain = body.get('retrain', False)
    search = body.get('search', False)
    window_days = body.get('window', 2)
    
    jobs, report = predict_unlabeled_jobs(
        window_days = window_days,
        retrain     = retrain,
        n_jobs      = 20,
        to_predict  = classes_to_predict,
        search      = search
    )

    jobs = [job.to_dict() for job in jobs]
    
    return jsonify({'msg': jobs, 'report':report.to_string()})


@app.route('/download', methods=['POST'])
def download():
    """
    Download jobs via the Upwork's API.
    """
    
    try:
        api_key, api_key_secret = load_api_key()
    
    except CredentialsNotFoundError as e:
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
    insert_records_into_db(jobs)

    return jsonify({'msg':"Done"})


@app.route('/create_jobs_table', methods=['GET', 'POST'])
def create_table():
    """
    NOT USED YET
    """
    
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
                "pref_hourly_rate_min" NULL,
                "pref_hourly_rate_max" NULL,
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
    """
    Return jobs queried from the database. 
    """
    
    if request.args:
        try:
            limit = int(request.args.get('limit'))
            limit = limit if ((limit > 0) and (limit <1e6)) else 20

            offset = int(request.args.get('offset'))
            offset = offset if (offset >= 0 and offset <1e6) else 0

            filters = request.args.get('filter', '')
            
            if filters != '':
                active_filter = ','.join(
                    f'"{f.lower().title()}"' for f in filters.split(','))
            
            else:
                active_filter = ''
        
        except Exception as e:
            msg = f"Trouble when parsing the given arguments:\n{e}."
            print(msg)
            return jsonify({'msg': msg})
    
    else:
        msg = 'Missing parameters in the request.'
        
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


@app.route('/count_jobs', methods = ['POST'])
def count_jobs():
    if request.method == 'POST':

        body = request.get_json()
        
        class_filter = body.get('classFilter')
        class_filter = ','.join(f'"{k.capitalize()}"' for k,v in filter(
            lambda x: x[1], class_filter.items()
        ))
    
        count_sql = f'''
            SELECT 
                label,COUNT(*) AS count 
            FROM 
                {TABLE_NAME} 
            WHERE 
                label IN ({class_filter})
            GROUP BY 
                label
        '''

        try:
            conn = get_conn()
            cur  = conn.cursor()
            cur.execute(count_sql)
            rows = cur.fetchall()
            data = [dict(row) for row in rows]
            msg = {}
            for x in data:
                msg[x['label']] = x['count']
            
        except Exception as e:
            msg = f"Error when making the query:\n{e}"
        
        finally:
            return jsonify({'msg':msg})


@app.route('/update_job', methods = ['GET', 'POST'])
def update_job():
    """
    Update the label of a job given its id.
    """
    
    if request.args:
        jobid = request.args.get('id')
        label = request.args.get('label')
        msg   = update_job(jobid, 'label', label)
    
    else:
        msg =  "Missing parameters."

    return jsonify({'msg':msg})


@app.route('/get_invitees', methods = ['GET', 'POST'])
def get_invitees():
    """
    """

    try:
        api_key, api_key_secret = load_api_key()
    
    except CredentialsNotFoundError as e:
        return jsonify({'msg': os.listdir("./data")})        

    access_token, access_token_secret = load_access_token()
    
    client_config = upwork.Config({
        'consumer_key': api_key,
        'consumer_secret': api_key_secret,
        'access_token': access_token,
        'access_token_secret': access_token_secret
    })

    client = upwork.Client(client_config)
    
    if request.args:
        jobid = request.args.get('jobid')
        
        if jobid:
            candidates = get_job_invitees(client, jobid)
        
        return jsonify({'msg': candidates})
    
    else:
        return jsonify({'msg': "error: no jobid provided"})


# This will be used to return the react app
@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
    