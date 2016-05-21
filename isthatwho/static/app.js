app = angular.module('isthatwho', []);

app.config(function($interpolateProvider) {
    // change up angular's templating syntax to avoid
    // collisions with Jinja2
    $interpolateProvider.startSymbol('{a');
    $interpolateProvider.endSymbol('a}');
});

app.service('MovieSearch', ['$http', function($http) {
  return function search(query) {
    return $http.get(SEARCH + '?query=' + query);
  };
}]);

app.service('CompareCasts', ['$http', function($http) {
  function buildURL(ids) {
    return CASTS + '?movie=' + ids.join('&movie=');
  };

  return function compare(movieIds) {
    return $http.get(buildURL(movieIds));
  };
}]);


app.controller('SearchAndCompareController', ['CompareCasts', 'Searcher', function(CompareCasts, Searcher) {
  var $sac = this;
  $sac.searchers = [Searcher(), Searcher()];
  $sac.common = {};
  $sac.ready = false;
  
  $sac.addSearcher = (data) => { $sac.searchers.push(Searcher(data)) };
  $sac.removeSearcher = (idx) => { $sac.searchers.splice(idx, 1); };

  $sac.compare = () => {
    $sac.ready = false;
    $sac.ids = gatherMovieIds();

    if ($sac.ids.length > 1) {
      CompareCasts($sac.ids).then(d => {
        $sac.idsToMovies = idsToNames();
        $sac.common = d.data;
        $sac.hasResults = Object.keys($sac.common).length > 0;
        $sac.ready = true;
      });
    }

  };

  var gatherMovieIds = () => {
    return $sac.searchers.map(s => s.selected.id).filter(Boolean);
  };

  var idsToNames = () => {
    var that = {};
    $sac.searchers.forEach((s) => {
      if (s.selected.id) {
        that[s.selected.id] = s.selected.title;
      }
    });
    return that;
  };

}]);


app.factory('Searcher', ['MovieSearch', function(MovieSearch) {
  function handlePreFilled(inst, data) {
    if (typeof data === 'string') {
      inst.query = data;
      inst.find();
    } else if (data.title && data.id) {
      inst.selectMatch(data);
      inst.find();
    }
  };

  function Searcher(data) {
    var $search = this;
    $search.matches = [];
    $search.selected = {};
    $search.query = '';

    var toggled = false;

    $search.showMatches = function() {
      return $search.matches.length && toggled;
    }

    $search.toggleShowMatches = function() {
      toggled = !toggled;
    }

    $search.find = function() {
      MovieSearch($search.query).then(function(resp) {
        $search.matches = resp.data;
      });
    };

    $search.selectMatch = function(match) {
      if (!$search.selected || $search.selected.id !== match.id) {
        $search.selected = match;
        $search.query = match.title;
      } else {
        $search.selected = {};
      }
    }

    if (!!data) {
      handlePreFilled(this, data);
    }
  };

  return function(data) {
    return new Searcher(data);
  };
}]);
