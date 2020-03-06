# Built-in imports
from __future__ import print_function
from os.path import exists, isfile
import os
import sys
import certifi
import time
import re

# External imports
import upwork
import pandas as pd
# pip install httplib2 urllib3

# Local imports
import config

def fix_module_import():
    """
    The module ca_certs_locater.py from upwork isn't prepared for Windows.
    """
    module = sys.modules.get('upwork')
    module.ca_certs_locater.get = lambda: \
        os.path.abspath(certifi.where())
    sys.modules['upwork'] = module


def get_client(public_key, secret_key, oauth_access_token, oauth_access_token_secret):
    """ Creates a full authenticated client object. """
    return upwork.Client(public_key, secret_key, oauth_access_token, oauth_access_token_secret)


def get_private_info(client):
    data_dict = client.auth.get_info()
    print(data_dict["info"])


def get_categories(client):
    categories = client.provider_v2.get_categories_metadata()
    return [to_unicode(c['title']) for c in categories]

   
def save_results_to_csv(results):
    if not isfile(config.DATA_FILE):
        print("CSV doesn't exist, creating...")
        df = pd.DataFrame(columns=config.FIELDS_NAMES)
    else:
        print("CSV exists, reading data and appending...")
        df = pd.read_csv(config.DATA_FILE, names=config.FIELDS_NAMES, header=0, index_col=0)
        df.reset_index(inplace=True)

    for result in results:
        if not result['id'] in df.index:
            row = craft_df_row(result)
            df = df.append(row)
    df.to_csv(config.DATA_FILE, index=False)


def craft_df_row(result):
    row = []
    for key in config.FIELDS_NAMES:
        if key == 'skills':
            row.append("; ".join(result[key]))
            continue
        
        elif key == 'snippet':
             result[key] = re.sub('\s+', ' ', result[key])
             
        elif len(key.split(".")) == 2:
            key1, key2 = key.split(".")
            client = result.get(key1)
            client_property = client.get(key2)
            if key == 'client.feedback':
                client_property = "{:.2f}".format(client_property)
            row.append(to_unicode(client_property))
            continue

        elif key == 'class':
            row.append('')
            continue

        row.append(to_unicode(result[key]))
    
    return pd.Series(row, name=result['id'], index=config.FIELDS_NAMES)


def get_access_token():
    """
    Obtains an Access Token and Secret.
    """

    #public key, secret key
    client = upwork.Client(config.consumer_key, config.consumer_secret)
    request_token, request_token_secret = client.auth.get_request_token()

    oauth_verifier = raw_input(
        'Please enter the verification code you get '
        'following this link:\n{0}\n\n> '.format(client.auth.get_authorize_url()))

    #Once you receive the request token and the resource owner's authorization
    #(verifier code), you are ready to request Upwork Server an Access token
    (access_token, access_token_secret) = client.auth.get_access_token(oauth_verifier)

    with open("access_token", "w") as f:
        f.write(access_token+"\n")
        f.write(access_token_secret)

    return [access_token, access_token_secret]


def load_access_token():
    try:
        with open("access_token", "r") as f:
            access_token = f.readline()[0:-1]
            access_token_secret = f.readline()

    except IOError as strerror:
        print("EXCEPTION! {}".format(strerror))
        access_token, access_token_secret = get_access_token()
    return {
        'oauth_access_token': access_token,
        'oauth_access_token_secret': access_token_secret
    }


def to_unicode(s):
    return(unicode(s).encode('utf-8'))


def search_jobs(terms):
    """
    Categories:

        Web, Mobile & Software Dev
        IT & Networking
        Data Science & Analytics
        Engineering & Architecture
        Design & Creative
        Writing
        Translation
        Legal
        Admin Support
        Customer Service
        Sales & Marketing
        Accounting & Consulting
    """
    
    # At least one of the `q`, `title`, `skill` parameters should be specified.
    data = {
        # Searches for the title of the job's profile. 
        # 'title': '',
        # The search query.
        'q': '',  # Terms treated with AND
        # Searches for skills in the job's profile
        # 'skills': ['python'],  # Skills treated with OR
        'job_status': 'open',
        'days_posted': 7,
        # 'category2': [ # only searches in ONE category at a time, the last
        #     'Data Science & Analytics',
        #     'Engineering & Architecture',
        #     'Web, Mobile & Software Dev',
        #     'IT & Networking'
        # ],
        }

    for term in search_terms:
        data['q'] = term

        for i in range(0, config.MAX_ENTRIES_PER_TERM, 100):
            time.sleep(1.5) # Default API limit
            results = client.provider_v2.search_jobs(data=data, page_offset="{}".format(i), page_size=100)
            if results:
                print("Fetched {} results for term '{}'".format(len(results), term))
                save_results_to_csv(results)
                if len(results) < 100:
                    break


def get_jobs_by_id(ids):
    """Return detailed profile information about the job. This method returns an exhaustive list of attributes associated with the job.
    """
    for id in ids:
        response = client.job.get_job_profile(id)
        print(response)
        break


if __name__ == "__main__":
    fix_module_import()
    credentials = load_access_token()
    client = get_client(config.consumer_key,
                        config.consumer_secret,
                        **credentials)
    search_terms = ['machine learning',
                    'python',
                    'artificial intelligence',
                    'opencv',
                    'time series',
                    'computer vision'
                  ]
    
    search_jobs(search_terms)
    # get_jobs_by_id(['~01ed772583214ce5c4'])
