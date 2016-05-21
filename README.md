# Is That Who I Think It Is?

A simple flask/amgular app to intersect the cast and crew of two movies
and show the common results.


Just a simple weekend project because I find myself asking this question too often.

## Install

1. Get a TMDB API key and export it into your shell under `TMDB_KEY`
2. install redis and start it
3. `pip install -r requirements`
4. Run the app (`flask --app=app run` if you're using Flask 0.10+)

## Notes
Only works with movies. Original, it also supported TV shows but TMDB has woeful
support for TV casts (seems like it only returns current/last cast instead of all
people who were on the show).
