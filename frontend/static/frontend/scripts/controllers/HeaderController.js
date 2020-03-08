'use strict';
angular.module('zapyle')
    .controller('HeaderController', function($rootScope, $location, $scope, $auth, $http, $routeParams, $localStorage, $sessionStorage,$route) {
        $rootScope.$on('parent', function(event, data) {
            $('#header-login').show()
            $rootScope.loggedIn = $localStorage.loggedIn
            $scope.loggedIn = $localStorage.loggedIn
            $scope.user_id = $localStorage.user_id
            $scope.zap_username = $localStorage.zap_username
            $scope.profilePic =  $localStorage.profile_picture
            $rootScope.$broadcast('dp', $scope.profilePic)
        });
        if($localStorage.loggedIn){
            $('#header-login').show()
            $scope.profilePic =  $localStorage.profile_picture
            $rootScope.loggedIn = $localStorage.loggedIn
            $scope.loggedIn = $localStorage.loggedIn
            $scope.zap_username = $localStorage.zap_username
        }
        // $scope.userId = $localStorage.id;
        // if ($localStorage.device_idx  == null) {
        //     window.location = '#/'
        // }
        // $rootScope.$on('parent', function(event, data) {
        //     $scope.status = $localStorage.loggedIn
        //     $scope.profilePic = $localStorage.profile_picture
        //     $scope.names = $localStorage.zap_username
        //      // window.location = '#/feeds'

        // });

        // $scope.status = $localStorage.loggedIn
        // $scope.profilePic = $localStorage.profile_picture
        // $scope.names = $localStorage.zap_username
 
        // if ($localStorage.uuid_keyx == null) {
        //     var device_id = Date.now();
        //     $localStorage.device_idx  = device_id;
        //     $http({
        //         method: 'POST',
        //         url: '/updateuuid/',
        //         data: {
        //             device_id: device_id
        //         }
        //     }).then(function successCallback(response) {
        //         $localStorage.uuid_keyx = response.data.uuid_key
        //             // location.reload();
        //     }, function errorCallback(response) {

        //     });

        // } // if end  of on load function

        $scope.logout = function() {
            $localStorage.$reset();
            $('#zap_footer').removeClass('is_visible')
            $('#zap_footer').addClass('is_hidden')
            $.get('/account/logout/', function(data){
                // $rootScope.check_login_root()
            $('#header-login').hide()
            $('#header-notlogin').show()
            $rootScope.loggedIn = false
            $route.reload();
                // window.location = $location.path();
            $('#zap_footer').removeClass('is_visible')
            $('#zap_footer').addClass('is_hidden')
            })
            

        }
    });
