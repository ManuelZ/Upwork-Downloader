# pip install httplib2 urllib3
from __future__ import print_function
import upwork
import sys
import os
from os.path import exists, isfile
import certifi
import config
import pandas as pd
import time

def fix_module_import():
    """
    The module ca_certs_locater.py from upwork isn't prepared for Windows.
    """
    module = sys.modules.get('upwork')
    module.ca_certs_locater.get = lambda: \
        os.path.abspath(certifi.where())
    sys.modules['upwork'] = module


def get_client(public_key, secret_key, oauth_access_token, oauth_access_token_secret):
    """
    Creates a full authenticated client object.
    """
    return upwork.Client(public_key,
                         secret_key,
                         oauth_access_token,
                         oauth_access_token_secret)


def get_private_info(client):
    data_dict = client.auth.get_info()
    print(data_dict["info"])


def get_categories(client):
    categories = client.provider_v2.get_categories_metadata()
    for c in categories:
        print(c["title"])
    return categories
   

def save_results_to_csv(results):
    add_header_to_csv()
    df = pd.read_csv(config.DATA_FILE)
    for result in results:
        row = craft_df_row(result)
        # Check duplicates
        if not result.get('id') in df['id'].unique():
            add_row(df, row)
    df.to_csv(config.DATA_FILE, index=False)


def add_header_to_csv():
    if not exists(config.DATA_FILE) or not isfile(config.DATA_FILE):
        with open(config.DATA_FILE, "w") as f:
            f.write(",".join(config.FIELDS_NAMES))
            f.write("\n")


def add_row(df, values):
    df.loc[len(df)] = values


def craft_df_row(result):
    row = []
    for key in config.FIELDS_NAMES:
        if key == "skills":
            row.append("; ".join(result.get(key)))
            continue
        elif len(key.split(".")) == 2:
            keys = key.split(".")
            row.append(to_unicode(result.get(keys[0]).get(keys[1])))
            continue
        row.append(to_unicode(result[key]))
    return row


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


def search_jobs(client, terms):
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

    data = {
        'q': 'machine learning',  # Terms treated with AND
        'skills': ['python'],  # Skills treated with OR
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
            time.sleep(1.5)
            results = client.provider_v2.search_jobs(data=data, page_offset="{}".format(i), page_size=100)
            if not results:
                break
            print("Fetched {} results for term '{}'".format(len(results), term))
            save_results_to_csv(results)
            if len(results) < 100:
                break


if __name__ == "__main__":
    fix_module_import()
    credentials = load_access_token()
    client = get_client(config.consumer_key,
                        config.consumer_secret,
                        **credentials)
    search_terms = ["machine learning", "python", "artificial intelligence"]
    search_jobs(client, search_terms)
