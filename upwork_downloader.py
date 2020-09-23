# Built-in imports
from __future__ import print_function
from os.path import exists, isfile
import re
import os
import sys
import time
import certifi
from datetime import datetime

# External imports
import upwork
import pandas as pd
from pytz import timezone
from pytz import all_timezones

# Local imports
import config
from utils import to_unicode


def fix_module_import():
    """
    The module ca_certs_locater.py from upwork isn't prepared for Windows.
    """
    module = sys.modules.get('upwork')
    module.ca_certs_locater.get = lambda: \
        os.path.abspath(certifi.where())
    sys.modules['upwork'] = module


def get_client(public_key, secret_key, oauth_access_token, oauth_access_token_secret):
    """ Create a full authenticated client object. """

    return upwork.Client(
        public_key,
        secret_key,
        oauth_access_token,
        oauth_access_token_secret
    )


def safe_load_data_file():
    """ Load jobs data """

    if not isfile(config.DATA_FILE):
        print("CSV doesn't exist, creating one...")
        df = pd.DataFrame(columns=config.FIELDS_NAMES)
    
    else:
        print("CSV exists, reading data and appending...")
        df = pd.read_csv(config.DATA_FILE, 
                         names=config.FIELDS_NAMES, 
                         header=0,
                         index_col=0)
        df.reset_index(inplace=True, drop=False)

    return df
   

def save_results_to_csv(results):
    df = safe_load_data_file()
    df.set_index('id', inplace=True, drop=False)

    for result in results:
        if not result['id'] in df.index:
            row = craft_df_row(result)
            df = df.append(row)

    df.reset_index(inplace=True, drop=True)
    df.to_csv(config.DATA_FILE, index=False)


def craft_df_row(result):
    """ Return a Pandas Series with name and column index """
    
    row = []
    for key in config.FIELDS_NAMES:
        if key == 'skills':
            row.append("; ".join(result[key]))
            continue
             
        elif len(key.split(".")) == 2:
            key1, key2 = key.split(".")
            client = result.get(key1)
            client_property = client.get(key2)
            
            if key == 'client.feedback':
                client_property = "{:.2f}".format(client_property)
            
            row.append(to_unicode(client_property))
            continue

        row.append(to_unicode(result[key]))
    
    return pd.Series(row, name=result['id'], index=config.FIELDS_NAMES)


def load_api_key():
    try:
        with open(config.API_KEY_FILENAME, "r") as f:
            key = f.readline()[:-1]
            secret = f.readline()
        return key, secret
    except:
        print("Can't load the API key.")

def request_access_token():
    """ Request an Access Token and Access Token Secret """

    api_key, api_key_secret = load_api_key()
    client = upwork.Client(api_key, api_key_secret)
    request_token, request_token_secret = client.auth.get_request_token()

    oauth_verifier = raw_input(
        'Please enter the verification code you get '
        'following this link:\n{0}\n\n'.format(client.auth.get_authorize_url()))

    # Once you receive the request token and the resource owner's authorization
    # (verifier code), you are ready to request Upwork Server an Access token
    access_token, access_token_secret = client.auth.get_access_token(oauth_verifier)

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
        print("EXCEPTION! {}".format(strerror))
        access_token, access_token_secret = request_access_token()
    
    return {
        'oauth_access_token': access_token,
        'oauth_access_token_secret': access_token_secret
    }


def search_jobs(terms):
    """ Search and save jobs """
    
    # At least one of the `q`, `title` or `skills` parameters required
    data = {
        # Search for the title of the job's profile
        # 'title': '',
        #
        # The search query
        'q': '',  # Terms treated with AND
        #
        # Search for skills in the job's profile
        # 'skills': ['python'],  # Skills treated with OR
        #
        'job_status': 'open',
        #
        'days_posted': config.DAYS_BACK_TO_SEARCH,
        # 'category2': [ # only searches in ONE category at a time, the last
        #     'Data Science & Analytics',
        #     'Engineering & Architecture',
        #     'Web, Mobile & Software Dev',
        #     'IT & Networking'
        # ],
        }

    for term in search_terms:
        data['q'] = term

        for i in range(0, config.MAX_ENTRIES_PER_TERM, config.ENTRIES_PER_RESULT_PAGE):
            time.sleep(1.5) # Default API limit
            
            results = client.provider_v2.search_jobs(
                data=data,
                page_offset="{}".format(i),
                page_size=config.ENTRIES_PER_RESULT_PAGE
            )

            if results:
                print("Fetched {} results for term '{}'".format(len(results), term))
                save_results_to_csv(results)
                if len(results) < config.ENTRIES_PER_RESULT_PAGE:
                    break


def get_jobs_by_id(ids):
    """
    Return detailed profile information about the job. 
    This method returns an exhaustive list of attributes associated with the job.
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

    for id in ids:
        print("Going for id {}".format(id))
        try:
            response = client.job.get_job_profile(id)
        except upwork.exceptions.HTTP403ForbiddenError:
            continue
        buyer = response.get('buyer', {})
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


def get_jobs_from_ids(ids_filename):
    """ """

    df = safe_load_data_file()
    df.set_index('id', inplace=True)

    ids = load_ids_from_file(ids_filename)
    good_jobs = get_jobs_by_id(ids)

    df = pd.concat([df, good_jobs], axis=0)
    
    # Remove duplicates
    # df = df.loc[~df.index.duplicated(keep='first')]

    df.reset_index(inplace=True)

    df.to_csv(config.DATA_FILE, index=False, encoding='utf-8-sig')


if __name__ == "__main__":
    fix_module_import()

    api_key, api_key_secret = load_api_key()

    credentials = load_access_token()
    
    client = get_client(
        api_key,
        api_key_secret,
        **credentials
    )
    
    search_terms = [
        'machine learning',
        'python',
        'artificial intelligence',
        'opencv',
        'time series',
        'computer vision'
    ]
    
    # Will save jobs in a csv file defined in config.py
    search_jobs(search_terms)
    
    # get_jobs_from_ids('data/ids.txt')    
