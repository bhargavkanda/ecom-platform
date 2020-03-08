'use strict';

/**
 * @ngdoc overview
 * @name zapyle
 * @description
 * # zapyle created by Albin CR
 *
 * Main module of the application.
 */
var zapyle = angular.module('zapyle', [
        // 'ngAnimate',
        'ngCookies',
        'ngResource',
        'ngRoute',
        'ngTouch',
        'satellizer',
        'ngStorage',
        'ngMessages',
        'angular-img-cropper'
    ])
    .run(function($rootScope, $cookies) {
      $cookies.put('PLATFORM', 'WEBSITE');
      $rootScope.$on("$locationChangeStart", function(event, next, current) { 
        ga('send', {
         'hitType': 'pageview',
         'page': window.location.hash,
         'title' : document.getElementsByTagName("title")[0].innerHTML,
        });  
      });
    })
    .config(function($routeProvider, $httpProvider, $interpolateProvider) {
        $interpolateProvider.startSymbol('[[').endSymbol(']]');


        /////////////////////////////////////
        //             Routes              //
        //                                //
        ////////////////////////////////////
        $routeProvider
            .when('/', {
                templateUrl: '/zapstatic/frontend/views/main.html?_='+ZAP_ENV_VERSION,
                controller: 'HomeController'
            })
            // .when('/access_token=:accessToken', {
            //     templateUrl: '/zapstatic/frontend/views/main.html',
            //     controller: 'TokenController'
            // })
            .when('/product/:productId', {
                templateUrl: '/zapstatic/frontend/views/product.html?_='+ZAP_ENV_VERSION,
                controller: 'ProductController'
            })
            .when('/feeds', {
                templateUrl: '/zapstatic/frontend/views/buy.html?_='+ZAP_ENV_VERSION,
                controller: 'HomeFeedController'
            })
            .when('/onboarding', {
                templateUrl: '/zapstatic/frontend/views/onboarding.html?_='+ZAP_ENV_VERSION,
                controller: 'BordingController'
            })
            .when('/checkout', {
                templateUrl: '/zapstatic/frontend/views/checkout.html?_='+ZAP_ENV_VERSION,
                controller: 'CheckoutController'
            })
            .when('/ordersummary/:OrderId', {
                templateUrl: '/zapstatic/frontend/views/order-summary.html?_='+ZAP_ENV_VERSION,
                controller: 'SummaryController'
            })
            .when('/discover', {
                templateUrl: '/zapstatic/frontend/views/discover.html?_='+ZAP_ENV_VERSION
            })
            .when('/sell', {
                templateUrl: '/zapstatic/frontend/views/sell.html?_='+ZAP_ENV_VERSION
            })
            .when('/zapyle-blog', {
                templateUrl: '/zapstatic/frontend/views/blogger.html?_='+ZAP_ENV_VERSION
            })
            .when('/about-us', {
                templateUrl: '/zapstatic/frontend/views/about-us.html?_='+ZAP_ENV_VERSION
            })
            .when('/contact-us', {
                templateUrl: '/zapstatic/frontend/views/contact-us.html?_='+ZAP_ENV_VERSION
            })
            .when('/press', {
                templateUrl: '/zapstatic/frontend/views/press.html?_='+ZAP_ENV_VERSION
            })
            .when('/shipping-returns-policy', {
                templateUrl: '/zapstatic/frontend/views/shipping-returns.html?_='+ZAP_ENV_VERSION
            }).when('/terms-conditions', {
                templateUrl: '/zapstatic/frontend/views/terms-conditions.html?_='+ZAP_ENV_VERSION
            })
            .when('/profile/:profileId', {
                templateUrl: '/zapstatic/frontend/views/profile.html?_='+ZAP_ENV_VERSION,
                controller: 'ProfileController'
            })
            .when('/blogger/:bloggerName', {
                templateUrl: '/zapstatic/frontend/views/blogger.html?_='+ZAP_ENV_VERSION,
                controller: 'BloggerController'
            })
            .when('/zapupload', {
                templateUrl: '/zapstatic/frontend/views/upload.html?_='+ZAP_ENV_VERSION,
                controller: 'UploadCtrl'
            })
            .when('/paymentcheck', {
                templateUrl: '/zapstatic/frontend/views/paymentcheck.html?_='+ZAP_ENV_VERSION,
                controller: 'PaymentCheckCtrl'
            })
            .when('/editproduct/:productId', {
                templateUrl: '/zapstatic/frontend/views/editproduct.html?_='+ZAP_ENV_VERSION,
                controller: 'editproductController'
            })
            .when('/summary/', {
                templateUrl: '/zapstatic/frontend/views/summary.html?_='+ZAP_ENV_VERSION,
                controller: 'summaryController'
            })
            .when('/login/', {
                templateUrl: '/zapstatic/frontend/views/login.html?_='+ZAP_ENV_VERSION,
                controller: 'PopController'
            })
            .when('/category/:itemName', {
                templateUrl: '/zapstatic/frontend/views/buy.html?_='+ZAP_ENV_VERSION,
                controller: 'HomeFeedController'
            })
            .when('/occasion/:itemName', {
                templateUrl: '/zapstatic/frontend/views/buy.html?_='+ZAP_ENV_VERSION,
                controller: 'HomeFeedController'
            })
            .when('/style/:itemName', {
                templateUrl: '/zapstatic/frontend/views/buy.html?_='+ZAP_ENV_VERSION,
                controller: 'HomeFeedController'
            })
            .when('/brand/:itemName', {
                templateUrl: '/zapstatic/frontend/views/buy.html?_='+ZAP_ENV_VERSION,
                controller: 'HomeFeedController'
            }).when('/authenticity', {
                templateUrl: '/zapstatic/frontend/views/auth.html?_='+ZAP_ENV_VERSION,
                //controller: 'HomeFeedController'
            })
            .otherwise({
                redirectTo: '/'
            });
        ////////////////////////////////////
        //              Oauth             //
        //                                //
        ////////////////////////////////////

      $httpProvider.defaults.xsrfCookieName = 'csrftoken';
      $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
      $httpProvider.defaults.headers.common["X-Requested-With"] = 'XMLHttpRequest';
      

        // 
    });

////////////////////////////////////
//           Global               //
//         Variables              //
////////////////////////////////////
var base_url = location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '');
var index_meta ='<meta data-zap="index" name="description" content="Zapyle is a fun, easy and social way to shop like a pro. The most chic closets in India to buy from and your own to sell." />'+
                '<meta data-zap="index" itemprop="name" content="Zapyle | Discover, Sell and Buy Fashion">'+
                '<meta data-zap="index" itemprop="description" content="Zapyle is a fun, easy and social way to shop like a pro. The most chic closets in India to buy from and your own to sell.">'+
                '<meta data-zap="index" itemprop="image" content="Zapyle logo">'+
                '<meta data-zap="index" name="twitter:card" content="summary">'+
                '<meta data-zap="index" name="twitter:site" content="@ZapyleSocial">'+
                '<meta data-zap="index" name="twitter:title" content="Zapyle | Discover, Sell and Buy Fashion">'+
                '<meta data-zap="index" name="twitter:description" content="Zapyle is a fun, easy and social way to shop like a pro. The most chic closets in India to buy from and your own to sell.">'+
                '<meta data-zap="index" name="twitter:image" content="'+ base_url +'" />'+
                '<meta data-zap="index" property="og:title" content="Zapyle | Discover, Sell and Buy Fashion" />'+
                '<meta data-zap="index" property="og:type" content="website" />'+
                '<meta data-zap="index" property="og:url" content="'+ base_url +'" />'+
                '<meta data-zap="index" property="og:image" content="Zapyle logo" />'+
                '<meta data-zap="index" property="og:description" content="Zapyle is a fun, easy and social way to shop like a pro. The most chic closets in India to buy from and your own to sell." />'+
                '<meta data-zap="index" property="og:site_name" content="Zapyle" />'
////////////////////////////////////
//           Facebook             //
//            Login               //
////////////////////////////////////


window.fbAsyncInit = function() {
    FB.init({
        appId: FB_CLIENT_ID,
        xfbml: true,
        version: 'v2.5'
    });
};

(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {
        return;
    }
    js = d.createElement(s);
    js.id = id;
    js.src = '//connect.facebook.net/en_US/sdk.js';
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));
