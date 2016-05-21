from requests.sessions import Session
from collections import ChainMap
from datetime import date
from functools import reduce
import operator as op
from pprint import pformat


class LoggingSession(Session):
    def __init__(self, logger, level, *args, **kwargs):
        self._logger = logger
        self._level = level
        super().__init__(*args, **kwargs)

    def send(self, request, *args, **kwargs):
        resp = super().send(request, *args, **kwargs)
        self._logger.log(self._level, 'Sent: {}'.format(pformat(request.__dict__)))
        self._logger.log(self._level, 'Got : {}'.format(pformat(resp.__dict__)))
        return resp


class TMDB:
    _BASE_URI = 'https://api.themoviedb.org/3/{}'

    def __init__(self, api_key, session=None):
        self.api_key = api_key
        self.session = session or Session()
        self._patch_session()

    def fetch_many(self, ids):
        return [self.fetch(id) for id in ids]

    def search(self, query):
        return pull_movies(
            self.get('search/movie', params={'query': query})['results']
        )

    def fetch(self, id):
        movie = self.get('movie/{}/credits'.format(id))
        return {
            'id': id,
            'cast': pull_actor_characters(movie['cast']),
            'crew': pull_crew_jobs(movie['crew'])
        }

    def get(self, uri, *args, **kwargs):
        return self.request('GET', uri, *args, **kwargs)

    def request(self, method, uri, *args, **kwargs):
        kwargs['headers'] = {'User-Agent': 'IsThatWho?/1.0'}
        uri = self._BASE_URI.format(uri)
        resp = self.session.request(method, uri, *args, **kwargs)
        resp.raise_for_status()
        return resp.json()

    def _patch_session(self):
        self.session.params.update({'api_key': self.api_key})


class CachingTMDB(TMDB):
    def __init__(self, cache, *args, **kwargs):
        self._cache = cache
        super().__init__(*args, **kwargs)

    def search(self, query):
        query = query.lower()
        result = self._cache.get(query)
        if not result:
            result = super().search(query)
            self._cache.set(query, result)
        return result

    def fetch(self, id):
        result = self._cache.get(id)
        if not result:
            result = super().fetch(id)
            self._cache.set(id, result)
        return result


class CrewIntersector:
    def __init__(self, tmdb):
        self._tmdb = tmdb

    def intersect(self, ids):
        movies = self._tmdb.fetch_many(ids)
        return ChainMap(intersect_crews(movies), intersect_casts(movies))


def cmap(f):
    return lambda seq: map(f, seq)


def get_casts(movies):
    return map(op.itemgetter('cast'), movies)


def get_crews(movies):
    return map(op.itemgetter('crew'), movies)


def intersect_casts(movies):
    return {
        actor: {
            movie['id']: movie['cast'][actor]
            for movie in movies
        }
        for actor in common(get_casts(movies))
    }


def intersect_crews(movies):
    return {
        member: {
            movie['id']: movie['crew'][member]
            for movie in movies
        }
        for member in common(get_crews(movies))
    }


def common(crews):
    return reduce(op.and_, [set(c.keys()) for c in crews])


def pull_actor_characters(cast):
    return {c['name']: c['character'] for c in cast}


def pull_crew_jobs(cast):
    return {c['name']: c['job'] for c in cast}


def pull_movies(movies):
    return [{'title': format_movie_name(m), 'id': m['id']} for m in movies]


def format_movie_name(movie):
    if movie['release_date']:
        when = date(*map(int, movie['release_date'].split('-')))
        return '{} ({!s})'.format(movie['title'], when.year)
    return movie['title']
