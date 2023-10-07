import tipster

from datetime import datetime
from flask import Flask, abort, render_template, redirect, request

# initialize
db = tipster.DB
tipster.tipster_load()
year = tipster.db_qry(db, "select coalesce(min(year), strftime('%Y', 'now')) from tbl_fixture where GameTimeUTC > current_date")
seasons = tipster.db_qry(db, "select distinct year from tbl_fixture order by 1 desc")
rounds = tipster.db_qry(db, "select distinct round from tbl_fixture where year = ? order by 1", (year,))


# Configure application
app = Flask(__name__)


@app.route("/")
def index():
    ''' Shows main page of tipster, which shows the data
        for the matches in the current round
    '''
    # get data for current round
    tipster.update_odds(db)
    tipster.update_results(db)
    data = tipster.get_current_round()
    if len(data) < 1:
        return redirect("/search")
    stats = []
    stats.append(tipster.get_stats(year))
    stats.append(tipster.get_stats(year, data[0][1]))

    return render_template(
        template_name_or_list="index.html",
        data=data,
        rounds=rounds,
        round=data[0][1],
        season=year,
        seasons=seasons,
        stats=stats
    )


@app.route("/search")
def search():
    '''Show matches based on user input'''

    # get user input
    round = int(request.args.get("r", 0))
    season = int(request.args.get("y", year))
    
    # handle invalid season/round
    if season not in seasons:
        abort(400)
    if round > 0 and round not in rounds:
        abort(400)
    
    # redirect to "/" if current round
    if round == tipster.db_qry(db, f"""
                                SELECT MIN(round) FROM tbl_fixture 
                                WHERE gametimeutc >= current_date"""):
        return redirect("/")

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
    '''Shows historical perfomance of the tipster algorithm'''

    data = tipster.get_history()
    
    return render_template(
        template_name_or_list="history.html",
        data=data,
        rounds=rounds,
        seasons=seasons
    )


@app.errorhandler(Exception)
def error(e):
    '''Shows an error page'''

    # Escape special characters.
    # https://github.com/jacebrowning/memegen#special-characters
    for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                        ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
        top = str(e.code).replace(old, new)
        bottom = e.name.replace(old, new)

    return render_template(
        template_name_or_list="error.html", 
        rounds=rounds,
        seasons=seasons,
        top=top, 
        bottom=bottom), e.code


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
