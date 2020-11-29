# Built-in imports
from os.path import exists, isfile
import re
import os
import time
import sqlite3 as sql
from datetime import datetime

# External imports
import upwork
from upwork.routers.jobs import search
from upwork.routers import metadata
from upwork.routers.jobs import profile
import pandas as pd
from pytz import timezone
import requests

# Local imports
from src import config
from src.config import SEARCH_TERMS
from src.config import MAX_ENTRIES_PER_TERM
from src.config import ENTRIES_PER_RESULT_PAGE
from src.utils import to_unicode
from src.exceptions import CredentialsNotFoundError


def load_api_key():
    try:
        with open(config.API_KEY_FILENAME, "r") as f:
            key = f.readline()[:-1]
            secret = f.readline()
        return key, secret
    except:
        raise CredentialsNotFoundError


def request_access_token():
    """ Request an Access Token and Access Token Secret """

    consumer_key, consumer_secret = load_api_key()

    client_config = upwork.Config({
        'consumer_key': consumer_key, 
        'consumer_secret': consumer_secret
    })
    
    client = upwork.Client(client_config)

    try:
        client_config.access_token
        client_config.access_token_secret
    except AttributeError:
        verifier = input(
            f'Please enter the verification code you get '
            f'following this link:\n{client.get_authorization_url()}\n\n>'
        )

        print('Retrieving keys.... ')
        # Once you receive the request token and the resource owner's authorization
        # (verifier code), you are ready to request Upwork Server an Access token
        access_token, access_token_secret = client.get_access_token(verifier)
        print('OK')

    with open(config.ACCESS_TOKEN_FILENAME, "w") as f:
        f.write(access_token+"\n")
        f.write(access_token_secret)
    
    return [access_token, access_token_secret]


def load_access_token():
    """
    Try to load an access token locally. If not available, start an OAuth flow. 
    """
    
    try:
        with open(config.ACCESS_TOKEN_FILENAME, 'r') as f:
            access_token = f.readline()[:-1]
            access_token_secret = f.readline()
    
    except IOError as strerror:
        print(f"Error loading the local secrets: {strerror}")
        access_token, access_token_secret = request_access_token()
    
    return access_token, access_token_secret


def search_jobs(client, terms):
    """
    Search jobs using the Python Upwork API based on given search terms.
    https://developers.upwork.com/?lang=python#jobs_search-for-jobs

    Args:
        client: An authenticated upwork.Client object
        terms : List of terms to use in the searches.
    
    Returns:
        List of results
    """

    final_results = []
    for term in terms:

        for i in range(0, MAX_ENTRIES_PER_TERM, ENTRIES_PER_RESULT_PAGE):
            print(f"A new loop for {term}")
            time.sleep(1.5) # Default API limit

            params = {
                'q'           : term.split(' '),  # Terms treated with AND
                'job_status'  : 'open',
                'days_posted' : config.DAYS_BACK_TO_SEARCH,
                'paging'      : f'{i};{ENTRIES_PER_RESULT_PAGE}' # offset;count
            }

            try:
                results = search.Api(client).find(params)
                jobs = results.get('jobs', [])
                # Modify the date_created so that the timezone has a format of 
                # "+00:00" instead of "+0000" since sqlite3 can only parse that
                for job in jobs:
                    job['date_created'] = datetime.strptime(
                        job['date_created'], "%Y-%m-%dT%H:%M:%S%z").isoformat()
                final_results.extend(jobs)
            
            except requests.exceptions.ConnectionError as e:
                print(f'Connection error, are you sure you have internet?')

            print(f'Fetched {len(jobs)} results for term "{term}"')

            if len(jobs) < ENTRIES_PER_RESULT_PAGE:
                break
    
    return final_results


def get_jobs_by_id(client, ids):
    """
    Return detailed profile information about the job. 
    https://developers.upwork.com/?lang=python#jobs_get-job-profile

    Args: 
        ids: List of ids
    """

    df = pd.DataFrame(columns=config.FIELDS_NAMES)
    
    def get_skills(skills):        
        if isinstance(skills, unicode):
            return skills

        skills = skills.get('op_required_skill')

        if isinstance(skills, str):
            return skills

        if isinstance(skills, dict):
            return skills.get('skill')
        
        try:
            skills = map(lambda x: x.get('skill'), skills)
        except Exception as e:
            print("@get_skills - {}, {}".format(e, response))
        
        return ";".join(list(skills))

    def get_status(status):
        if (status == 'Active'):
            status = 'Open'
        elif (status == 'Filled'):
            status = 'Closed'
        return status

    def get_verification_status(status):
        if status:
            return 'VERIFIED'
        else:
            return 'None'
    
    def get_duration(duration):
        if not duration:
            return 'None'
        return duration


    # The profile api can receive requests for up to 20 profiles. Unfortunately
    # when some of those profiles are "disabled" (I have not found any 
    # definition of that in the documentation. Even more,  the "disabled" 
    # profiles can still be accessed through the normal web interface), the
    # whole query fails.
    # That's why I'm requesting them one by one.
    disabled_profiles = []
    for id in ids:

        print(f"Job id: {id}")

        try:
            response = profile.Api(client).get_specific(id)
            if 'error' in response:
                print(f"Error when requesting '{id}':\n{response['error']['message']}\n")
                disabled_profiles.append(id)
            else:
                print(f"Succesful response for job '{id}'\n")
            continue
        
        except Exception as e:
            print(f"Error: {e}")
            continue
        
        # op means "Original Poster"
        op = response.get('profile', {})
        buyer = op.get('buyer', {})
        
        row = pd.Series([
            id,
            response.get('op_title'),
            response.get('op_description'),
            response.get('job_type'),
            response.get('amount'),
            get_status(response.get('ui_opening_status')),
            response.get('op_job_category_v2', {}).get('op_job_category_v', {}).get('groups', {}).get('group', {}).get('name'),
            response.get('op_job_category_v2', {}).get('op_job_category_v', {}).get('name'),
            "http://www.upwork.com/jobs/{}".format(id),
            response.get('workload'), # bad
            get_duration(response.get('op_eng_duration')),
            datetime.fromtimestamp(int(response.get('op_ctime'))//1000, tz=timezone('America/Lima')).strftime("%Y-%m-%dT%H:%M:%S%z"),
            get_skills(response.get('op_required_skills')),
            "{:.2f}".format(float(buyer.get('op_adjusted_score'))),
            response.get('op_tot_feedback'),
            buyer.get('op_tot_jobs_posted'),
            get_verification_status(response.get('op_cny_upm_verified')),
            buyer.get('op_tot_fp_asgs'),
            buyer.get('op_country')
        ], name=id, index=config.FIELDS_NAMES)

        df = df.append(row)
    df.set_index('id', inplace=True, drop=True)
    return df


def load_ids_from_file(filename):
    with open(filename) as f:
        return [line.rstrip() for line in f]


def add_records_to_db(records):
    """
    Insert records in sqlite3 database.

    Args:
    data: a list of tuples
    """

    # Transform the data into a list of lists
    data = []
    for record in records:
        row = []
        for field in config.FIELDS_NAMES:
            if 'client' in field:
                field = field.split('.')[1]
                value = record.get('client').get(field, '')
            else:
                value = record.get(field, '')
                if field == 'label':
                    value = 'Uncategorized'
                elif field == 'skills':
                    value = "; ".join(value)
            row.append(value)
        data.append(row)

    try:
        with sql.connect(config.DATABASE) as conn:
            cur = conn.cursor()
    
            # Insert records with id that don't exist (id is the primary key)
            insert_sql = "INSERT OR IGNORE INTO {} ({}) VALUES ({})".format(
                config.TABLE_NAME,
                ','.join(f'"{f}"' for f in config.FIELDS_NAMES),
                ','.join(['?'] * len(config.FIELDS_NAMES))
            )

            # Bulk insert
            cur.executemany(insert_sql, data)
            conn.commit()
    
    except Exception as e:
        print(e)


if __name__ == "__main__":

    api_key, api_key_secret = load_api_key()

    access_token, access_token_secret = load_access_token()
    
    client_config = upwork.Config({
        'consumer_key': api_key,
        'consumer_secret': api_key_secret,
        'access_token': access_token,
        'access_token_secret': access_token_secret
    })

    client = upwork.Client(client_config)
    jobs = search_jobs(client, SEARCH_TERMS)
    add_records_to_db(jobs)