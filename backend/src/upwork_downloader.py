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
import pandas as pd
from pytz import timezone
import requests

# Local imports
from src import config
from src.config import SEARCH_TERMS
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

    Args:
        client: An authenticated upwork.Client object
        terms : List of terms to use in the searches.
    """

    final_results = []
    for term in terms:

        for i in range(0, config.MAX_ENTRIES_PER_TERM, config.ENTRIES_PER_RESULT_PAGE):
            print(f"A new loop for {term}")
            time.sleep(1.5) # Default API limit

            params = {
                'q'           : term.split(' '),  # Terms treated with AND
                'job_status'  : 'open',
                'days_posted' : config.DAYS_BACK_TO_SEARCH,
                'paging'      : f'{i};{config.ENTRIES_PER_RESULT_PAGE}' # offset;count.
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

            if len(jobs) < config.ENTRIES_PER_RESULT_PAGE:
                break
    
    return final_results


def load_ids_from_file(filename):
    with open(filename) as f:
        return [line.rstrip() for line in f]


def add_records(records):
    """
    Insert records in sqlite3 database.
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

    # Will save jobs in a csv file defined in config.py
    jobs = search_jobs(client, SEARCH_TERMS)
    add_records(jobs)