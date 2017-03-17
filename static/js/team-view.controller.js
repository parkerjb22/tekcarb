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

            TeamService.getPlayers().then(function(players) {
                vm.players = players
            })

            vm.selectedTeam = ''
            vm.buttonText = 'Update Scores'
        }

        vm.updatescores = (function(){
            vm.buttonText = "Updating..."
            TeamService.updatescores().then(function() {
                getTeams()
                vm.buttonText = 'Update Scores'
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
