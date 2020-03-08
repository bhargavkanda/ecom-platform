'use strict';

var homefeedApp = angular.module('zapyle')
    homefeedApp.run(['$route', '$rootScope', '$location', function ($route, $rootScope, $location) {
        var original = $location.path;
        $location.path = function (path, reload) {
            if (reload === false) {
                var lastRoute = $route.current;
                var un = $rootScope.$on('$locationChangeSuccess', function () {
                    $route.current = lastRoute;
                    un();
                });
            }
            return original.apply($location, [path]);
        };
    }])
    homefeedApp.controller('HomeFeedController', function($scope, $location, $routeParams, $http, likeService, UnlikeService, $localStorage, SellerData, ProductData) {
        $('#zap_footer').addClass('is_hidden')
        $('#zap_footer').removeClass('is_visible')
        $scope.test = function(title,index){
            $routeParams.itemName = title;
            if($('.class_'+index).hasClass( "selected" )){
                return false;
            }
            $('.filter-values li').removeClass('selected')
            $('.class_'+index).addClass('selected')
            window.history.pushState('','','#/'+$scope.type+'/'+title+'')
            $location.path('#/'+$scope.type+'/'+title+'', false);
            //alert($location.path)



            document.getElementById('page').style.display = false ? 'block' : 'none';
            document.getElementById('loading').style.display = true ? 'block' : 'none';
            console.log(title,type)
            if(title == 'All'){
                var my_url = '/catalogue/?page=1'
            }else{
                var my_url = "catalogue/"+$scope.type+"/" + title+'/1'
            }
            $http({
            method: 'GET',
            url: my_url,
        }).then(function successCallback(response) {
            if(response.data.status == 'success'){
                firstPageClick = true
                show_loader('page', true);
                show_loader('loading', false);
                $scope.loadMore_flag = false
                $scope.logged_userId = $localStorage.user_id
                
                $scope.products = response.data.data.data
                // $scope.new_products = response.data.data.data
                // for(var i in $scope.new_products){
                //     $scope.products.push($scope.new_products[i])
                // }
                $scope.loadmoreVisibilityStatus = response.data.data['next']
                $scope.current_page = response.data.data['page']
                console.log(response)
                $scope.totalPages = response.data.data.total_pages
                $('#zap_footer').addClass('is_visible')
                $('#zap_footer').removeClass('is_hidden')
            }})
        }
        $('.filter-types').click(function(){
            $('.types').toggleClass('is_visible')
        });
        $(document).mouseup(function (e)
        {
            var container = $(".sub-menu");
            if (!container.is(e.target))
            {
                // $('.types').removeClass('is_visible');
            }
        });


        $('ul.types li').click(function(e) 
        {
            $scope.type = $(this).children('span').text().toLowerCase();
            $routeParams.itemName = 'All';
            if(!$localStorage.filter_items){
                $http({
                    method: 'GET',
                    url: '/filters/webFilterItems/',
                }).then(function successCallback(response) {
                    $localStorage.filter_items = response.data.data
                    
                    $scope.sub_types = $localStorage.filter_items[$scope.type]
                    setTimeout(function(){
                        setFiltersWidth();
                    });
                    
                })
            }else{
                var opt = $(this).attr('data');
                console.log(opt, ">>>>>")
                $scope.type = opt
                $scope.sub_types = $localStorage.filter_items[opt]
            }
            // $('.types').removeClass('is_visible');
            // alert()
            // alert(window.location.hash);
            if ('#/'+$scope.type+'/All' === window.location.hash) {
                return 0;
            }
            $('.chosen-type').text($(this).text());
            window.history.pushState('','','#/'+$scope.type+'/All')
            $location.path('#/'+$scope.type+'/All', false);
            document.getElementById('page').style.display = false ? 'block' : 'none';
            document.getElementById('loading').style.display = true ? 'block' : 'none';
            $scope.getGridPageData(1, true);
            $scope.$apply()
            setFiltersWidth();
            $('.filter-values li').removeClass('selected');
            $('.class_0').addClass('selected');
            
        } )

        $(window).load(function() {
            setFiltersWidth();
        });
        $(window).resize(function() {
            setFiltersWidth();
        });
        function setFiltersWidth() {
            filter_options = $('.filter-values li');
            total_width = 20;
            filter_options.each(function() {
                width = $(this).width();

                total_width = total_width + width;
            });
            $('.filter-values').width(total_width);
        }
        
        if(!$localStorage.filter_items){
            $http({
                method: 'GET',
                url: '/filters/webFilterItems/',
            }).then(function successCallback(response) {
                $localStorage.filter_items = response.data.data
                if(!$routeParams.itemName){
                    $scope.type = 'category'
                    $scope.sub_types = $localStorage.filter_items['category']
                    setTimeout(function(){
                        setFiltersWidth();
                    });
                }else{
                    $scope.type = type
                    $scope.sub_types = $localStorage.filter_items[type]
                    setTimeout(function(){
                        setFiltersWidth();
                    });
                }
            })
        }
        //if (typeof jQuery != 'undefined') {

//     alert("jQuery library is loaded!");

// }else{

//     alert("jQuery library is not found!");

// }
    
        var delta = Math.abs(Date.now() - PageStartTime) / 1000;
        var minutes = Math.floor(delta / 60) % 60;
        delta -= minutes * 60;
        var seconds = delta % 60;
        mixpanel.track("User Event", {'Event Name': 'Changed page','to':window.location.href,  'time spent on page':minutes+' minutes '+seconds+' seconds', 'from': CurrentPage});
        CurrentPage = window.location.href
        PageStartTime = Date.now()
        $scope.user_id = $localStorage.user_id
        var firstPageClick = true;
        $scope.totalPages=1;
        //alert(JSON.stringify(mixPanelVar))

//         $scope.show_pagination = function(){
//             $('#paginationholder').html('');
//             $('#paginationholder').html('<ul id="pagination-demo" class="pagination-sm"></ul>');
//             $('#pagination-demo').twbsPagination({
//                 totalPages: $scope.totalPages,
//                 visiblePages: 10,
//                 onPageClick: function (event, page) {
//                     if(firstPageClick) {
//                        firstPageClick = false;
//                        return;
//                     }
//                     document.getElementById('page').style.display = false ? 'block' : 'none';
//                     document.getElementById('loading').style.display = true ? 'block' : 'none';
//                     if($scope.pageView == "productPage"){
//                     $http({
//                     method: 'GET',
//                     url: '/catalogue/?q='+$scope.search_product+'&page='+page+'&perpage='+parseInt($scope.itemsPerPageproduct),

//                     }).then(function successCallback(response) {
//                         show_loader('page', true);
//                         show_loader('loading', false);
//                         $scope.products = response.data.data.data
//                         $scope.totalPages = response.data.data.total_pages
//                         }, function errorCallback(response) {
//                             show_loader('page', true);
//                             show_loader('loading', false);
//                      });
//                 }else{
//                     $http({
//                     method: 'GET',
//                     url: '/catalogue/sellerview/?q='+$scope.search_product+'&page='+page+'&perpage='+parseInt($scope.itemsPerPageseller),// + scope.seller_pagination + '/' + $localStorage.id,
//                 }).then(function successCallback(response) {
//                     show_loader('page', true);
//                     show_loader('loading', false);
//                     $scope.feeds = response.data.data.data
//                     $scope.totalPages = response.data.data.total_pages
// }, function errorCallback(response) {
//                     show_loader('page', true);
//                     show_loader('loading', false);
//                  });
//                 }
//                 }
//             });
//         }
//         $scope.perpageChange = function(){
//             if($scope.pageView == "productPage"){
//                 $scope.getGridPageData(1);
//             }else{
//                 $scope.getSellerPageData(1);
//             }
//         }
        $scope.feeds = []
        $scope.getSellerPageData = function(page){
                firstPageClick = true
                $http({
                    method: 'GET',
                    url: '/catalogue/sellerview/?q='+$scope.search_product+'&page='+page+'&perpage='+parseInt($scope.itemsPerPageseller),// + scope.seller_pagination + '/' + $localStorage.id,
                }).then(function successCallback(response) {
                    show_loader('page', true);
                    show_loader('loading', false);
                    $scope.loadMore_flag = false
                    // $scope.feeds = response.data.data.data
                    //$scope.totalPages = response.data.data.total_pages
                    $scope.new_products_seller = response.data.data.data
                    for(var i in $scope.new_products_seller){
                        $scope.feeds.push($scope.new_products_seller[i])
                    }
                    $scope.loadmoreVisibilityStatus = response.data.data['next']
                    $scope.current_page = response.data.data['page']
                    $scope.totalPages = response.data.data.total_pages
                    //$scope.show_pagination()
                }, function errorCallback(response) {
                    show_loader('page', true);
                    show_loader('loading', false);
                 });
            
        }
        $scope.products = []
        $scope.getGridPageData = function(page, replace) {
                firstPageClick = true

            
            // if ($localStorage.loggedIn) {
                 $http({
                    method: 'GET',
                     url: '/catalogue/?page='+page+'&perpage='+parseInt($scope.itemsPerPageproduct),

                }).then(function successCallback(response) {
                    show_loader('page', true);
                    show_loader('loading', false);
                    $scope.loadMore_flag = false
                    //alert(JSON.stringify(response.data.data[0]))
                    // var hege = ["Cecilie", "Lone"];
                    // var stale = ["Emil", "Tobias", "Linus"];
                    // var children = hege.concat(stale);
                    // alert(JSON.stringify(children))



                    $scope.logged_userId = $localStorage.user_id
                    
                    $scope.new_products = response.data.data.data
                    if (replace === true) {
                        $scope.products = $scope.new_products;
                    } else {
                        for(var i in $scope.new_products){
                            $scope.products.push($scope.new_products[i])
                        }
                    }
                    
                    $scope.loadmoreVisibilityStatus = response.data.data['next']
                    $scope.current_page = response.data.data['page']
                    console.log(response)
                    // $('#pagination-demo').html('');
                    //$('#pagination-demo').html('<ul id="pagination-demo" class="pagination-sm"></ul>');
                    $scope.totalPages = response.data.data.total_pages
                    //$scope.show_pagination()
                    //alert(JSON.stringify(response.data.data))

                    $('#zap_footer').removeClass('is_hidden')
                    $('#zap_footer').addClass('is_visible')
                }, function errorCallback(response) {
                    show_loader('page', true);
                    show_loader('loading', false);
                    $('#zap_footer').removeClass('is_hidden')
                    $('#zap_footer').addClass('is_visible')
                 });
        }






        $scope.limit = 2;
        $scope.begin = 0;
        $scope.seller_pagination = 1;
        $scope.product_pagination = 1;
        var status = $localStorage.loggedIn
        $scope.status = status;
        SellerData.emptyData();
        ProductData.emptyData();
        $localStorage.loadMoreStatus = "productPage";
        var PageStatus = $localStorage.loadMoreStatus;


        $scope.itemsPerPageproduct='28'
        $scope.itemsPerPageseller='16'

        // Get Grid page data
        // ---------------------------------------------------------

        //  Like onclick function
        // ----------------------------------------
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
                    }else{
                        if (status == 'like'){
                            mixpanel.track("User Event", {'Event Name': 'Love a product', 'Title of product': grid.title, 'price': grid.listing_price, 'from page': 'feed'});
                        }
                    }
                })
                request.error(function() {})
            }else{
                $('#signup-login').addClass('is_visible');
            }
        }
        

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
        $scope.product_search = function(){
            if($scope.pageView == "sellerPage"){
                $scope.getGridPageData(1, false);
            }
            if($scope.pageView == "productPage"){
                $scope.getSellerPageData(1);
            }
        }

        //  Load more function
        // ---------------------------------------------------
        $scope.loadMore = function() {
            if($scope.loadMore_flag){
                return false
            }
            $scope.loadMore_flag = true
            if($routeParams.itemName){
                if($routeParams.itemName == 'All'){
                    $scope.getGridPageData(parseInt($scope.current_page)+1, false);
                }else{
                    load_filtered_data(parseInt($scope.current_page)+1)
                }
            }
            else if($scope.pageView == "productPage"){
                $scope.getGridPageData(parseInt($scope.current_page)+1, false);
            }
            else if($scope.pageView == "sellerPage"){
                $scope.getSellerPageData(parseInt($scope.current_page)+1)
            }            
            
            // if ($localStorage.loadMoreStatus === 'sellerPage') {
            //      $scope.seller_pagination = $scope.seller_pagination + 1;
            //     $scope.getSellerPageData();
            //     // $scope.feeds = SellerFeedView;

            // } else {
            //      $scope.product_pagination = $scope.product_pagination + 1;
            //     $scope.getGridPageData();
            //     // $scope.gridProducts = ProductFeedarray;
            // }
        }
        //$localStorage.pageView = "productPage"
        $scope.pageView = "productPage";
        $scope.productView = function(){
            $scope.feeds = []
            if($scope.pageView == "sellerPage"){
                document.getElementById('page').style.display = false ? 'block' : 'none';
                document.getElementById('loading').style.display = true ? 'block' : 'none';
                $('.is_selected.icon-menu').removeClass('is_selected');
                $('.icon-th').addClass('is_selected');
                // $('.content.seller-view').addClass('is_hidden');
                // $('.content.product-view').removeClass('is_hidden');
                $scope.getGridPageData(1, false);
                $scope.pageView = "productPage";
                $localStorage.pageView = "productPage"
            }
        }
        $scope.sellerView = function(){
            $scope.products = []
            if($scope.pageView == "productPage"){
                document.getElementById('page').style.display = false ? 'block' : 'none';
                document.getElementById('loading').style.display = true ? 'block' : 'none';
                $('.is_selected.icon-th').removeClass('is_selected');
                $('.icon-menu').addClass('is_selected');
                // $('.content.seller-view').removeClass('is_hidden');
                // $('.content.product-view').addClass('is_hidden');
                $scope.getSellerPageData(1);
                $scope.pageView = "sellerPage";
                $localStorage.pageView = "sellerPage"
            }
        }
        
        //  Admire function
        // ----------------------------------------------------

        $scope.admire = function(feed) {
            if ($localStorage.loggedIn) {
                feed.admire_or_not = !feed.admire_or_not
                if (feed.admire_or_not==true){
                    var status = 'admire'
                    feed.admires_count++
                }else{
                    var status = 'unadmire'
                    feed.admires_count--
                }
                $http.post('/user/admire/', {
                    'user': feed.id,
                    'action' : status
                }).success(function(response) {
                    if(response.status=="error"){
                        feed.admire_or_not = !feed.admire_or_not
                    }else{
                        mixpanel.track("User Event", {'Event Name': 'Admire user', 'username':feed.zap_username, 'from page': 'feeds'});
                    }
                }).error(function(response) {
                    //code here
                });
            }else {
                $('#signup-login').addClass('is_visible');
            }
        }
        
        //$scope.getSellerPageData(1);
        
    $scope.start_execution = function(){
        if ($localStorage.pageView == "sellerPage"){
           $scope.pageView = 'sellerPage'
           document.getElementById('page').style.display = false ? 'block' : 'none';
            document.getElementById('loading').style.display = true ? 'block' : 'none';
            $('.is_selected.icon-th').removeClass('is_selected');
            $('.icon-menu').addClass('is_selected');
            $scope.getSellerPageData(1);   
        }else{
             $scope.getGridPageData(1, false);                 
        }
    }
    function load_filtered_data(page){
        firstPageClick = true
        $http({
            method: 'GET',
            url: "catalogue/"+$scope.type+"/"+$routeParams.itemName+"/"+page,
        }).then(function successCallback(response) {
            show_loader('page', true);
            show_loader('loading', false);
            $scope.loadMore_flag = false
            $scope.new_products_seller = response.data.data.data
            for(var i in $scope.new_products_seller){
                $scope.products.push($scope.new_products_seller[i])
            }
            $scope.loadmoreVisibilityStatus = response.data.data['next']
            $scope.current_page = response.data.data['page']
            $scope.totalPages = response.data.data.total_pages
            $('#zap_footer').removeClass('is_hidden')
            $('#zap_footer').addClass('is_visible')
        }, function errorCallback(response) {
            show_loader('page', true);
            show_loader('loading', false);
            $('#zap_footer').removeClass('is_hidden')
            $('#zap_footer').addClass('is_visible')
         });
    }
    var type = ''
    if($routeParams.itemName){
        type = window.location.hash.split("/")[1]
        $scope.type = type
        $('.chosen-type').text(type);
        $scope.itemName = $routeParams.itemName
        setFiltersWidth();
        if($localStorage.filter_items){
            $scope.sub_types = $localStorage.filter_items[type]
            setTimeout(function(){
                setFiltersWidth();
            });
        }
        if($scope.itemName == 'All'){
            $('.class_0').addClass('selected')
            $scope.getGridPageData(1, false);
            // if($localStorage.filter_items){
            //     $scope.sub_types = $localStorage.filter_items[type]
            //     setTimeout(function(){
            //         setFiltersWidth();
            //     }
            // }
            return false;
        }
        $http({
            method: 'GET',
            url: "catalogue/"+type+"/" + $routeParams.itemName+'/1',
        }).then(function successCallback(response) {
            if(response.data.status == 'success'){


                    firstPageClick = true
                    show_loader('page', true);
                    show_loader('loading', false);
                    $scope.loadMore_flag = false
                    $scope.logged_userId = $localStorage.user_id
                    
                    $scope.products = response.data.data.data
                    // $scope.new_products = response.data.data.data
                    // for(var i in $scope.new_products){
                    //     $scope.products.push($scope.new_products[i])
                    // }
                    $scope.loadmoreVisibilityStatus = response.data.data['next']
                    $scope.current_page = response.data.data['page']
                    console.log(response)
                    $scope.totalPages = response.data.data.total_pages
                    $('#zap_footer').removeClass('is_hidden')
                    $('#zap_footer').addClass('is_visible')
            }})
    }else{
        if($localStorage.filter_items){
            $scope.type = 'category'
            $scope.sub_types = $localStorage.filter_items['category']
            setTimeout(function(){
                setFiltersWidth();
            });
        }
        $scope.getGridPageData(1, false);
    }
});