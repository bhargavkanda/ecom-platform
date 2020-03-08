'use strict';

angular.module('zapyle')
    // .filter("reverse", function(){
    //     return function(items){
    //         return items.slice().reverse(); // Create a copy of the array and reverse the order of the items
    //     };
    // });
    .directive("responsiveMenu", function() {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                $('#show-menu').click(function() {
                    $('.side-menu').toggleClass('is_visible');
                    $('.signup-login-links').toggleClass('is_hidden');
                });
            }
        }
    })
    .directive("hideMenu", function() {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                $('.side-menu .nav-bar').on('click', 'li', function(){
                // $('#show-menu').click(function() {
                    //alert()
                    $('.side-menu').toggleClass('is_visible');
                    $('.signup-login-links').toggleClass('is_hidden');
                });
            }
        }
    })
    .directive("selectCard", function(addressService) {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                $('.address-card').click(function() {
                    $('.address-card').removeClass('is_selected');
                    $(this).addClass('is_selected');
                    addressService.selectAddress($(this).attr('id'));
                });
            }
        }
    })
    .directive("selectMenu", function() {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                $('header .nav-bar li').click(function() {
                    $('header .nav-bar li').removeClass('selected');
                    $(this).addClass('selected');
                });
            }
        }
    })
    .directive("countinueShopping", function($localStorage) {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                $('.zap-msg a').click(function() {
                     $localStorage.buy_status = false;
                    window.location.href = "#/feeds";
                });
            }
        }
    }).directive("dynamicHeigh", function() {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                $('.discover .fold-wrapper').css({
                    'height': $(window).height()
                });
                $('.sell .fold-wrapper').css({
                    'height': $(window).height()
                });
            }
        }
    })
    .directive("discoverVideo", function() {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                $('.video').click(function() {
                    $('#zap-video').addClass('is_visible');
                    $('#zap-video .video-frame').html('<iframe width="100%" height="100%" src="https://www.youtube.com/embed/Bbd3Zi-6V-o?autoplay=1" frameborder="0" allowfullscreen></iframe>');
                });
                $('#zap-video .close, #zap-video .glass').click(function() {
                    $('#zap-video').removeClass('is_visible');
                    $('#zap-video .video-frame').html('');
                });
            }
        }
    })
    .directive("closePop", function() {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
               $("#signup-login").click(function(){
                    $("#signup-login").removeClass('is_visible');
               })
            }
        }
    })
    .directive("loginChange", function() {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                $('.show-login').click(function() {
                     $('.signup-module').hide(500);
                    $('.signin-module').show(500);
                });
                $('.show-signup').click(function() {
 
                    $('.signup-module').show(500);
                    $('.signin-module').hide(500);
                });
            }
        }
    })
.directive("savedRadio", function() {
    return {
        link: function(scope, elem, attrs) {
            elem.on("click", function() {
                $('.mysavedcards').removeClass('selected')
                elem.addClass("selected");
            });
        }
    };
})
.directive("sizeSelect", function() {
    return {
        restrict: 'A',
        link: function(scope, elem, atts) {

            $('.generic .size').click(function() {

                $('.generic .size').removeClass('is_selected');
                $(this).addClass('is_selected');
            });
            $('.waist .size').click(function() {

                $('.waist .size').removeClass('is_selected');
                $(this).addClass('is_selected');
            });
            $('.footwear .size').click(function() {

                $('.footwear .size').removeClass('is_selected');
                $(this).addClass('is_selected');
            });
            // $('.brand').click(function() {
            //     $(this).toggleClass('is_selected');
            //     if ($('.brand.is_selected').length) {
            //         $('#onboarding-brands .footer .button').removeClass('is_disabled');
            //     } else {
            //         $('#onboarding-brands .footer .button').addClass('is_disabled');
            //     }
            // });

        }
    }

})

.directive('toggleClass', function() {
        return {
            restrict: 'A',
            link: function(scope, element, attrs) {
                element.bind('click', function() {
                    element.toggleClass('is_selected');
                });
            }
        };
    })
    .directive("newAddress", function() {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                $('.new-address-card').click(function() {
                    $('#add-address').fadeIn(500);
                });
                $('#add-address .cancel').click(function() {
                    $('#add-address').fadeOut(500);
                })
                $('#add-address .submit').click(function() {
                    $('#add-address').fadeOut(500);
                    $('.address-card').removeClass('is_selected');
                })
            }
        }
    })
    .directive("showNotifications", function() {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                $('#show-coupon').click(function() {
                    $('.apply-coupon').addClass('show');
                });
            }
        }
    })
    .directive("logStatus", function() {
        return {
            restrict: 'A',
            link: function(scope, elem, attrs) {
                $('.logged-in').click(function() {
                    $('.user-options').toggleClass('is_visible');
                });
            }
        }
    })

.directive("popUp", function() {
    return {
        restrict: 'A',
        link: function(scope, elem, attrs) {
            $('.signup-login-links a').click(function() {
                
                $('#signup-login').addClass('is_visible');
            });
            $('#signup-login .close').click(function() {
                $('#signup-login').removeClass('is_visible');
            });

        }
    }
})




.directive("switchViews", function($http, $localStorage, SellerData, ProductData) {

        return {
            restrict: "A",
            link: function(scope, elem, attrs) {

                $('.view-switch > span > span').click(function(event) {
                    $('#loadmore_error').removeClass('is_visible');
                    SellerData.emptyData();
                    ProductData.emptyData();
                    scope.seller_pagination = 1;
                    scope.product_pagination = 1;
                    $('.view-switch .is_selected').removeClass('is_selected');
                    $(this).addClass('is_selected');
                    $('[class*="-view"].content').addClass('is_hidden');
                    $('.' + $(this).attr('id')).removeClass('is_hidden');
                     if ($(event.target).attr('class') == 'icon-th is_selected') {
                        $localStorage.loadMoreStatus = "productPage";
                        if ($localStorage.loggedIn) {

                //             $http({
                //     method: 'GET',
                //     url: '/catalogue/',
                // }).then(function successCallback(response) {
                    //alert(JSON.stringify(response.data.data[0]))
                    // $scope.products = response.data.data
                     // scope.gridProducts = response.data;
                    //  if(response.data.length < 30){
                    //     $scope.loadmoreVisibilityStatus = false;
                    // }
                    // else{
                    //      $scope.loadmoreVisibilityStatus = true;
                    // }
                    // if (response.data.length === 0) {
                    //     $scope.product_pagination = $scope.product_pagination - 1;
                    //     $('#loadmore_error').addClass('is_visible');
                    // } else {$('#loadmore_error').removeClass('is_visible');
                    //     for (var i = 0; i < response.data.length; i++) {
                    //         ProductData.addData(response.data[i]);
                    //     }
                    //     $scope.gridProducts = ProductData.getData();
                    // }


                // }, function errorCallback(response) {
                //  });


                            //  $http({
                            //     method: 'GET',
                            //     url: '/web/buy/productview/' + scope.product_pagination,
                            // }).then(function successCallback(response) {
                            //      // scope.gridProducts = response.data;
                            //      for (var i = 0; i < response.data.length; i++) {
                            //         ProductData.addData(response.data[i]);
                            //     }
                            //     scope.gridProducts = ProductData.getData();


                            // }, function errorCallback(response) {
                            //  });


                            
                        } else {

                            $http({
                                method: 'GET',
                                url: '/web/buy/productview/' + scope.product_pagination,
                            }).then(function successCallback(response) {
                                 for (var i = 0; i < response.data.length; i++) {
                                    ProductData.addData(response.data[i]);
                                }
                                scope.gridProducts = ProductData.getData();


                            }, function errorCallback(response) {
                             });
                        }

                    } else if ($(event.target).attr('class') == 'icon-menu is_selected') {
                        $localStorage.loadMoreStatus = "sellerPage";
                         if ($localStorage.loggedIn) {
                             $http({
                                method: 'GET',
                                url: '/catalogue/sellerview/',// + scope.seller_pagination + '/' + $localStorage.id,
                                headers: {
                                    'X-UuidKey': $localStorage.uuid_keyx,
                                    'X-DeviceID': $localStorage.device_idx 
                                }
                            }).then(function successCallback(response) {
                                scope.feeds = response.data.data

                            }, function errorCallback(response) {
                             });
                        } else {
                             $http({
                                method: 'GET',
                                url: '/web/buy/sellerview/' + scope.seller_pagination + '/',
                                headers: {
                                    'X-UuidKey': $localStorage.uuid_keyx,
                                    'X-DeviceID': $localStorage.device_idx 
                                }
                            }).then(function successCallback(response) {
                                 // scope.feeds = response.data;
                                for (var i = 0; i < response.data.length; i++) {
                                    SellerData.addData(response.data[i]);
                                }
                                scope.feeds = SellerData.getData();

                            }, function errorCallback(response) {
                             });
                        }

                    } else {

                    }
                });
            }
        }
    })
    .directive("mouseHover", function(mouseHoverService) {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {

                $(".product-card").mouseover(function() {
                    if (!$(this).hasClass('current')) {
                        $(this).addClass('current');
                        var current = $(this).find('.is_current');
                        setTimeout(function() {
                            mouseHoverService.changeImage(current);
                        }, 100);
                    };
                });

                $(".product-card").mouseleave(function() {
                    $(this).removeClass('current');
                    $(this).find('.product-display a span').removeClass("is_current");
                    $(this).find('.product-display a span:last-child').addClass("is_current");
                });

            }
        }
    })
    .directive("thumbnailClick", function() {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                $('.thumbnails li').click(function() {
                     $('.thumbnails li').removeClass('is_current');
                    $(this).addClass('is_current');
                    $('.product-images .large img').attr('src', $('.thumbnails .is_current img').attr('src'))
                });
                $('.normal-sizes .size').click(function() {
                     $('.normal-sizes .size').removeClass('is_selected');
                    $(this).addClass('is_selected');
                });

            }
        }
    })
    .directive("selectSizeclick", function() {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                $('.normal-sizes .size').click(function() {
                     $('.normal-sizes .size').removeClass('is_selected');
                    $(this).addClass('is_selected');
                });

            }
        }
    })
    .directive("likeClick", function() {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                $('a .love-it .icon-heart-empty').click(function() {
                     $('.normal-sizes .size').removeClass('is_selected');
                    $(this).addClass('is_selected');
                });

            }
        }
    })
    .directive("deleteComment", function() {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                $(".comment").mouseover(function() {
                    $(this).find('.delete').addClass('is_visible');
                });
                $(".comment").mouseleave(function() {
                    $(this).find('.delete').removeClass('is_visible');
                });

            }
        }
    });
