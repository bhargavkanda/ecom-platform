'use strict';

angular.module('zapyle')
    .controller('TokenController', function($scope, $routeParams, $http, $localStorage, $q, $rootScope) {

        if (window.location.href.indexOf("access_token") > -1) {
            var url_code = window.location.href.split("access_token")[1]
            if (url_code.length > 10) {
 
                $http({
                    method: 'jsonp',
                    url: 'https://api.instagram.com/v1/users/self/?callback=JSON_CALLBACK&&access_token' + url_code
                }).then(function successCallback(response) {
                     $localStorage.login_type = "instagram";
                    $localStorage.user_name = response.data.data.username;
                    $localStorage.profile_picture = response.data.data.profile_picture;
                    $http({
                        method: 'POST',
                        url: '/user/',
                        headers: {
                            'X-UuidKey': $localStorage.uuid_keyx,
                            'X-DeviceID': $localStorage.device_idx 
                        },
                        data: {
                            "username": response.data.data.username,
                            "logged_from": "insta",
                            "full_name": response.data.data.full_name,
                            "avatar": response.data.data.profile_picture,
                            "gcm_reg_id": "",
                            "device_id": $localStorage.device_idx 
                        }
                    }).then(function successCallback(response) {
 
                        $localStorage.loggedIn = true
                        $localStorage.id = response.data.id
                        if (response.data.zap_username == null || response.data.new_user == true) {
                            window.location = '#/onboarding'
                        } else {
                            $localStorage.info = true
                            $localStorage.zap_username = response.data.zap_username
                            $localStorage.email = response.data.email
                            $localStorage.user = response.data.new_user
                            $localStorage.loggedIn = true
                            $localStorage.id = response.data.id
                            $rootScope.$broadcast('parent', 'Sathyalog')
                        }
                    }, function errorCallback(response) {
                     });

                }, function errorCallback(response) {
                 }).then(function() {
                    if ($localStorage.user_name == null || $localStorage.user == true) {
                        window.location = '#/onboarding'
                    } else {
                        window.location.replace('#/feeds')


                    }
                });


            }
        }
 
    });
