from .tmdb import CachingTMDB, CrewIntersector, LoggingSession
from .cache import Cache
from redis import StrictRedis
from flask import Flask, jsonify, request, render_template
from os import environ
from flask_bootstrap import Bootstrap
import logging


logging.basicConfig(filename='isthatwho.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

cache = Cache(StrictRedis('localhost', 6379, db=0), prefix='tmdb')
tmdb = CachingTMDB(
    cache=cache,
    api_key=environ['TMDB_KEY'],
    session=LoggingSession(logger, logging.DEBUG)
)
credits = CrewIntersector(tmdb)

app = Flask(__name__)
Bootstrap(app)


@app.after_request
def allow_cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS, PUT'
    resp.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
    return resp


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/search/')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify([])

    return jsonify(tmdb.search(query))


@app.route('/compare/')
def compare():
    movie_ids = request.args.getlist('movie', int)

    if not movie_ids:
        return jsonify({})

    return jsonify(dict(credits.intersect(movie_ids)))
