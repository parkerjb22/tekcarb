(function() {

    var myApp = angular.module('myApp')
    
    myApp.controller("TeamViewCtrl", TeamViewCtrl)

    TeamViewCtrl.$inject = ['$routeParams', '$interval', 'TeamService']

    function TeamViewCtrl($routeParams, $interval, TeamService) {
        var vm = this
        // var player = $routeParams.id
        activate();

        function activate() {
            vm.rounds = {}

            getTeams()

            TeamService.getCurrentRound().then(function(rnd) {
                vm.rnd = parseInt(rnd, 10);

                $interval(function() {
                    getRound(vm.rnd)
                    if (vm.rnd < 6) {
                        getRound(vm.rnd + 1)
                    }
                }, 1000);
            })

            TeamService.getPlayers().then(function(players) {
                vm.players = players
            })

            vm.selectedTeam = ''
        }

        vm.updatescores = (function(){
            vm.buttonText = "Updating..."
            TeamService.updatescores().then(function() {
                getTeams()
                vm.buttonText = 'Update Scores'
            })
        })

        function getTeams(){
            for (var i=1; i<=6; i++) {
                getRound(i)
            }
        }

        function getRound(round_num){
            if (round_num >= 5){
                TeamService.getLateRoundTeams(round_num).then(function(teams) {
                    vm.rounds[round_num] = teams
                })
            } else {
                TeamService.getTeams(round_num).then(function(teams) {
                    vm.rounds[round_num] = vm.orderTeams(teams)
                })
            }
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
