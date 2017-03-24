( function() {

    var myApp = angular.module('myApp')
  
    myApp.factory('TeamService', TeamService)
    
    TeamService.$inject = ['$resource']
    
    function TeamService($resource) {

	    var teamResource = $resource('api/rnd/:round', {round: "@round"}, {
			get: { method: 'GET', params: {}, isArray: false },
            query: { method: 'GET', params: {}, isArray: true }
	    })

        var playerResource = $resource('api/players', {id: "@id"}, {
            query: { method: 'GET', params: {}, isArray: true },
        })

        var scoreResource = $resource('api/updatescore', {id: "@id"}, {
            get: { method: 'GET', params: {}, isArray: false }
        })

        var roundResource = $resource('api/current_round', {id: "@id"}, {
            get: { method: 'GET', params: {}, isArray: false }
        })

        return {
            getTeams: getTeams,
            getLateRoundTeams : getLateRoundTeams,
            getPlayers: getPlayers,
            updatescores: updatescores,
            getCurrentRound : getCurrentRound,
        }

        function getTeams(round) {
            return teamResource.get({round: round}).$promise
        }

        function getLateRoundTeams(round) {
            return teamResource.query({round: round}).$promise
        }

        function getPlayers() {
            return playerResource.query().$promise
        }

        function updatescores() {
            return scoreResource.get().$promise
        }

        function getCurrentRound() {
            return roundResource.query().$promise
        }
    }
       
})();