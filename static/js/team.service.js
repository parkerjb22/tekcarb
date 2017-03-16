( function() {

    var myApp = angular.module('myApp')
  
    myApp.factory('TeamService', TeamService)
    
    TeamService.$inject = ['$resource']
    
    function TeamService($resource) {

	    var teamResource = $resource('api/rnd/:round', {round: "@round"}, {
			query: { method: 'GET', params: {}, isArray: true },
			get: { method: 'GET', params: {}, isArray: false }
	    })

        var playerResource = $resource('api/players', {id: "@id"}, {
            query: { method: 'GET', params: {}, isArray: true },
            get: { method: 'GET', params: {}, isArray: false }
        })

        return {
            getTeams: getTeams,
            getPlayers: getPlayers
        }

        function getTeams(round) {
            return teamResource.get({round: round}).$promise
        }

        function getPlayers() {
            return playerResource.query().$promise
        }
    }
       
})();