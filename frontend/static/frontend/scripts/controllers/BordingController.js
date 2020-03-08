'use strict';

/**
 * @ngdoc function
 * @name appApp.controller:AboutCtrl
 * @description
 * # AboutCtrl
 * Controller of the appApp
 */
angular.module('zapyle')
    .controller('BordingController', function($scope, $auth, $http, $route, $routeParams, $localStorage, $sessionStorage, $rootScope,$location) {
        $scope.email = $localStorage.email
        $scope.zap_username = $localStorage.zap_username
        $scope.stage = $localStorage.stage
        $scope.full_name = $localStorage.full_name
        $scope.username = $localStorage.username
        $scope.mob_no = $localStorage.phone_number
        console.log($scope.email, $scope.zap_username, $scope.stage, $scope.full_name)
        // $http({
        //         method: 'GET',
        //         url: '/onboarding/',
        //     }).then(function successCallback(response) {
        //alert(response.data.current_step)
        $scope.get_sizes = function(){
            $http({
              method: 'GET',
              url: '/onboarding/4/'
            }).then(function successCallback(response) {
                $scope.waist_sizes = response.data.data.waist_sizes
                $scope.cloth_sizes = response.data.data.cloth_sizes
                $scope.foot_sizes = response.data.data.foot_sizes
                // this callback will be called asynchronously
                // when the response is available
              }, function errorCallback(response) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
              });
        }
        $scope.get_brand_tags = function(){
            $http({
              method: 'GET',
              url: '/onboarding/2/'
            }).then(function successCallback(response) {
                $scope.brandtags = response.data.data;
                // this callback will be called asynchronously
                // when the response is available
              }, function errorCallback(response) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
              });
        }
        $scope.get_brands = function(){
            $http({
              method: 'GET',
              url: '/onboarding/3/'
            }).then(function successCallback(response) {
                $scope.allbrands = response.data.data.selected_brands
                Array.prototype.push.apply($scope.allbrands,response.data.data.unselected_brands)
              }, function errorCallback(response) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
              });
        }
        switch($scope.stage){
            case 5:
                window.location = '#/feeds'
                break;
            case 4:
                $scope.get_sizes()
                $('#onboarding-size').addClass('is_visible');
                $('#onboarding-brands').removeClass('is_visible');
                break;
            case 3:
                $scope.get_sizes()
                $('#onboarding-size').addClass('is_visible');
                // $scope.get_brands()
                // $('#onboarding-brands').addClass('is_visible');
                // $('#onboarding-style').removeClass('is_visible');
                $localStorage.stage = 4
                break;
            case 2:
                $scope.get_sizes()
                $('#onboarding-size').addClass('is_visible');
                // $scope.get_brand_tags()
                // $('#onboarding-style').addClass('is_visible');
                // $('#onboarding-name').removeClass('is_visible');
                $localStorage.stage = 4
                break;
            case 1:
                $('#onboarding-name').addClass('is_visible');
                break;
                }
            // });
        $scope.available = 1
        $scope.check_username = function(){
            if(!$scope.zap_username || $scope.zap_username.length<4){
                $scope.available=0
                return false
            }
            $http({
                method: 'POST',
                url: '/user/check_username/',
                data: {
                'zap_username': $scope.zap_username,
                'email': $scope.email,
                },
            }).then(function successCallback(response) {
                console.log(response)
                $scope.available=response.data.status == "success"
            });
        }
        $scope.errors ={}

        $scope.logout = function() {
            $localStorage.$reset();
            $http({
              method: 'GET',
              url: '/account/logout/'
            }).then(function successCallback(response) {
                $('.pri-overlay').removeClass('is_visible')
                $rootScope.loggedIn = false
                $location.url("/feeds")
              }, function errorCallback(response) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
              });
        }
        $scope.submit_otp = function(){
            $http({
                method: 'POST',
                url: '/onboarding/1/?action=otp',
                data: {
                    "otp": $scope.otp,
                },
            }).then(function successCallback(response) {
                if (response.data.status == "success"){
                        $scope.get_brand_tags()
                        $localStorage.stage = 4
                        $localStorage.zap_username = $scope.zap_username
                        $rootScope.$broadcast('parent', 'Sathyalog')
                        // $('#onboarding-style').addClass('is_visible');
                        // $('#onboarding-name').removeClass('is_visible');
                        $scope.get_sizes()
                        $localStorage.stage = 4
                        $('#onboarding-size').addClass('is_visible');
                        $('#onboarding-name').removeClass('is_visible');
                }
                else {
                    $('#error-otp').removeClass('is_hidden')
                }
                },
                function errorCallback(response) {
 
                });            
        }
        $scope.submit_username = function() {
            $('#onboarding_1_button').html('Please wait')
            $("#onboarding_1_button").prop('disabled', true) 
            $scope.errors = {}
            $http({
                method: 'POST',
                url: '/onboarding/1/',
                data: {
                    "zap_username": $scope.zap_username,
                    "email": $scope.email,
                    "phone_number": $scope.mob_no
                },
            }).then(function successCallback(response) {
                if (response.data.status == "success"){
                    // $scope.otp_page = true
                        $scope.get_brand_tags()
                        $localStorage.stage = 4
                        $localStorage.zap_username = $scope.zap_username
                        $rootScope.$broadcast('parent', 'Sathyalog')
                        // $('#onboarding-style').addClass('is_visible');
                        // $('#onboarding-name').removeClass('is_visible');
                        $scope.get_sizes()
                        $localStorage.stage = 4
                        $('#onboarding-size').addClass('is_visible');
                        $('#onboarding-name').removeClass('is_visible');
                        $('#onboarding_1_button').html('Next')
                        $("#onboarding_1_button").prop('disabled', false) 
                }
                else {
                    var error_msg = response.data.detail
                    if ('phone_number' in error_msg){
                        $scope.errors.mob_number = error_msg['phone_number'][0]
                    }
                    if ('zap_username' in error_msg){
                        $scope.errors.zap_username = error_msg['zap_username'][0]               
                    }if('email' in error_msg){
                        $scope.errors.email = error_msg['email'][0]
                    }
                    $('#onboarding_1_button').html('Next')
                    $("#onboarding_1_button").prop('disabled', false) 
                }
                },
                function errorCallback(response) {
                    $('#onboarding_1_button').html('Next')
                    $("#onboarding_1_button").prop('disabled', false) 
                });

        }

        $scope.submit_btags = function() {
            var btags=[]
            $('#onboarding-style').find('.is_selected').each(function() {
                btags.push($(this).data('id'));
            });
            $http({
                method: 'POST',
                url: '/onboarding/2/',
                data: {
                    "btags_selected": btags,
                },
            }).then(function successCallback(response) {
                console.log(JSON.stringify(response)+'---------')
                if (response.data.status == "success"){
                    $scope.get_brands()
                    $localStorage.stage = 3
                    $('#onboarding-brands').addClass('is_visible');
                    $('#onboarding-style').removeClass('is_visible');
                }});
        }

        $scope.submit_brands = function() {
            var brands=[]
            $('#onboarding-brands').find('.is_selected').each(function() {
                brands.push($(this).data('id'));
            });
            $http({
                method: 'POST',
                url: '/onboarding/3/',
                data: {
                    "brands_selected": brands,
                },
            }).then(function successCallback(response) {
                if (response.data.status == "success"){
                    $scope.get_sizes()
                    $localStorage.stage = 4
                    $('#onboarding-size').addClass('is_visible');
                    $('#onboarding-brands').removeClass('is_visible');
                }
            },
            function errorCallback(response) {
            });
        }
        
        $scope.start_shopping = function() {
            $('#onboarding_2_button').html('Please wait..')
            $("#onboarding_2_button").prop('disabled', true) 
            $scope.cloth_sizes_to_send = []
            $scope.foot_sizes_to_send = []
            $scope.waist_sizes_to_send = []
            $('#onboarding-size .generic').find('.is_selected').each(function() {
                $scope.cloth_sizes_to_send.push($(this).data('id'));
            });
            $('#onboarding-size .footwear').find('.is_selected').each(function() {
                $scope.foot_sizes_to_send.push($(this).data('id'));
            });
            $('#onboarding-size .waist').find('.is_selected').each(function() {
                $scope.waist_sizes_to_send.push($(this).data('id'));
            });
            $http({
                method: 'POST',
                url: '/onboarding/4/',
                data: {
                    'foot_sizes': $scope.foot_sizes_to_send,
                    'cloth_sizes': $scope.cloth_sizes_to_send,
                    'waist_sizes': $scope.waist_sizes_to_send},
            }).then(function successCallback(response) { 
                    if (response.data.status == "success") {
                         $localStorage.stage = 5
                         $rootScope.$broadcast('parent', 'Sathyalog')
                        window.location = '#/feeds'
                    }else{
                        $('#onboarding_2_button').html('Start Shopping')
                        $("#onboarding_2_button").prop('disabled', false) 
                    }
                },
                function errorCallback(response) {
                    $('#onboarding_2_button').html('Start Shopping')
                    $("#onboarding_2_button").prop('disabled', false) 
                 });
        }









        // if(!$localStorage.loggedIn){
        //     $location.url('/')
        //   }        
        // $scope.loggedIn = $localStorage.loggedIn
        // $scope.email = $localStorage.email
        // $scope.username = $localStorage.username
        // $scope.zap_username = $scope.username
        // $localStorage.zap_username = $scope.zap_username
        // $scope.stage = $localStorage.stage
        // var array = new Array();
        // var array2 = new Array();
        // // var array3 = new Array();
        // var array4 = new Array();
        // var array5 = new Array();  



        // if ($scope.stage==2){
        //     $http({
        //     method: 'GET',
        //     url: '/onboarding/getbrandtags/',
        // }).then(function successCallback(response) {
        //     $scope.brandtags = response.data.data;
        // }, function errorCallback(response) {

        // });
        //     $('#onboarding-style').addClass('is_visible');
        //     $('#onboarding-name').removeClass('is_visible')
        //     $('#onboarding-brands').removeClass('is_visible')
        //     $('#onboarding-size').removeClass('is_visible')
        // }
        // if ($scope.stage == 3){
        //     $http({
        //     method: 'GET',
        //     url: '/onboarding/getbrands/',
        // }).then(function successCallback(response) {
        //     $scope.allbrands = response.data.data;
        // }, function errorCallback(response) {

        // });
        //     $('#onboarding-brands').addClass('is_visible');
        //     $('#onboarding-style').removeClass('is_visible');
        //     $('#onboarding-size').removeClass('is_visible');
        //     $('#onboarding-name').removeClass('is_visible');
        // }

        // if ($scope.stage == 4){
        //     $('#onboarding-brands').removeClass('is_visible')
        //     $('#onboarding-size').addClass('is_visible');       
        //     $('#onboarding-style').removeClass('is_visible');
        //     $('#onboarding-name').removeClass('is_visible');     
        // }
        // if ($scope.stage == 5){
        //     window.location = '/#/feeds'
        // }  
        // $scope.start_shopping = function() {
        //     $http({
        //         method: 'POST',
        //         url: '/onboarding/4/',
        //         data: {},
        //     }).then(function successCallback(response) {
        //              if (response.data.status == "success") {
        //                 $localStorage.stage = 5
        //                  $rootScope.$broadcast('parent', 'Sathyalog')
        //                 window.location = '#/feeds'
        //             }
        //         },
        //         function errorCallback(response) {
        //          });
        // }

        

        
        

        ////////////////////////////end of steps //////////////////////////
        // $http({
        //     method: 'GET',
        //     url: '/getfashionimages/',
        // }).then(function successCallback(response) {
        //     $scope.boho = response.data.boho;
        //     $scope.chic = response.data.chic;
        //     $scope.classic = response.data.classic;
        //     $scope.trendy = response.data.trendy;
        // }, function errorCallback(response) {

        // });


        // $http({
        //     method: 'GET',
        //     url: '/getbrand/',
        // }).then(function successCallback(response) {
        //     $scope.allbrands = response.data;
        // }, function errorCallback(response) {

        // });


        // $http({
        //     method: 'GET',
        //     url: '/getsize/',
        // }).then(function successCallback(response) {
        //      $scope.wast = response.data.waist_size_list
        //     $scope.size = response.data.size_list
        //     $scope.footSize = response.data.foot_size_list
 

        // }, function errorCallback(response) {

        // });
    });
        // $scope.check_login = function(){
        //     $http.get('/user/').
        //         success(function(data, status, headers, config) {
        //         if(data.data.status == true){
        //             $scope.email = data.data.email
        //             $scope.user = data.data.username
        //             $scope.name = data.data.username
        //             $localStorage.zap_username = data.data.username
        //             $localStorage.stage = data.data.stage
                    
        //             }
        //       }).
        //       error(function(data, status, headers, config) {

        //         // called asynchronously if an error occurs
        //         // or server returns response with an error status.
        //       });
        // }
        // $scope.check_login()    
        // $scope.send = function() {
        //     $('.brands-list').find('.is_selected').each(function() {
        //         array2.push($(this).data('id'))
        //     });

        //     $localStorage.fashionBrand = array2
        //     $http({
        //         method: 'POST',
        //         url: '/updatefashionbrands/',
        //         data: {
        //             "brand": $localStorage.fashionBrand
        //         }
        //     }).then(function successCallback(response) {
        //              if (response.data == "Updated") {
        //                  $rootScope.$broadcast('parent', 'Sathyalog')
        //                 window.location = '#/feeds'
        //             }
        //         },
        //         function errorCallback(response) {
        //          });
        // }



        // $scope.step3 = function() {

        //     var generic = $('.generic').find('.is_selected').text();

        //     $localStorage.generic = generic;


        //     $('.waist').find('.is_selected').each(function() {
        //         array4.push($(this).data('id'));
        //     });
        //     $localStorage.waist = array4;

        //     $('.footwear').find('.is_selected').each(function() {
        //         array5.push($(this).data('id'));
        //     });
        //     $localStorage.footware = array5;

        //     $http({
        //         method: 'POST',
        //         url: '/onboardingsize/',
        //         data: {
        //             "generic_size": $localStorage.generic,
        //             "waist_size": $localStorage.waist,
        //             "footware_size": $localStorage.footware

        //         },
        //     }).then(function successCallback(response) {
        //              if (response.data == "Updated") {
        //              }
        //         },
        //         function errorCallback(response) {
        //          });

        // }

        // $scope.step2 = function() {
        //     $('#onboarding-style').find('.is_selected').each(function() {
        //         array.push($(this).data('id'));
        //     });

        //     $localStorage.fashionStyle = array


        //     $http({
        //         method: 'POST',
        //         url: '/updatefashionbrands/',
        //         data: {
        //             "fashion_type": $localStorage.fashionStyle
        //         },
        //     }).then(function successCallback(response) {
        //              if (response.data == "Updated") {
        //              }
        //         },
        //         function errorCallback(response) {
        //          });
        // }
