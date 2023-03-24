import os
import pandas as pd
import re
import sqlite3
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime, timezone


# set this to your team if you want to improve their tipping score (by the SENTIMENTAL_POINTS) so you tip them more often
SENTIMENTAL_TEAM = "Carlton"
SENTIMENTAL_POINTS = 5
USE_ODDS = True
USE_HOME_ADVANTAGE = True
USE_LADDER = False

YEAR = datetime.today().year
DB = "afl_tipster.db"
CSV_FILE = "tipster_data.csv"
CSV_URL = "https://gist.githubusercontent.com/nickneos/4856afa4c53150bf36b72eea66178892/raw/34790c0375b12d6edf9118712da48d16b3ec9e39/tipster_data.csv"
MENU = [
    "Print Current Round with Tipster's Picks",
    "Print Round (n)",
    "Simulate Prior Seasons",
    "Print Ladder",
    "Exit"
]
PRINTABLE_COLS = "GameTimeLocal, Round, HomeTeam, HomeOdds, AwayTeam, AwayOdds, Score, Result, TipstersPick, TipOutcome"

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

ASCII_ART = f'' \
    '  __  .__                __                 ' + f'\n' \
    '_/  |_|__|_____  _______/  |_  ___________  ' + f'\n' \
    '\   __\  \____ \/  ___/\   __\/ __ \_  __ \ ' + f'\n' \
    ' |  | |  |  |_> >___ \  |  | \  ___/|  | \/ ' + f'\n' \
    ' |__| |__|   __/____  > |__|  \___  >__|    ' + f'\n' \
    '         |__|       \/            \/        ' + f'\n'


def main():

    # if csv doesnt exist, download
    if not os.path.exists(CSV_FILE):
        urllib.request.urlretrieve(CSV_URL, CSV_FILE)

    # create/update db from csv
    db_import_csv(DB, CSV_FILE)

    # add local time column based on utc column
    data = []
    for row in db_qry(DB, "SELECT ID, GameTimeUTC FROM tbl_fixture "):
        data.append({
            "id": row[0],
            "datetime": utc_to_local(row[1])
        })
    db_qry_many(DB, f"UPDATE tbl_fixture SET GameTimeLocal = :datetime WHERE ID = :id", data)

    ##### USER MENU #####
    print(f"\n{HEADER}{ASCII_ART}{ENDC}\n")

    while True:
        sel = tipster_menu()

        # [MENU OPTION 1] Print current round with tipsters picks
        if sel == MENU[0]:
            option_one()

        # [MENU OPTION 2] Print selected round
        elif sel == MENU[1]:
            option_two()

        # [MENU OPTION 3] Simulate
        elif sel == MENU[2]:
            simulate()

        # [MENU OPTION 4] PRINT AFL LADDER
        elif sel == MENU[3]:
            get_afl_ladder(DB)
            db_print(DB, f"SELECT * FROM tbl_ladder")

        # [MENU OPTION EXIT]
        if sel.lower() == "exit":
            # write back to csv
            update_csv(CSV_FILE, DB, "select * from tbl_fixture")
            break


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


def db_print(db, sql):

    try:
        # Read sqlite query results into a pandas DataFrame
        conn = sqlite3.connect(db)
        df = pd.read_sql_query(sql, conn)

        # print df
        print(f"\n{df.to_string(index=False)}\n")

        conn.close()

    except Exception as e:
        print(f"\n{FAIL}Couldn't output data\n{e}\n{ENDC}")


def update_csv(csv, db, sql):
    """ Update csv from sqlite3 table """

    try:
        conn = sqlite3.connect(db)
        df = pd.read_sql_query(sql, conn)
        df.to_csv(csv, index=False)
        conn.close

    except Exception as e:
        print(f"{FAIL}Couldn't update {csv}\n{e}{ENDC}")


def update_odds(db):

    try:
        # URL for scraping AFL odds
        url = "https://www.sportsbet.com.au/betting/australian-rules/afl"

        # get that beautiful soup
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')

        #  get the round number
        round = soup.find("li", attrs={"data-automation-id": "competition-round-selector-1"}).getText()

        # get the matchs from soup
        regex = re.compile("\d+-competition-event-card")
        matches = soup.find_all("div", attrs={"data-automation-id": regex})

        # extract out time
        event_times = []
        for match in matches:
            et = match.find("span", attrs={"data-automation-id": "competition-event-card-time"})
            event_times.append(et.getText())

        # extract out odds for each market
        mkt_odds = []
        for match in matches:
            o = match.find_all("span", attrs={"data-automation-id": "price-text"})
            mkt_odds.append(cleaner(o))

        # extract out market labels
        mkt_labels = []
        for match in matches:
            mkt = match.find_all(
                "div", attrs={"data-automation-id": "market-coupon-label"})
            mkt_labels.append(cleaner(mkt))

        # extract out participants
        participants = []
        regex = re.compile("(participant-(one|two))")
        for match in matches:
            team = match.find_all("div", attrs={"data-automation-id": regex})
            participants.append(cleaner(team))

        # all lists should be same size (number of matches)
        if (len(mkt_odds) != len(mkt_labels)
            or len(mkt_odds) != len(participants)
                or len(mkt_labels) != len(participants)):
            return None

        #  reset list of matches
        matches = []

        # loop through each match
        for i in range(len(mkt_odds)):
            # get attributes of match
            teams = participants[i]
            mkts = mkt_labels[i]
            odds = mkt_odds[i]
            dt = datetime.strptime(f"{event_times[i]} {YEAR}", "%A, %d %b %H:%M %Y")

            # loop through all the betting markets for the match
            # eg. head to head, line, etc
            for j, mkt in enumerate(mkts):
                # only interested in head to head market
                if mkt.lower() == "head to head":
                    odds_home = odds[j * 2]
                    odds_away = odds[j * 2 + 1]
                    market = mkt
                    break

            # add dict to list of matches
            matches.append({
                "event_time": dt,
                "round": round,
                "home_team": fix_team_name(teams[0]),
                "away_team": fix_team_name(teams[1]),
                "market": market,
                "home_odds": odds_home,
                "away_odds": odds_away
            })


        # update sql table
        sql = '''
            UPDATE tbl_fixture
            SET HomeOdds=:home_odds, AwayOdds=:away_odds
            WHERE HomeTeam=:home_team AND AwayTeam=:away_team and Round=:round AND competition = 'HA'
                AND GameTimeUTC > CURRENT_TIMESTAMP
        '''
        db_qry_many(db, sql, matches)

        print(f"{OKGREEN}Odds updated{ENDC}")

    except Exception as e:
        print(f"\n{WARNING}Couldn't Update Odds\n{e}\n{ENDC}")

    return db


def update_results(db):

    try:

        # URL for scraping AFL results
        url = f"https://www.footywire.com/afl/footy/ft_match_list?year={YEAR}"

        # get that beautiful soup
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')

        matches = []

        regex = re.compile("((dark|light)color)")
        for s in soup.find_all("tr", attrs={"class": regex}):
            try:
                d = cleaner(s.find_all("td"))
                teams = re.findall(r"(\w{2,}( \w{2,})?)", d[1])
                home_team = teams[0][0]
                away_team = teams[1][0]
                score = d[4]

                # break out of loop if match has no score
                if score == "":
                    break

                # determine winner
                scores = re.split("-", score)

                if int(scores[0]) > int(scores[1]):
                    winner = home_team
                elif int(scores[0]) < int(scores[1]):
                    winner = away_team
                else:
                    winner = "Draw"

                match = {
                    "score": score,
                    "winner": winner,
                    "home_team": home_team,
                    "away_team": away_team,
                    "year": str(YEAR)
                }
                matches.append(match)

            except IndexError:
                continue

        sql = '''
            UPDATE tbl_fixture
            SET score=:score, result=:winner,
                tipoutcome = CASE
                    WHEN tipsterspick=:winner THEN 1
                    WHEN :winner='Draw' THEN 1
                    ELSE 0 END
            WHERE HomeTeam=:home_team AND AwayTeam=:away_team and strftime('%Y', gametimelocal)=:year AND competition = 'HA'
        '''
        db_qry_many(db, sql, matches)

        print(f"{OKGREEN}Results updated{ENDC}")

    except Exception as e:
        print(f"\n{WARNING}Couldn't Update Scores\n{e}\n{ENDC}")

    return db


def tip_wizard(match):
    """ Takes a dictionary representing a match, and returns the tipsters pick """

    team1 = match["Home_Team"]
    team2 = match["Away_Team"]
    tipster_score1 = 0
    tipster_score2 = 0

    # FACTOR 1: Odds
    if USE_ODDS:
        try:
            odds1 = float(match["Odds_Home"])
            odds2 = float(match["Odds_Away"])
        except:
            odds1 = 0
            odds2 = 0

        # calculation for determining strength (s) in the difference between the odds
        n = abs((odds1 * 100) - (odds2 * 100))
        s = (n / 20) - 1
        if s < 0:
            s = 0

        # add n to odds on favorite
        if odds1 - odds2 < 0:
            tipster_score1 += s
        else:
            tipster_score2 += s

    # FACTOR 2: Sentimental Team
    if SENTIMENTAL_TEAM is not None:
        if team1 == SENTIMENTAL_TEAM:
            tipster_score1 += SENTIMENTAL_POINTS
        elif team2 == SENTIMENTAL_TEAM:
            tipster_score2 += SENTIMENTAL_POINTS

    # FACTOR 3: Home Ground
    # note team1 is the home team
    if USE_HOME_ADVANTAGE:
        # lists of states/regions
        nsw = ["Sydney", "GWS"]
        qld = ["Brisbane", "Gold Coast"]
        vic = ["Carlton", "Collingwood", "Essendon", "Geelong", "Hawthorn",
            "Melbourne", "North Melbourne", "Richmond", "St Kilda", "Western Bulldogs"]
        sa = ["Adelaide", "Port Adelaide"]
        wa = ["West Coast", "Freemantle"]

        # interstate home teams get more added to score depending on region
        if team1 in wa and team2 not in wa:
            tipster_score1 += 3
        elif team1 in qld and team2 not in qld:
            tipster_score1 += 2
        elif team1 in sa and team2 not in sa:
            tipster_score1 += 2
        elif team1 in nsw and team2 not in nsw:
            tipster_score1 += 1

    # FACTOR 4: Ladder Position
    # TODO:

    # Return tip
    if tipster_score1 > tipster_score2:
        return team1
    elif tipster_score2 > tipster_score1:
        return team2
    else:
        return team1


def get_afl_ladder(db):
    """ Gets AFL Ladder and updates db """

    url = f"https://www.footywire.com/afl/footy/ft_ladder?year={YEAR}"

    try:
        # get ladder into df
        table = pd.read_html(url, header=0, index_col=0, attrs={"width": "998"})
        df = table[0]
        df = df.dropna(how="all")

        # write df to sql
        conn = sqlite3.connect(db)
        df.to_sql('tbl_ladder', conn, if_exists='replace', index = False)
        conn.commit()
        conn.close

        print(f"{OKGREEN}Ladder updated{ENDC}")
        return db

    except Exception as e:
        print(f"\n {FAIL}Issue getting AFL Ladder\n{e}{ENDC}")
        return None


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


def tipster_menu():
    """ Prints out user menu """

    # print menu
    for i, m in enumerate(MENU):
        print(f"{OKBLUE}[{i+1}] {m}{ENDC}")

    # get user selection
    while True:
        try:
            sel = int(input(f"\n{OKCYAN}Select option [1] to [{len(MENU)}]: {ENDC}"))
        except:
            continue
        if sel >= 1 and sel <= len(MENU):
            break

    return MENU[sel - 1]


def option_one():

    # update odds and results
    update_odds(DB)
    update_results(DB)

    # get round number that is the round in progress (or upcoming round if none in progress)
    today = datetime.today().date()
    curr_rnd =  db_qry(DB, f"SELECT MIN(round) FROM tbl_fixture WHERE gametimelocal >= ? AND competition = 'HA'", (today,))

    # # update tipster picks for current round
    for row in db_qry(DB, f"SELECT ID, {PRINTABLE_COLS} FROM tbl_fixture WHERE round = {curr_rnd} and strftime('%Y', gametimelocal) = '{YEAR}' AND competition = 'HA'"):
        match = {
            "Home_Team": row[3],
            "Odds_Home": row[4],
            "Away_Team": row[5],
            "Odds_Away": row[6]
        }
        pick = (tip_wizard(match))
        db_qry(DB, f"UPDATE tbl_fixture SET TipstersPick = ? WHERE ID = ? AND competition = 'HA'", (pick, row[0]))

    #  update csv
    update_csv(CSV_FILE, DB, "select * from tbl_fixture")

    # print current round
    db_print(DB, f"SELECT {PRINTABLE_COLS} FROM tbl_fixture WHERE round = {curr_rnd} and strftime('%Y', gametimelocal) = '{YEAR}' AND competition = 'HA'")

    # print stats
    db_print(DB, f'''
        SELECT Year as Season,
            sum(TipOutcome) as `Tip Score`,
            count(*) as `No of Matches`,
            round((sum(TipOutcome)/count(*)) * 100, 1) as `Percentage (%)`
        FROM tbl_fixture
        WHERE strftime('%Y', gametimelocal) = '{YEAR}' AND competition = 'HA' AND tipoutcome is not null
        ''')


def option_two():
    # print round n
    while True:
        try:
            n = int(input(f"{OKCYAN}Select Round [1-24]: {ENDC}"))
        except:
            continue
        if n >= 1 and n <= 24:
            break

    db_print(DB, f"SELECT {PRINTABLE_COLS} FROM tbl_fixture WHERE round = {n} and strftime('%Y', gametimelocal) = '{YEAR}' AND competition = 'HA'")


def simulate(db = DB, SeasonStart = 2013):

    for y in range(SeasonStart, YEAR):

        # for storing picks
        data = []

        # query to loop through
        sql = f'''
            SELECT ID, {PRINTABLE_COLS}
            FROM tbl_fixture
            WHERE strftime('%Y', gametimelocal) = ? AND competition = 'HA'
        '''
        # iterate through query
        for row in db_qry(db, sql, (str(y),)):
            match = {
                "Home_Team": row[3],
                "Odds_Home": row[4],
                "Away_Team": row[5],
                "Odds_Away": row[6]
            }
            pick = (tip_wizard(match))
            data.append({"pick": pick, "id": row[0]})

        # update db with picks
        sql = '''
            UPDATE tbl_fixture
            SET TipstersPick = :pick,
                TipOutcome = CASE WHEN result=:pick OR result='Draw' THEN 1 ELSE 0 END
            WHERE ID=:id AND competition='HA'
        '''
        db_qry_many(db, sql, data)

    # print stats
    db_print(db, f'''
        SELECT Year as Season,
            sum(TipOutcome) as `Tip Score`,
            count(*) as `No of Matches`,
            round((sum(TipOutcome)/count(*)) * 100, 1) as `Percentage (%)`
        FROM tbl_fixture
        WHERE competition = 'HA' AND Year < {YEAR}
        GROUP BY Year
        UNION SELECT 'Total' as Season,
            sum(TipOutcome) as `Tip Score`,
            count(*) as `No of Matches`,
            round((sum(TipOutcome)/count(*)) * 100, 1) as `Percentage (%)`
        FROM tbl_fixture
        WHERE competition = 'HA' AND Year < {YEAR}
    ''')


if __name__ == '__main__':
    main()
    # db_qry(DB, "update tbl_fixture set tipoutcome = null, tipsterspick = null where year < 2023")
    # update_csv(CSV_FILE, DB, "select * from tbl_fixture")
    # db_print(DB, "PRAGMA table_info(tbl_fixture)")