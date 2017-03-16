(function() {

    var myApp = angular.module('myApp')
    
    myApp.controller("TeamViewCtrl", TeamViewCtrl)

    TeamViewCtrl.$inject = ['$routeParams', 'TeamService']

    function TeamViewCtrl($routeParams, TeamService) {
        var vm = this
        // var player = $routeParams.id
        activate();

        function activate() {
            vm.rounds = {}

            TeamService.getTeams(1).then(function(teams) {
                vm.rounds[1] = teams
            })
            TeamService.getTeams(2).then(function(teams) {
                vm.rounds[2] = teams
            })

            TeamService.getTeams(3).then(function(teams) {
                vm.rounds[3] = teams
            })
            TeamService.getTeams(4).then(function(teams) {
                vm.rounds[4] = teams
            })

            TeamService.getPlayers().then(function(players) {
                vm.players = players
            })

            vm.selectedTeam = ''
        }

        vm.selectTeam = (function (name) {
            if (vm.selectedTeam === name){
                vm.selectedTeam = ''
            } else {
                vm.selectedTeam = name
            }
        })
    }

})();
