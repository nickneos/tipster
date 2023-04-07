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
    '''TODO'''

    data = tipster.get_current_round()
    stats = tipster.get_stats()
    round = data[0][1]
    return render_template(
        template_name_or_list="index.html",
        data=data,
        rounds=rounds,
        round=round,
        year=year,
        seasons=seasons,
        stats=stats
    )


@app.route("/round")
def round():
    '''TODO'''

    round = int(request.args.get("r"))

    if round > 0:
        data = tipster.get_round(round)
        stats = tipster.get_stats()
        return render_template(
            template_name_or_list="index.html",
            data=data,
            rounds=rounds,
            round=round,
            year=year,
            seasons=seasons,
            stats=stats
        )
    else:
        return redirect("/season")


@app.route("/season")
def season():
    '''TODO'''

    try:
        season = int(request.args.get("y"))
    except TypeError:
        season = year

    if season not in seasons:
        season = year
        
    data = tipster.get_season(season)
    stats = tipster.get_stats(season)
    
    return render_template(
        template_name_or_list="season.html",
        data=data,
        rounds=rounds,
         round=0,
         year=season,
         seasons=seasons,
         stats=stats
    )


@app.route("/history")
def history():
    '''TODO'''

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
    app.run(host='0.0.0.0')