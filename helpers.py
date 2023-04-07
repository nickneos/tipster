import pandas as pd
import re
import sqlite3

from datetime import datetime, timezone

YEAR = datetime.today().year
DB = "afl_tipster.db"
CSV_FILE = "tipster_data.csv"
CSV_URL = "https://gist.githubusercontent.com/nickneos/4856afa4c53150bf36b72eea66178892/raw/34790c0375b12d6edf9118712da48d16b3ec9e39/tipster_data.csv"

# Colours
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


def db_import_csv(db, csv):

    try:
        # create db if doesnt exist
        conn = sqlite3.connect(db)
        c = conn.cursor()

        # load into df
        df = pd.read_csv(csv)

        # write to sql
        df.to_sql('tbl_fixture', conn, if_exists='replace', index = False)

        conn.commit()
        c.close()

        return db

    except Exception as e:
        print(f"{FAIL}Couldn't import {csv} into {db}\n{e}{ENDC}")
        return None


def db_qry(db, sql, param=None):

    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        if param is None:
            c.execute(sql)
        else:
            c.execute(sql, param)
        result = c.fetchall()

        conn.commit()
        c.close()

        if len(result) == 1:
            if len(result[0]) == 1:
                return result[0][0]
            else:
                return result[0]
        elif len(result) > 1:
            if len(result[0]) == 1:
                tmp = []
                for x in result:
                    tmp.append(x[0])
                return tmp
            else:
                return result
        else:
            return result

    except Exception as e:
        print(f"{FAIL}{e}{ENDC}")
        return None


def db_qry_many(db, sql, param):

    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.executemany(sql, param)
        result = c.fetchall()

        conn.commit()
        c.close()

        return result

    except Exception as e:
        print(f"{FAIL}{e}{ENDC}")
        return None


def db_print(data, columns):

    if type(columns) is not list:
        columns = re.split(", ", columns)

    
    if type(data) is tuple:
        ldata = []
        ldata.append(data)
        data = ldata

    df = pd.DataFrame(data, columns=columns)

    # print df
    print(f"\n{df.to_string(index=False)}\n")


def sql_to_csv(sql_qry, csv=CSV_FILE, db=DB):
    """ Create csv from sqlite3 query """

    try:
        conn = sqlite3.connect(db)
        df = pd.read_sql_query(sql_qry, conn)
        df.to_csv(csv, index=False)
        conn.close

    except Exception as e:
        print(f"{FAIL}Couldn't update {csv}\n{e}{ENDC}")


def cleaner(list):
    """" Cleans the lists extracted from beautiful soup """

    content = []
    for li in list:
        content.append(li.getText().replace("\n", " ").replace("\t""", " "))
    # print(content)
    return content


def fix_team_name(teamname):
    """ Standardise team names """
    if teamname == "Greater Western Sydney":
        teamname = "GWS"

    return teamname


def utc_to_local(utc_dt):
    """ Converts utc datetime to local datetime"""

    if type(utc_dt) == str:
        try:
            utc_dt = datetime.fromisoformat(utc_dt)
        except:
            utc_dt = None

    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)