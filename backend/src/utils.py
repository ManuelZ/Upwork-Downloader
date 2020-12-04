# Built-in imports
import sqlite3 as sql

# External imports
import numpy as np
import pandas as pd


# Local imports
from src.config import DATABASE
from src.config import TABLE_NAME


def to_unicode(s):
    return(unicode(s).encode('utf-8'))


def gen_parameters_from_log_space(low_value=0.0001, high_value=0.001, n_samples=5):
    """
    Generate a list of parameters by sampling uniformly from a logarithmic space
    
    E.g.
           [ x   x  x | x  x x   |  x  x x  | x  x   x ]
        0.0001      0.001       0.01       0.1         1
    
    Which will draw much more small numbers than larger ones.
    """
    a = np.log10(low_value)
    b = np.log10(high_value)
    r = np.sort(np.random.uniform(a, b, n_samples))
    return 10 ** r

def identity(x):
    """Simple identity function used in TfidfVEctorizer as passthrough"""
    return x


def load_database_data(classFilter=['Good', 'Bad', 'Maybe']):
    """ Load data from the sqlite database based on """

    try:
        cur = sql.connect(DATABASE).cursor()
        classFilter = ','.join(f'"{f}"' for f in classFilter)
        select_sql = f"SELECT * FROM {TABLE_NAME} WHERE label IN ({classFilter}) ORDER BY strftime('%Y-%m-%dT%H:%M:%SZ', date_created) DESC"
        cur.execute(select_sql)
        rows = cur.fetchall()
        names = names = [description[0] for description in cur.description]
        df = pd.DataFrame(rows, columns=names)
        return df
    
    except Exception as e:
        print(f"Error in SELECT operation: {e}")


def load_unlabeled_data():
    unlabeled = load_database_data(['Uncategorized'])
    unlabeled.date_created = pd.to_datetime(unlabeled.date_created)
    unlabeled.drop(['label'], axis=1, inplace=True)
    
    return unlabeled