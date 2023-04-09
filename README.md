# Tipster

Tipster is a web app built with Flask, that helps you pick winners for your [AFL Tipping](#im-not-australianwhat-is-afl-tipping) competition!

## I'm not Australian...What is AFL Tipping?

I'll answer this in two parts:

### AFL

[Australian Rules Football](https://en.wikipedia.org/wiki/Australian_rules_football) is the most popular spectator sport in Australia (debatable depending where you live in Australia). [AFL](https://en.wikipedia.org/wiki/Australian_Football_League) is the highest level of competition for Australian Rules Football.

### Tipping

Tipping in Australia has nothing to do with tipping your waitress! Tipping refers to a competition where (for a particular sport) you choose which teams you think are going to win their respective games for each round (a 'tip'). For each correct 'tip' you receive a point towards your overall score. Usually you would be in a Tipping competition with your friends, family, work colleagues, etc. The person with the most tips at the end of the season is declared the winner.

## How does Tipster work?
Tipster is a web app built with Flask that can be accessed in a browser after executing `python app.py`. Tipster can also be run as a command line tool without a pretty web based interface via `python tipster.py`.

Tipster initially loads `tipster_data.csv` into a sqlite database. This csv file contains all the AFL regular season matches for seasons 2013 to 2023 inclusive. At the time of creating this web app, the 2023 season just commenced.

Tipster will then update some data for the matches in the current round and display info for the current round (there are usually 24 rounds in a regular season, and each round is made up of usually 9 matches since there are 18 teams at present). The data it updates are:
- the live odds for the upcoming matches in the current round (scraped from sportsbet.com.au)
- which team Tipster is predicting to win (based on the algorithm I have programmed within the function `tip_wizard()` in `tipster.py`)
- the winner and score for each match that completed

Via the web interface you can:
- pick any round in the current season or prior seasons, and see who's playing, what each teams' odds are, who Tipster is picking as the winner, and (if the match is already completed) the score and result.
- pick any season from 2013 to 2023, and see the same data as in prior point, but for the whole season
- view histroical tipping performance of Tipster

## What is the algorithm in `tip_wizard()`
The algorithm I have programmed is basically the mental algorithm I use when I pick tips manually:
1. Betting Odds: if the bookmakers have a heavy favourite, I will almost always pick that team straight away (unless its my favourite team who I may be more lenient on). The closer the odds are to each other for either team to win, then the less emphasis I place on odds. (eg. if team a is the favourite at $1.72 vs team b who is $2.10, I may not factor the odds that much into my decision)
2. I may give more weight to the team that is playing at their home ground, especially if it's an interestate team. By interstate, I mean teams not based in Victoria which is where the majority of AFL teams are based.
3. Each teams ladder position and any winning streaks they have currently.

## How good is the algorithm

The web app actually lets you check this yourself by clicking on `history`. This brings up Tipster's tipping perfomance for each prior AFL season from 2013. Whenever the history button is clicked, the `get_history()` function in `tipster.py` will calculate on the fly; which team it would have picked for each match in all the prior seasons in the database. This means if the algorithm settings are ever changed, the tipping performance will adjust accordingly (based on the new settings) since its calculated on the fly.

## Video Demo:  
TODO
