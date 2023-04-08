import tipster

from datetime import datetime
from flask import Flask, redirect, render_template, request

# Configure application
app = Flask(__name__)

db = tipster.DB
tipster.tipster_load()
year = tipster.db_qry(db, "select min(year) from tbl_fixture where GameTimeUTC > current_date")
seasons = tipster.db_qry(db, "select distinct year from tbl_fixture order by 1 desc")
rounds = tipster.db_qry(db, "select distinct round from tbl_fixture where year = ? order by 1", (year,))


@app.route("/")
def index():
    ''' Shows main page of tipster, which shows the data
        for the matches in the current round
    '''
    data = tipster.get_current_round()
    round = data[0][1]
    season = year
    stats = []
    stats.append(tipster.get_stats(season))
    stats.append(tipster.get_stats(season, round))

    return render_template(
        template_name_or_list="index.html",
        data=data,
        rounds=rounds,
        round=round,
        season=season,
        seasons=seasons,
        stats=stats
    )


@app.route("/search")
def search():
    '''Show matches based on user input'''

    round = int(request.args.get("r", 0))
    season = int(request.args.get("y", year))

    if season == 0:
        season = year

    data = tipster.get_matches(season, round)
    stats = []
    stats.append(tipster.get_stats(season))
    if round > 0:
        stats.append(tipster.get_stats(season, round))
    
    return render_template(
        template_name_or_list="index.html",
        data=data,
        rounds=rounds,
        round=round,
        season=season,
        seasons=seasons,
        stats=stats
    )


@app.route("/history")
def history():
    '''Show historical perfomance of the tipster algorithm'''

    data = tipster.get_history()
    
    return render_template(
        template_name_or_list="history.html",
        data=data,
        rounds=rounds,
        seasons=seasons
    )


### JINJA FILTERS ###

@app.template_filter()
def pretty_date(dttm):
    dttm = datetime.fromisoformat(dttm)
    d = dttm.strftime("%d").lstrip("0")
    return dttm.strftime(f"%A, %B {d} %Y %H:%M")


@app.template_filter()
def pretty_odds(odds):
    try:
        return '${:,.2f}'.format(odds)
    except TypeError:
        return ""


@app.template_filter()
def pretty_none(str):
    if str is None:
        return ""
    else:
        return str
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)