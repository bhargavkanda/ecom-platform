var zapyleAdmin = angular.module('zapyleAdmin',[
             'ngCookies',
             'ngResource',
             'ngRoute',
             'ngtouch',
             'satellizer',
             'ngStorage', 
             'ngMessages',
             'angular-img-cropper'
	]);
	zapyleAdmin.config(function($routeProvider,$httpProvider,$interpolateProvier){
		$interpolateProvider.startSymbol('[[').endSymbol(']]');
		$httpProvider.defaults.xsrfCookieName = 'csrftoken';
		$httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
		$httpProvider.defualts.headers.common["X-Requested-Width"] = 'XMLHttpRequest';
	});
    zapyleAdmin.controller('myCtrl',function($scope,$http,$location,$localStorage){
		$scope.confirm_with_seller = function(){
			
		}
	});

	zapyleAdmin.controller('iCtrl',function($scope,$http,$location,$localStorage){
		$scope.cancel_order = function(){
			cancelled = true;
		}
	});
	zapyleAdmin.controller('AdminCtrl',function($scope,$http,$location,$localStorage){
		$scope.confirm_with_buyer = function(){

		}
	})