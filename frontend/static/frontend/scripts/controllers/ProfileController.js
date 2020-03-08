'use strict';

/**
 * @ngdoc function
 * @name zapyle.controller:MainCtrl
 * @description
 * # HomeController Created by Albin CR
 * Controller of the zapyle
 */
angular.module('zapyle')
    .controller('ProfileController', function($scope, $http, $routeParams, $localStorage, likeService, UnlikeService, admireService, UnadmireService) {
        var delta = Math.abs(Date.now() - PageStartTime) / 1000;
        var minutes = Math.floor(delta / 60) % 60;
        delta -= minutes * 60;
        var seconds = delta % 60;
        mixpanel.track("User Event", {'Event Name': 'Changed page','to':window.location.href, 'from':CurrentPage,  'time spent on page':minutes+' minutes '+seconds+' seconds'});
        CurrentPage = window.location.href
        PageStartTime = Date.now()
        $scope.limit = 2;
        $scope.begin = 0;
        var status = $localStorage.loggedIn;
        $scope.user_id = $localStorage.user_id;
        var descrip;
        $scope.edit_desc = false


        // Get server data function
        // ----------------------------------------
        $scope.$on("$destroy", function() {
            $("meta[data-zap='prpage']").remove()
            $('html').append(index_meta)
            document.title = "Zapyle | Discover, Sell and Buy Fashion"
        });

        $scope.metaTagChange = function(){
            $("html").attr("itemtype", "http://schema.org/Person");
            document.title = $scope.profiledata.zap_username
            $("meta[data-zap='index']").remove()
            $('head').append(
                    '<meta data-zap="prpage" name="description" content="'+$scope.profiledata.description+'" />'+
                    '<meta data-zap="prpage" itemprop="name" content="'+$scope.profiledata.zap_username+'">'+
                    '<meta data-zap="prpage" itemprop="description" content="'+$scope.profiledata.description+'">'+
                    '<meta data-zap="prpage" itemprop="image" content="'+base_url+'/#/profile/' + $routeParams.profileId + '/'+'">'+
                    '<meta data-zap="prpage" name="twitter:card" content="summary">'+
                    '<meta data-zap="prpage" name="twitter:site" content="@ZapyleSocial">'+
                    '<meta data-zap="prpage" name="twitter:title" content="'+$scope.profiledata.zap_username+'">'+
                    '<meta data-zap="prpage" name="twitter:description" content="'+$scope.profiledata.description+'">'+
                    '<meta data-zap="prpage" name="twitter:image" content="'+$scope.profiledata.profile_pic+'">'+
                    '<meta data-zap="prpage" property="og:title" content="'+$scope.profiledata.zap_username+'" />'+
                    '<meta data-zap="prpage" property="og:type" content="person" />'+
                    '<meta data-zap="prpage" property="og:url" content="'+base_url+'/#/profile/' + $routeParams.profileId + '/'+'" />'+
                    '<meta data-zap="prpage" property="og:image" content="'+$scope.profiledata.profile_pic+'" />'+
                    '<meta data-zap="prpage" property="og:description" content="'+$scope.profiledata.description+'" />'+
                    '<meta data-zap="prpage" property="og:site_name" content="Zapyle" />')
        }

        $scope.getDataforGuest = function() {
            $http({
                method: 'GET',
                url: '/user/profile/' + $routeParams.profileId + '/'
            }).then(function successCallback(response) {
                show_loader('page', true);
                show_loader('loading', false);
                $scope.profiledata = response.data.data;
                $scope.admired = response.data.data.admired_by_user;
                $scope.profile_description = response.data.data.description;

                $scope.editDesc = response.data.description;
                descrip = response.data.description;
                $scope.metaTagChange()
                mixpanel.track("User Event", {'Event Name': 'Visit user profile', 'username':$scope.profiledata.zap_username, 'from page': 'profile'});
            }, function errorCallback(response) {
             });
        }


        $scope.getDataforUser = function() {
            $http({
                method: 'GET',
                url: '/edit_user/',
                headers: {
                    'X-UuidKey': $localStorage.uuid_keyx,
                    'X-DeviceID': $localStorage.device_idx
                }
            }).then(function successCallback(response) {
                 $scope.profiledata = response.data;
                $scope.admired = response.data.admired_by_user;
                $scope.profile_description = response.data.description;

            }, function errorCallback(response) {
             });
        }





        //  Proceed With Checking
        // ------------------------------------------

        // if ($localStorage.loggedIn) {
        // $scope.getDataforUser();
        // } else {
        $scope.getDataforGuest();
        // }


        //  Like onclick function
        // ----------------------------------------
        $scope.plike = function(card,status) {

            if ($localStorage.loggedIn) {
                if (status == 'like'){
                    card['liked_by_user'] = true
                    card['likesCount']++
                }else{
                    card['liked_by_user'] = false
                    card['likesCount']--
                }
                var request = $http({
                    method: "POST",
                    url: '/user/like_product/',
                    data: {
                        'product_id': card.id,
                        'action': status,
                    },
                });
                request.success(function(rs) {
                    console.log(JSON.stringify(rs))
                    if(rs.status == "error"){
                        if (status == 'like'){
                            card['liked_by_user'] = false
                            card['likesCount']--
                        }else{
                            card['liked_by_user'] = true
                            card['likesCount']++
                        }
                    }
                })
                request.error(function() {})
            }else {
                $('#signup-login').addClass('is_visible');
            }
            
        }


        // Like function to async
        // -------------------------------------

        $scope.startlike = function(album_id) {
             var promise =
                likeService.postLikes(album_id);
            promise.then(
                function(payload) {
                 },
                function(errorPayload) {
                 });
        };


        // Un like fnuction  to async
        // -------------------------------------------------

        $scope.unlike = function(album_id) {
            var promise =
                UnlikeService.postunLikes(album_id);
            promise.then(
                function(payload) {
 
                },
                function(errorPayload) {

                 });
        };



        //  Admire function
        // ----------------------------------------------------

        $scope.admire = function(u) {
            if ($localStorage.loggedIn) {
                var u_copy = u
                u.admire_or_not = !u.admire_or_not
                if (u.admire_or_not==true){
                    var status = 'admire'
                    if($scope.user_id == $scope.profiledata.id){
                        $scope.profiledata.admiring++
                    }
                }else{
                    var status = 'unadmire'
                    if($scope.user_id == $scope.profiledata.id){
                        $scope.profiledata.admiring--
                        $scope.admiring.shift(u)
                    }
                }
                $http.post('/user/admire/', {
                    'user': u.id,
                    'action' : status
                }).success(function(response) {
                    if(response.status=="error"){
                        u.admire_or_not = !u.admire_or_not
                        $scope.admiring.unshift(u_copy)
                    }else{
                        if(status== 'admire'){
                            mixpanel.track("User Event", {'Event Name': 'Admire user', 'username':u.zap_username, 'from page': 'profile'});
                        }
                    }
                }).error(function(response) {
                    //code here
                });
            }else {
                $('#signup-login').addClass('is_visible');
            }
        }
        $scope.admire2 = function(status) {
            if ($localStorage.loggedIn) {
                if (status == 'admire'){
                    $scope.profiledata.admired_by_user = true
                    $scope.profiledata.admirers++
                }else{
                    $scope.profiledata.admired_by_user = false
                    $scope.profiledata.admirers--
                }
                $http.post('/user/admire/', {
                    'user': $scope.profiledata.id,
                    'action' : status
                }).success(function(response) {
                    console.log(response)
                    if(response.status == 'success'){
                        if($scope.current_tab == 'admires'){
                            $scope.get_admires('admires')
                        }
                    }else
                    if(response.status=="error"){
                       // u.admire_or_not = !u.admire_or_not
                    }
                }).error(function(response) {
                    //code here
                });
            }else {
                $('#signup-login').addClass('is_visible');
            }
        }
        $scope.like_unlike = function(grid,status){
            if($localStorage.loggedIn){
                if (status == 'like'){
                    grid['liked_by_user'] = true
                    grid['likes_count']++
                }else{
                    grid['liked_by_user'] = false
                    grid['likes_count']--
                }
                var request = $http({
                    method: "POST",
                    url: '/user/like_product/',
                    data: {
                        'product_id': grid.id,
                        'action': status,
                    },
                });
                request.success(function(rs) {
                    console.log(JSON.stringify(rs))
                    if(rs.status == "error"){
                        if (status == 'like'){
                            grid['liked_by_user'] = false
                            grid['likes_count']--
                        }else{
                            grid['liked_by_user'] = true
                            grid['likes_count']++
                        }
                    }
                })
                request.error(function() {})
            }else{
                $('#signup-login').addClass('is_visible');
            }
        }

        //  EditProfile function
        // ----------------------------------------------------

        $scope.editProfile = function() {

            // var id = $('._editcheck').attr('id');
             if ($localStorage.loggedIn) {
                if(!$scope.profiledata.description){
                    $('#inputbox_fordesc').attr("placeholder", "Type your description here");
                    return false
                }
                $http({
                        method: 'PUT',
                        url: '/user/mydetails/',
                        data: {
                            description: $scope.profiledata.description
                        },
                    }).then(function successCallback(response) {
                         $scope.edit_desc = false
                    }, function errorCallback(response) {
                     });

                // if (id === 'edit-profile') {
                //     $('#description').removeClass('is_visible');
                //     $('#inputbox_fordesc').removeClass('is_hidden');
                //     $('#description').addClass('is_hidden');
                //     $('#inputbox_fordesc').addClass('is_visible');
                //     $('#inputbox_fordesc').text($('#description').text());
                //     // $scope.profile_description = $("#description").text();

                //     document.getElementById("edit-profile").setAttribute("id", "save-profile");
                // } else {

                //     $('#description').removeClass('is_hidden');
                //     $('#inputbox_fordesc').removeClass('is_visible');

                //     $('#description').addClass('is_visible');
                //     $('#inputbox_fordesc').addClass('is_hidden');

                //     document.getElementById("save-profile").setAttribute("id", "edit-profile");
                //     if ($scope.editDesc == "" || $scope.editDesc == undefined) {
                //          $scope.profile_description = $('#description').text();
                //         $('#inputbox_fordesc').text($('#description').text());

                //     } else {
 
                //         $scope.profile_description = $scope.editDesc;
                //         $('#inputbox_fordesc').text($scope.editDesc);

                //     }

                //     $http({
                //         method: 'PUT',
                //         url: '/user/mydetails/',
                //         data: {
                //             description: $scope.profile_description
                //         },
                //     }).then(function successCallback(response) {
                //          // $scope.profile_description = $scope.editDesc;



                //     }, function errorCallback(response) {
                //      });

                // }

            } else {
                $('#signup-login').addClass('is_visible');
            }


        }

        $scope.get_admires = function(admire_type){
            $http({
                    method: 'PUT',
                    url: "/user/admire/",
                    data:{
                        'user_id':$scope.profiledata.id,
                        'admire_type':admire_type
                    }
                }).then(function successCallback(response) {
                    if(response.data.status == 'success'){
                        if(admire_type == 'admires'){
                            $scope.admires = response.data.data
                            mixpanel.track("User Event", {'Event Name': 'Looking at admirers', 'from page': 'profile'});
                        }else{
                            $scope.admiring = response.data.data
                            mixpanel.track("User Event", {'Event Name': 'Looking at admiring', 'from page': 'profile'});
                        }
                    }else{
                        alert(response.data.detail)
                    }
                     $scope.Comments = response.data.data;
                 }, function errorCallback(response) {
                 });
        }



    });
