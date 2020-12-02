# Built-in imports
import sqlite3 as sql
import datetime

# External imports
import iso8601
import pytz
import upwork

# Local imports
from src.upwork_downloader import update_records
from src.upwork_downloader import get_jobs_by_id
from src.upwork_downloader import get_authenticated_client
from upwork.routers.jobs import profile
from src.exceptions import CredentialsNotFoundError
from src.config import FIELDS_NAMES
from src.utils import load_database_data

# Adapters:
# Python object -> text for sqlite3
def object_to_iso8601_adapter(dt):
    """
    Convert a datetime.datetime timezone-aware Python object into a string in 
    ISO8601 format.
    """
    return dt.isoformat()


# Converters:
# text from sqlite3 -> python object
def iso8601_to_object_converter(s):
    """
    Convert a string that represents an ISO8601 timestamp (ISO8601 format 
    contains timezone information) into a timezone-aware Python object.
    """
    dt = iso8601.parse_date(str(s, 'utf-8'))
    return dt


def utcnow():
    return datetime.datetime.now(tz=pytz.utc)


# sql.register_adapter(datetime.datetime, object_to_iso8601_adapter)
# sql.register_converter("timestamp_tz", iso8601_to_object_converter)

# con = sql.connect('data/jobs_db.sqlite3', detect_types=sql.PARSE_DECLTYPES)
# cur = con.cursor()

# # Test fetching of timestamps
# cur.execute("select date_created from jobs_temp")
# row = cur.fetchone()
# print(row)


# # Test insertion of timestamps
# cur.execute("insert into jobs_temp (id, title, snippet, job_type, budget, job_status, category2, subcategory2, url, date_created) values ({})".format(
#     ','.join(['?'] * 10)
#     ),
#             ("id", "title", "snippet", "job_type", "budget", "job_status", "category2", "subcategory2", "url", utcnow()))
# con.commit()
# cur.execute("select date_created from jobs_temp where id = 'id'")
# row = cur.fetchone()
# print(row)

# con.close()

def load_ids_from_file(filename):
    with open(filename) as f:
        return [line.rstrip() for line in f]


def recreate_db():
    """
    Recreate the table only to transform the date_created column, since it has
    a format that doesn't allow parsing with sqlite's strftime function.
    """

    con = sql.connect('data/jobs_db.sqlite3', detect_types=sql.PARSE_DECLTYPES)
    cur = con.cursor()

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS jobs_temp (
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
    
    cur.execute(create_table_sql)

    select_sql = "SELECT * FROM jobs"
    cur.execute(select_sql)
    rows = cur.fetchall()
    
    data = []
    for row in rows:
        row = list(row)
        # Transform the datetime that has a timezone format "+0000" into "+00:00"
        dt = iso8601_to_object_converter(row[-9].encode())
        row[-9] = object_to_iso8601_adapter(dt)
        data.append(row)


    # Construct the SQL request
    insert_sql = "INSERT INTO jobs_temp ({}) VALUES ({})".format(
        ','.join([f'"{f}"' for f in FIELDS_NAMES]),
        ','.join(['?'] * len(FIELDS_NAMES))
    )

    # Execute the SQL request
    cur.executemany(insert_sql, data)
    con.commit()

    con.close()





def update_db():
    """
    - Retrieve all the labeled jobs from the database
    - Call the profile api for each job and retrieve the features of interest
    - Update the DB with the new features
    """

    client = get_authenticated_client()
    df = load_database_data(filter=['Good', 'Bad', 'Maybe'])

    modifications = {
        "columns" : ["pref_hourly_rate_min", "pref_hourly_rate_max"],
        "ids"     : [],
        "values"  : []
    }

    disabled_profiles = []
    for idx,row in df.iterrows():
        jobid = row["id"]
        print(f"Working on job: {jobid}")        
        
        try:
            response = profile.Api(client).get_specific(jobid)
            if 'error' in response:
                print(f"Error when requesting '{jobid}':\n{response['error']['message']}\n")
                disabled_profiles.append(jobid)
            else:
                print(f"Succesful response for job '{jobid}'\n")
        
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        # op means "Original Poster"
        op    = response.get('profile', {})
        buyer = op.get('buyer', {})
        
        preferred_hourly_rate_min = op.get('op_pref_hourly_rate_min')
        if preferred_hourly_rate_min in ("", 0, "0"):
            preferred_hourly_rate_min = None

        preferred_hourly_rate_max = op.get('op_pref_hourly_rate_max')
        if preferred_hourly_rate_max in ("", 0, "0"):
            preferred_hourly_rate_max = None

        print(f"preferred_hourly_rate_min: {preferred_hourly_rate_min}")
        print(f"preferred_hourly_rate_max: {preferred_hourly_rate_max}")

        print(f"op_low_hourly_rate_all: {op.get('op_low_hourly_rate_all')}")
        print(f"op_high_hourly_rate_all: {op.get('op_high_hourly_rate_all')}")
        

        modifications['ids'].append(jobid)
        modifications['values'].append(
            (preferred_hourly_rate_min, preferred_hourly_rate_max)
        )

    print(modifications)

    # update_records(modifications)


if __name__ == "__main__":

    update_db()

    # try:
    #     api_key, api_key_secret = load_api_key()
    
    # except CredentialsNotFoundError as e:
    #     import os

    # access_token, access_token_secret = load_access_token()
    
    # client_config = upwork.Config({
    #     'consumer_key': api_key,
    #     'consumer_secret': api_key_secret,
    #     'access_token': access_token,
    #     'access_token_secret': access_token_secret
    # })

    # client = upwork.Client(client_config)
    # ids = load_ids_from_file("../data/ids.txt")
    # get_jobs_by_id(client, ids)
