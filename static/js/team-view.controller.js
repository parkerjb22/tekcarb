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

            getTeams()

            vm.selectedTeam = ''
        }

        vm.updatescores = (function(){
            TeamService.updatescores().then(function() {
                getTeams()
            })
        })

        function getTeams(){
            TeamService.getTeams(1).then(function(teams) {
                vm.rounds[1] = vm.orderTeams(teams)
            })
            TeamService.getTeams(2).then(function(teams) {
                vm.rounds[2] = vm.orderTeams(teams)
            })
            TeamService.getTeams(3).then(function(teams) {
                vm.rounds[3] = vm.orderTeams(teams)
            })
            TeamService.getTeams(4).then(function(teams) {
                vm.rounds[4] = vm.orderTeams(teams)
            })

            TeamService.getPlayers().then(function(players) {
                vm.players = players
            })
        }

        vm.orderTeams = (function(teams){
            var round = {}
            round['EAST'] = teams['EAST']
            round['WEST'] = teams['WEST']
            round['MIDWEST'] = teams['MIDWEST']
            round['SOUTH'] = teams['SOUTH']
            return round
        })

        vm.selectTeam = (function (name) {
            if (vm.selectedTeam === name){
                vm.selectedTeam = ''
            } else {
                vm.selectedTeam = name
            }
        })
    }

})();
