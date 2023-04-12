# Tipster
- [Tipster](#tipster)
  - [Overview](#overview)
  - [I'm not Australian...What is AFL Tipping?](#im-not-australianwhat-is-afl-tipping)
  - [How does Tipster work?](#how-does-tipster-work)
  - [What is the algorithm in `tip_wizard()`](#what-is-the-algorithm-in-tip_wizard)
  - [Can the algorithm be changed?](#can-the-algorithm-be-changed)
  - [How good is the algorithm?](#how-good-is-the-algorithm)
  - [Key files in this repo:](#key-files-in-this-repo)
    - [app.py](#apppy)
    - [tipster.py](#tipsterpy)
    - [helpers.py](#helperspy)
    - [wsgi.py](#wsgipy)
    - [tipster.db](#tipsterdb)
    - [tipster\_data.csv](#tipster_datacsv)
    - [static/](#static)
    - [templates/](#templates)
  - [Video Demo:](#video-demo)


## Overview

Tipster is a web app built with Flask, that helps you pick winners for your [AFL Tipping](#im-not-australianwhat-is-afl-tipping) competition!

I created this as part of my [Final Project](https://cs50.harvard.edu/x/2023/project/) submission for [CS50x](https://cs50.harvard.edu/x/2023/)

## I'm not Australian...What is AFL Tipping?

Firstly [AFL](https://en.wikipedia.org/wiki/Australian_Football_League) refers to the Australian Football League. Think of it as the NBA or NFL of [Australian Rules Football](https://en.wikipedia.org/wiki/Australian_rules_football). AFL is the most popular spectator sport in Australia (debatable depending where you live in Australia). 

Secondly **Tipping** in Australia has nothing to do with tipping your waitress! Tipping refers to a competition where (for a particular sport) you choose which teams you think are going to win their respective games for each round of the season (a "tip"). For each correct "tip" you receive a point towards your overall score. Usually you would be in a Tipping competition with your friends, family, work colleagues, etc. The person with the most tips at the end of the season is declared the winner.

## How does Tipster work?
Tipster is a web app built with Flask that can be accessed in a browser after executing `python app.py`. Tipster can also be run as a command line tool without a pretty web based interface via `python tipster.py`.

Tipster initially loads `tipster_data.csv` into a SQLite database. This csv file contains all the AFL regular season matches for seasons 2013 to 2023 inclusive. At the time of creating this web app, the 2023 season just commenced.

Tipster will then update some data (within the SQLite database) for the matches in the current round and display info for the current round (there are usually 24 rounds in a regular season, and each round is made up of usually 9 matches since there are 18 teams at present). The data it updates are:
- the live odds for the upcoming matches in the current round (scraped from [sportsbet.com.au](https://www.sportsbet.com.au/) using [Beautiful Soup](https://pypi.org/project/beautifulsoup4/))
- which team Tipster is predicting to win (based on the algorithm I have programmed within the function `tip_wizard()` in `tipster.py`)
- the winner and score for each match that completed

Via the web interface you can:
- Pick any round in the current season or prior seasons, and see who's playing, what each teams' odds are, who Tipster is picking as the winner, and (if the match is already completed) the score and result.
- Pick any season from 2013 to 2023, and see the same data as in prior point, but for the whole season
- view historical tipping performance of Tipster

## What is the algorithm in `tip_wizard()`
The algorithm I have programmed is basically the mental algorithm I use when I pick tips manually:
1. Betting Odds: if the bookmakers have a heavy favorite, I will almost always pick that team straight away (unless it's my favorite team who I may be more lenient on). The closer the odds are to each other for either team to win, then the less emphasis I place on odds. (e.g. if Team A is the favorite at $1.72 vs team b who is $2.10, I may not factor the odds that much into my decision)
2. I may give more weight to the team that is playing at their home ground, especially if it's an interstate team. By interstate, I mean teams not based in Victoria which is where the majority of AFL teams are based.
3. Each teams ladder position and any winning streaks they have currently.

## Can the algorithm be changed?
In `tipster.py`, there are some global variables that are used by the algorithm which can be adjusted as desired. 

For a future release I would like to move these global variable to a `settings.json` file for example, and potentially have functionality in the web app to change these settings.

## How good is the algorithm?

The web app actually lets you check this yourself by clicking on `history`. This brings up Tipster's tipping performance for each prior AFL season from 2013. Whenever the history button is clicked, the `get_history()` function in `tipster.py` will calculate on the fly; which team it would have picked for each match in all the prior seasons in the database. This means if the algorithm settings are ever changed, the tipping performance will adjust accordingly (based on the new settings) since it's calculated on the fly.

## Key files in this repo:

### app.py

This is the flask app serving the web frontend for Tipster.

It handles 3 routes (`/`, `/search` and `/history`); the error handling for the website; and some custom jinja function for the template files.

### tipster.py

This is the main python backbone of Tipster. It contains all the functions that process the tipster database, scrapes websites for match results and odds, queries the database for matches, calculates who to tip for upcoming matches, etc. It also contains a command line interface so that this python script can be run in a terminal independently of the flask app frontend.

### helpers.py

Some helpful functions that `tipster.py` uses.

### wsgi.py

Needed only when self-hosting this web app with [gunicorn](https://gunicorn.org/).

### tipster.db

The SQLite database that contains the table for storing all the Tipster backend data.

The schema is as follows:

```sql
CREATE TABLE IF NOT EXISTS "tbl_fixture" (
"ID" INTEGER,
  "Year" INTEGER,
  "Competition" TEXT,
  "Round" INTEGER,
  "GameTimeUTC" TEXT,
  "GameTimeLocal" TEXT,
  "HomeTeam" TEXT,
  "AwayTeam" TEXT,
  "Ground" TEXT,
  "Score" TEXT,
  "Result" TEXT,
  "HomeOdds" REAL,
  "AwayOdds" REAL,
  "TipstersPick" TEXT,
  "TipOutcome" INTEGER
);
```

### tipster_data.csv

The initial dataset that is loaded into the database.

### static/

This folder contains the JavaScript and CSS files used by the web application.

### templates/

Contains the HTML files used by the web application.


## Video Demo:  
TODO
