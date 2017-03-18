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

            TeamService.getPlayers().then(function(players) {
                vm.players = players
            })

            vm.selectedTeam = ''

            $interval(function() {
                getRound(1)
                getRound(2)
            }, 1000);
        }

        vm.updatescores = (function(){
            vm.buttonText = "Updating..."
            TeamService.updatescores().then(function() {
                getTeams()
                vm.buttonText = 'Update Scores'
            })
        })

        function getTeams(){
            for (var i=1; i<=4; i++) {
                getRound(i)
            }
        }

        function getRound(round_num){
            TeamService.getTeams(round_num).then(function(teams) {
                vm.rounds[round_num] = vm.orderTeams(teams)
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
