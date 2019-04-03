# pip install httplib2 urllib3
from __future__ import print_function
import upwork
import sys
import csv
import os
from os.path import exists, isfile
import certifi
import config
import pandas as pd


def fix_module_import():
    """
    The module ca_certs_locater.py from upwork isn't prepared for Windows.
    :return:
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
    return(categories)


def search_jobs(client):
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
        'q': 'machine learning',
        'skills': ['R', 'python'],
        'job_status': 'open',
        'days_posted': 7
        }
    # data = {'q': 'python', 'skills': ['R', 'python']}

    # data = {
    #         #multiple skills are used as with AND
    #         'q': ['machine'],
    #
    #         #only searches in ONE category at a time, the last one
    #         #'category2':[#'Data Science & Analytics',
    #                      #'Engineering & Architecture',
    #                      #'Web, Mobile & Software Dev',
    #                      #'IT & Networking'
    #                      #],
    #
    #         #add skills, they are treated with OR
    #         'skills': ['python'],
    #         #doesn't work
    #         #'posted_since': 1,
    #         }

    # data = {'q': [
    #               'process',
    #               'management',
    #               'six sigma',
    #               'lean manufacturing'
    #               ],

    #'category2':['Data Science & Analytics',
                                                         #'Engineering & Architecture',
                                                         #'Web, Mobile & Software Dev',
                                                         #'IT & Networking'
    #                                                   ]
    #      }

    for i in range(0, 300, 100):
        results = client.provider_v2.search_jobs(data=data,
                                                 page_offset="{}".format(i),
                                                 page_size=100
                                                 )

        fieldnames = ['title', 'snippet', 'budget', 'job_status',
                      'category2', 'subcategory2', 'job_type', 'url',
                      'date_created', 'id', 'skills']

        if not exists(config.data_file) or not isfile(config.data_file):
            with open(config.data_file, "w") as f:
                f.write(",".join(fieldnames))
                f.write("\n")

        df = pd.read_csv(config.data_file)

        with open(config.data_file, "a") as csvfile:
            for result in results:
                row = craft_df_row(fieldnames, result)
                addRow(df, row)

                writer = csv.DictWriter(csvfile,
                                        fieldnames=fieldnames,
                                        delimiter=',',
                                        quotechar='"',
                                        quoting=csv.QUOTE_ALL,
                                        lineterminator='\n'
                                        )

                row = craft_row(fieldnames, result)
                writer.writerow(row)

        print(len(results))
    print(df.shape)



def addRow(df, values):
    df.loc[len(df)] = values

def craft_df_row(fieldnames, result):
    row = []
    for key in fieldnames:
        if key == "skills":
            row.append("; ".join(result[key]))
            continue
        row.append(toUni(result[key]))
    return row

def craft_row(fieldnames, result):
    row = {}
    for key in fieldnames:
        if key == "skills":
            row[key] = "; ".join(result[key])
            continue
        row[key] = toUni(result[key])
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
        #call the function which handles the token request,
        #also writes it to a file
        access_token, access_token_secret = get_access_token()
    return {'oauth_access_token': access_token, 'oauth_access_token_secret': access_token_secret}


def toUni(s):
    return(unicode(s).encode('utf-8'))


if __name__ == "__main__":
    fix_module_import()
    credentials = load_access_token()
    client = get_client(config.consumer_key,
                        config.consumer_secret,
                        **credentials)
    search_jobs(client)
