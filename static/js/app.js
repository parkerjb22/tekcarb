(function(){
	'use strict';   // See note about 'use strict'; below

	var myApp = angular.module('myApp', ['ngRoute', 'ngResource', 'ui.router']);

	myApp.config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {

		$urlRouterProvider.otherwise('/bracket');

		$stateProvider
			.state('index', {
	          abstract: true,
	          views: {
	            '@' : { templateUrl: '../static/partials/layout.html' }
	          }
	        })
			.state('bracket', {
				url:"/bracket",
				views: {
					"@": { templateUrl: '../static/partials/bracket.html', controller: 'TeamViewCtrl', controllerAs: "vm" },
					"rounds@bracket": { templateUrl: "../static/partials/_rounds.html"},
					"round5@bracket": { templateUrl: "../static/partials/_round5.html"},
					"round6@bracket": { templateUrl: "../static/partials/_round6.html"},
					"playerKey@bracket": { templateUrl: "../static/partials/_player_key.html"}
				}
			});
	    }]);
})();


