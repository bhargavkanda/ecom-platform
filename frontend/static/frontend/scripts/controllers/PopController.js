'use strict';

/**
 * @ngdoc function
 * @name zapyle.controller:MainCtrl
 * @description
 * # HomeController Created by Albin CR
 * Controller of the zapyle
 */

angular.module('zapyle')
    .controller('titleCtrl', function($scope, $rootScope) {
        $rootScope.base_url = base_url
})

angular.module('zapyle')
    .controller('PopController', function($location,$scope, $auth, $http, $routeParams, $localStorage, $sessionStorage, $q, $rootScope) {
        $scope.reset_token= $location.search()['q']
        if(!$location.search()['q']){
            $scope.reset_token=''
        }
        if($location.search()['action'] == 'signup'){
            $scope.email_login_flag = false
        }else{
            $scope.email_login_flag = true
        }
        $scope.check_login = function(noredirect){
            $http.get('/user/mydetails/').
                success(function(data, status, headers, config) {
                if (data.status == "success"){
                    $('#login').removeClass('open')
                    $('#login').addClass('done')
                    $('#address').addClass('open')
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
                    $rootScope.$broadcast('parent', 'pop')
                    ga('set', 'dimension3', $localStorage.zap_username );
                    console.log($localStorage.stage)
                    if(!noredirect){
                        if ($localStorage.stage < 5) {
                            $location.url('/onboarding')
                            return false
                        }
                        else if(location.hash.substr(0,7)=="#/login"){
                            $location.url('/feeds')
                            return false
                        }
                    }
                }else{
                    $scope.loggedIn = false
                    $localStorage.$reset();

                    // $localStorage.loggedIn = false
                }
                

              }).
              error(function(data, status, headers, config) {

                // called asynchronously if an error occurs
                // or server returns response with an error status.
              });
        }
        // if(!$localStorage.loggedIn){
        $scope.check_login()
        // }

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
        //     }, function errorCallback(response) {

        //     });

        // }

        $scope.insta_please_wait = function(){
            $('#signup-login').removeClass('is_visible')
            window.location.href = "/account/instagram/" 
            //$('#please-wait-header').addClass('is_visible')
        }        

        $scope.FBLogin = function() {

            $localStorage.$reset()
            FB.login(function(response) {
                if(response.status == 'connected'){
                    $('#signup-login').removeClass('is_visible')
                    //$('#please-wait-header').addClass('is_visible')
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
                        //alert(JSON.stringify(response))

                        //$('#please-wait-header').removeClass('is_visible')
                        $scope.check_login()
                        console.log(response.data.data.profile_completed, "ooo")
                        if(response.data.data.profile_completed == 5){

                            // $location.url('/feeds')
                        }
                        //window.location = '#/onboarding'
                        // $location.url('/onboarding')
                    }, function errorCallback(response){

                    })
                }else{
                    //$('#please-wait-header').removeClass('is_visible')
                }
            }, {scope: 'public_profile,email'});
        };
        $scope.checkout_signin = function(){
            $(".checkout_signin").text('PLEASE WAIT')
            $(".checkout_signin").prop('disabled', true)
            $scope.errors = {}
            $http({
                method: 'POST',
                url: "/account/login/",
                data: {
                    email: $scope.l.email_login,
                    password: $scope.l.password_login,
                    logged_device: "website",
                    logged_from: "zapyle"
                }
            }).then(function successCallback(response) {
                console.log(response.data)
                if(response.data.status=="success"){
                    mixpanel.track("User Event", {'Event Name': 'Logged In', 'Channel':'Email'});
                    if(location.hash.substr(0,7)=="#/login"){
                        $scope.check_login()
                        //$location.url('/feeds')
                        return false
                    }
                    $('#signup-login').removeClass('is_visible')
                    $scope.l=''
                    $scope.check_login("noredirect")
                    //$scope.get_datas()
                }else{
                    var error_msg = response.data.detail
                    if (typeof error_msg == 'string'){
                        $scope.errors.password = error_msg
                    }else{
                        if ('email' in error_msg){
                            $scope.errors.email = error_msg['email'][0]
                        }
                        if ('password' in error_msg){
                            $scope.errors.password = error_msg['password'][0]               
                        }
                    }
                    console.log(JSON.stringify(response.data.detail))
                }
                $(".checkout_signin").text('Login with Email')
                $(".checkout_signin").prop('disabled', false)
            }, function errorCallback(response) {

            });   
        }
        $scope.checkout_signup = function(){
            $(".btn_signup").text('PLEASE WAIT')
            $(".btn_signup").prop('disabled', true)
            $scope.errors = {}
            $http({
                method: 'POST',
                url: "/account/signup/",
                data: {
                    zap_username: $scope.s.signup_zap_username,
                    email: $scope.s.signup_email,
                    password: $scope.s.signup_password,
                    confirm_password: $scope.s.signup_confirm_password,
                    phone_number: $scope.s.signup_phone_number,
                    first_name: $scope.s.signup_first_name,
                    logged_device: "website",
                }
            }).then(function successCallback(response) {
                if(response.data.status=="success"){
                    mixpanel.track("User Event", {'Event Name': 'Signed up', 'Channel':'Email'});
                    if(location.hash.substr(0,10)=="#/checkout"){
                    $('#signup-login').removeClass('is_visible')

                        $scope.check_login("noredirect")
                        //$location.url('/feeds')
                        return false
                    }else{
                    $('#signup-login').removeClass('is_visible')
                        $scope.check_login()
                    }
                    // $scope.check_login("noredirect")
                    $scope.s=''
                }else{
                    var error_msg = response.data.detail
                    if ('zap_username' in error_msg){
                        $scope.errors.username = error_msg['zap_username'][0]
                    }
                    if ('email' in error_msg){
                        $scope.errors.Email = error_msg['email'][0]
                    }
                    if ('password' in error_msg){
                        $scope.errors.pwd = error_msg['password'][0]               
                    }
                    if ('confirm_password' in error_msg){
                        $scope.errors.cpwd = error_msg['confirm_password'][0]               
                    }
                    if ('first_name' in error_msg){
                        $scope.errors.fname = error_msg['first_name'][0]
                    }
                    if ('phone_number' in error_msg){
                        if(error_msg['phone_number']['phone_number']){
                            $scope.errors.phone = error_msg['phone_number']['phone_number']
                        }else{
                            $scope.errors.phone = error_msg['phone_number'][0]           
                        }
                    }
                    //console.log(JSON.stringify(response.data.detail))
                }
                $(".btn_signup").text('Signup with Email')
                $(".btn_signup").prop('disabled', false)
            }, function errorCallback(response) {

            });   
        }
        $scope.close_login_popup = function(){
            $('.signup-login').removeClass('is_visible')
        }
        $scope.send_verification_email = function(email){
            if(!email){
                return false
            }
            $(".email_verify_button").html('Please Wait...').prop('disabled', true);;
            $http({
                method: 'POST',
                url: "/account/password/reset/",
                data: {
                    email: email,
                }
            }).then(function successCallback(response) {
                $(".email_verify_button").html("Send Verification Email").prop('disabled', false);
                $scope.frgt_email=''
                if(response.data.status=="success"){
                    $scope.success_msg = response.data.data
                    //setTimeout(function(){alert(frgt_pwd_flag)}, 300);
                    
                }else{
                    if (typeof(response.data.detail)=='object'){
                        $scope.success_msg = response.data.detail['email'][0]
                        //alert(JSON.stringify(response.data.detail['email'][0]))
                    }else{
                        $scope.success_msg = response.data.detail
                        //alert(JSON.stringify(response.data.detail))
                    }
                }
            })
        }
        $scope.reset_password = function(new_pwd,confirm_pwd){
            $scope.success_msg = ''
            if(!new_pwd){
                $scope.success_msg = "Enter new Password"
                return false
            }
            if(new_pwd == confirm_pwd){
                $(".reset_btn").text('PLEASE WAIT')
                $(".reset_btn").prop('disabled', true)
                $http({
                    method: 'POST',
                    url: "/account/password/reset/"+$scope.reset_token+"/",
                    data: {
                        password: new_pwd,
                    }
                }).then(function successCallback(response) {
                        //alert(JSON.stringify(response))
                        if(response.data.status=='success'){
                            $scope.check_login('noredirect')
                            $location.url('/feeds')
                        }else{
                            if ('password' in response.data.detail){
                                $scope.success_msg = response.data.detail['password'][0]
                            }else{
                                alert(JSON.stringify(response.data.detail))
                            }
                            $(".reset_btn").text('Change Password')
                            $(".reset_btn").prop('disabled', false)
                        }
                }, function errorCallback(response) {
                    if (response.status == '404'){
                        $scope.success_msg = 'Password reset link is expired.'
                    }
                    $(".reset_btn").text('Change Password')
                    $(".reset_btn").prop('disabled', false)
                })
            }else{
                $scope.success_msg = "password didn't match"
            }
        }
    });

// else if (response.data.new_user == false) {
//     a = function(data) {
//             $localStorage.zap_username = response.data.zap_username
//             $localStorage.email = response.data.email
//             $localStorage.user = response.data.new_user
//             $localStorage.id = response.data.id
//             return true

//         }
//         // location.reload(true);
//         
//     if (a) {
//         location.reload(true);
//     }



// }
