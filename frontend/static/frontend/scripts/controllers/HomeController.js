'use strict';

/**
 * @ngdoc function
 * @name zapyle.controller:MainCtrl
 * @description
 * # HomeController Created by Albin CR
 * Controller of the zapyle
 */
 var mixPanelVar = {}
    mixPanelVar.SessionStart = Date.now() 
    mixPanelVar.UserType = 'Guest'
    mixPanelVar.UserName = null
var CurrentPage = window.location.href
    mixPanelVar.Platfrom = 'Website'
var PageStartTime = Date.now()
var no_of_products_viewed = 0
angular.module('zapyle')
    .controller('HomeController', function($route, $scope, $http, $routeParams, $localStorage, $sessionStorage, $q, $rootScope, $location) {
            $('#zap_footer').addClass('is_hidden')
            $('#zap_footer').removeClass('is_visible')

        $scope.INSTAGRAM_CLIENT_ID = INSTAGRAM_CLIENT_ID
        $scope.check_login = function
        (){
            $http.get('/user/mydetails/').
                success(function(data, status, headers, config) {
                if (data.status == "success"){
                    $localStorage.phone_number = data.data.phone_number
                    $localStorage.user_type = data.data.user_type
                    $localStorage.loggedIn = $scope.loggedIn = true
                    $localStorage.email = data.data.email || ""
                    $localStorage.full_name = data.data.full_name
                    $localStorage.zap_username = data.data.zap_username || ""
                    $localStorage.stage = data.data.profile_completed
                    $localStorage.profile_picture = data.data.profile_pic
                    $localStorage.user_id = data.data.user_id
                    $localStorage.username = data.data.username
                    $rootScope.$broadcast('parent', 'Sathyalog')
                    mixPanelVar.UserType = data.data.user_type
                    mixPanelVar.UserName = data.data.zap_username || "Guest"
                    mixpanel.identify(mixPanelVar.UserName);
                    mixpanel.register(mixPanelVar)
                    mixpanel.track("User Event", {'Event Name': 'Open App'});
                    ga('set', 'dimension3', $localStorage.zap_username );

                    if ($localStorage.stage < 5) {
                        $location.url('/onboarding')
                        return false
                    }
                }else{
                    $scope.loggedIn = false
                    $localStorage.$reset();
                    $rootScope.$broadcast('parent', 'Sathyalog')
                    mixpanel.track("User Event", {'Event Name': 'Open App'});

                    // $localStorage.loggedIn = false
                }
                

              }).
              error(function(data, status, headers, config) {
                $localStorage.$reset();
                $scope.loggedIn = false
                $rootScope.$broadcast('parent', 'Sathyalog')
                // called asynchronously if an error occurs
                // or server returns response with an error status.
              });
        }
        // if(!$localStorage.loggedIn){
            $scope.check_login()
        // }
        $rootScope.check_login_root = function (){
            $scope.check_login()
            $('#header-login').hide()
            $('#header-notlogin').show()
            $rootScope.loggedIn = false
            $route.reload();
        }
        $scope.insta_please_wait = function(){
            $('#please-wait').addClass('is_visible')
            window.location.href = "/account/instagram/" 
        }

        $scope.FBLogin = function() {

            $localStorage.$reset()
            FB.login(function(response) {
                $('#please-wait').addClass('is_visible')
                if(response.status == 'connected'){
                    var a_t = response.authResponse.accessToken
                    $http({
                        method: 'POST',
                        url: '/account/login/',
                        data: {
                            "access_token": a_t,
                            "logged_from": "fb",
                            "logged_device": "website"
                        }
                    }).then(function successCallback(response) {
                        mixpanel.track("User Event", {'Event Name': 'Logged In', 'Channel':'Fb'});

                        //alert(JSON.stringify(response))
                        $scope.check_login()
                        if(response.data.data.profile_completed == 5){

                            $location.url('/feeds')
                        }
                        //window.location = '#/onboarding'
                        // $location.url('/onboarding')
                    }, function errorCallback(response){

                    })
                }else{
                    $('#please-wait').removeClass('is_visible')
                }
            }, {scope: 'public_profile,email'});
        };
        $( window ).on('beforeunload', function() {
            var delta = Math.abs(Date.now() - mixPanelVar.SessionStart) / 1000;
            var minutes = Math.floor(delta / 60) % 60;
            delta -= minutes * 60;
            var seconds = delta % 60;
            mixpanel.track("User Event", {'Event Name': 'Close App',  'time spent on page':minutes+' minutes '+seconds+' seconds', 'number of products viewed':no_of_products_viewed});
        });
        jQuery('a').click(function (event) {
        if(event.target.id == 'btn_send'){
            send_sms()
        }
    });
    $('#txtphone_number').keypress(function(e){
        if(e.which == 13){
            send_sms()
            
        }
    })
    function send_sms(){
        $.post( "/", {'phone_number':$("#txtphone_number").val()},function( data ) {
            $('.sucess_msg').removeClass('is_visible')
            $('.error-msg').removeClass('is_visible')
            if(data.status == 'success'){
                $('.sucess_msg').addClass('is_visible')
                $('.sucess_msg').text(data['data'])
                $("#txtphone_number").val('')
                fbq('track', "LeadConversion");
            }else{
                var err = data.errors
                $('.error-msg').addClass('is_visible')
                $('.error-msg').text(err['error'])
            }
        });
    }
    });

