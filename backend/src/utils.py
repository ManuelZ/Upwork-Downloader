import pandas as pd
import sqlite3 as sql
from src.config import DATABASE
from src.config import TABLE_NAME

def to_unicode(s):
    return(unicode(s).encode('utf-8'))


def load_database_data(filter=['Good', 'Bad', 'Maybe']):
    """ Load data from the sqlite database based on """

    try:
        cur = sql.connect(DATABASE).cursor()
        filter = ','.join(f'"{f}"' for f in filter)
        select_sql = f"SELECT * FROM {TABLE_NAME} WHERE label IN ({filter}) ORDER BY strftime('%Y-%m-%dT%H:%M:%SZ', date_created) DESC"
        cur.execute(select_sql)
        rows = cur.fetchall()
        names = names = [description[0] for description in cur.description]
        df = pd.DataFrame(rows, columns=names)
        return df
    except Exception as e:
        print(f"Error in SELECT operation: {e}")