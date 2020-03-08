'use strict';

/**
 * @ngdoc function
 * @name zapyle.controller:MainCtrl
 * @description
 * # HomeController Created by Albin CR
 * Controller of the zapyle
 */
angular.module('zapyle')
    .controller('ProductController', function($location, $rootScope, $timeout, $scope, $http, $routeParams, productService, UnlikeService, likeService, $localStorage) {
        var delta = Math.abs(Date.now() - PageStartTime) / 1000;
        var minutes = Math.floor(delta / 60) % 60;
        delta -= minutes * 60;
        var seconds = delta % 60; 
        mixpanel.track("User Event", {'Event Name': 'Changed page','to':window.location.href, 'time spent on page':minutes+' minutes '+seconds+' seconds', 'from': CurrentPage});
        CurrentPage = window.location.href
        PageStartTime = Date.now()
        no_of_products_viewed++
        $( "div" ).delegate( ".size-item", "click", function() {
            $('.size-item').removeClass('is_selected')
            $(this).addClass('is_selected')
            $scope.quantity_over_try = false;
            $scope.size_change()
        })
        // Select Size function
        // ---------------------------------------------------------------
        $rootScope.$on('dp', function(event, data) {
            $scope.profilePic = data
            $scope.user_id = $localStorage.user_id;

        });
        $scope.size_change = function(){
            $scope.item_quantity = 1
            $scope.size_selected_id = $('.size-item.is_selected').data('id')
            for(var i=0;i<$scope.selectedProduct.no_of_products.length;i++){
                if ($scope.selectedProduct.no_of_products[i]['size_id']==$scope.size_selected_id){
                    $scope.available_quantity = $scope.selectedProduct.no_of_products[i]['quantity']
                    $scope.$apply()
                }
            }
        }
        $scope.limit = 2;
        $scope.begin = 0;
        var SelectedSizeId = null;
        var SelectedQuantity;
        var ProductData;
        var Size_US = new Array();
        var Size_UK = new Array();
        var Size_EU = new Array();
        var CommentList = new Array();
        var FreeSize;
        var FSizeId;
        var FSizeQuantity;
        var QuantityCheck = false;
        var QuantityObject;
        var QuantityToShow = 1;
        var CommentTriggerVar = false;
        $scope.QuantityToShow = QuantityToShow;
        $scope.CommentTrigger = CommentTriggerVar;
        $scope.Comments = CommentList;
        var Products_Likes_Count;
        var Products_Comment_Count;
        var status = $localStorage.loggedIn
        $scope.status = status;
        $scope.QuantityCheck = QuantityCheck;
        $scope.profilePic = $localStorage.profile_picture;
        $scope.user_id = $localStorage.user_id;
        if(!$localStorage.cartList){
            $localStorage.cartList = []
        }
        console.log($localStorage.cartList)
        // $scope.size_type_change = function(s_type){
        //     if(s_type == "US"){
        //         $scope.size_to_show = 
        //     }
        // }


        // Main Get function
        // ---------------------------------------------------------------        
        // if ($localStorage.loggedIn) {
            $scope.$on("$destroy", function() {
                $("meta[data-zap='ppage']").remove()
                $('html').append(index_meta)
                document.title = "Zapyle | Discover, Sell and Buy Fashion"
            });
            $scope.metaTagImage = function(){
                console.log($scope.selectedProduct.thumbnails)
                var temp = ""
                for(var i in $scope.selectedProduct.thumbnails){
                    temp += '<meta data-zap="ppage" property="og:image" content="'+base_url+ $scope.selectedProduct.thumbnails[i].url.split('.')[0] + '.' + $scope.selectedProduct.thumbnails[i].url.split('.')[2] +'" />'
                }
                return temp
            }
            $scope.metaTagChange = function(){
                $("html").attr("itemtype", "http://schema.org/Product");
                document.title = $rootScope.itemprop_name = $scope.selectedProduct.title
                $("meta[data-zap='index']").remove()
                $('head').append(
                    '<meta data-zap="ppage" name="description" content="'+$scope.selectedProduct.description+'" />' +
                    '<meta data-zap="ppage" itemprop="name" content="'+ $scope.selectedProduct.title +'">' +
                    '<meta data-zap="ppage" itemprop="description" content="'+ $scope.selectedProduct.description +'">' +
                    '<meta data-zap="ppage" itemprop="image" content="'+base_url+$scope.selectedProduct.thumbnails[0].url.split('.')[0] + '.' + $scope.selectedProduct.thumbnails[0].url.split('.')[2]+'">'+
                    '<meta data-zap="ppage" name="twitter:card" content="product">'+
                    '<meta data-zap="ppage" name="twitter:site" content="@ZapyleSocial">'+
                    '<meta data-zap="ppage" name="twitter:title" content="'+$scope.selectedProduct.title+'">'+
                    '<meta data-zap="ppage" name="twitter:description" content="'+$scope.selectedProduct.description+'">'+
                    '<meta data-zap="ppage" name="twitter:image" content="'+base_url+$scope.selectedProduct.thumbnails[0].url.split('.')[0] + '.' + $scope.selectedProduct.thumbnails[0].url.split('.')[2]+'">'+
                    '<meta data-zap="ppage" name="twitter:data1" content="'+$scope.selectedProduct.listing_price+'">'+
                    '<meta data-zap="ppage" name="twitter:label1" content="Price">'+
                    '<meta data-zap="ppage" name="twitter:data2" content="'+$scope.selectedProduct.brand.brand+'">'+
                    '<meta data-zap="ppage" name="twitter:label2" content="Brand">'+
                    '<meta data-zap="ppage" property="og:title" content="'+$scope.selectedProduct.title+'" />'+
                    '<meta data-zap="ppage" property="og:type" content="article" />'+
                    '<meta data-zap="ppage" property="og:url" content="'+base_url+$location.path()+'" />'+
                    $scope.metaTagImage()+
                    '<meta data-zap="ppage" property="og:description" content="'+$scope.selectedProduct.description+'" />'+
                    '<meta data-zap="ppage" property="og:site_name" content="Zapyle" />'+
                    '<meta data-zap="ppage" property="og:price:amount" content="'+$scope.selectedProduct.listing_price+'" />'+
                    '<meta data-zap="ppage" property="og:price:currency" content="INR" />'
                )
            }

            $http({
                method: 'GET',
                url: "catalogue/singleproduct/" + $routeParams.productId,
            }).then(function successCallback(response) {
                if(response.data.status == 'success'){
                    show_loader('page', true);
                    show_loader('loading', false);
                    ProductData = response.data[0]
                    $scope.selectedProduct = response.data.data;
                    $scope.metaTagChange()
                    $scope.item_size = $scope.selectedProduct.size[0]
                    $scope.item_quantity = 1;
                    if($scope.item_size.category_type == 'FS'){
                        $scope.available_quantity = $scope.selectedProduct.no_of_products[0]['quantity'];
                    }
                    $scope.totalQuantity = 0
                    var no_of_products_list = $scope.selectedProduct.no_of_products
                    for(var i in no_of_products_list){
                        $scope.totalQuantity+=no_of_products_list[i]['quantity']
                    }
                    $scope.available_quantity = $scope.totalQuantity
                    console.log($scope.totalQuantity)
                    //$scope.getComments();
                    mixpanel.track("User Event", {'Event Name': 'Viewed Product', 'Product Title': $scope.selectedProduct.title, 'price': $scope.selectedProduct.listing_price, 'from page': 'Product'});
                }else{
                    window.location = '#/feeds' 
                }
            }, function errorCallback(response) {
            });
        
        
        $scope.increment_quantity = function(){
            if(!$('.size-item.is_selected').length && $scope.item_size.category_type != 'FS'){
                alert("Please select size")
                return false
            }
            if($scope.item_quantity < $scope.available_quantity ){
                $scope.item_quantity++
            }else{
                $scope.quantity_over_try = true;
                //$timeout(function() {$scope.quantity_over_try = false;}, 1000);
            }
        }
        $scope.decrement_quantity = function(){
            $scope.quantity_over_try = false;
            if($scope.item_quantity > 1){
                $scope.item_quantity--
            }   
        }
        $scope.SelectSize = function(sizeId) {
            SelectedSizeId = sizeId;
            if (!FreeSize) {
                var ArrayToCheck = Size_US.concat(Size_UK.concat(Size_EU));
                for (var i = 0; i < ArrayToCheck.length; i++) {
                    if (ArrayToCheck[i].id == sizeId) {
                        QuantityToShow = ArrayToCheck[i].quantity;
                     
                        if (parseInt(QuantityToShow) === 0) {
                            QuantityCheck = true;


                        } else {
                            QuantityCheck = false;
                        }
                    }
                }
            } else {
                QuantityToShow = FSizeQuantity;
                // if (parseInt(QuantityToShow) === 0) {
                 //     QuantityCheck = true;


                // } else {
                //     QuantityCheck = false;
                // }

            }
            $scope.QuantityCheck = QuantityCheck;
        }



        // Quantity ADD function
        // ---------------------------------------------------------------


        $scope.QuantityPlus = function() {
            var current = document.getElementById("quantity").innerHTML;
            var actual = QuantityToShow;
            if (SelectedSizeId == null) {
                 $.gritter.add({
                    title: 'Please select size first.',
                });
            } else {
                if (actual === parseInt(current)) {
                 } else if (actual > parseInt(current)) {
                     current = parseInt(current) + 1;
                    $scope.QuantityToShow = current;
                 } else {
                 }
            }
        }



        // Quantity minus function
        // ---------------------------------------------------------------        

        $scope.QuantityMinus = function() {
            var current = document.getElementById("quantity").innerHTML;
            var actual = QuantityToShow;
            if (SelectedSizeId == null) {
                 $.gritter.add({
                    title: 'Please select size first.',
                });
            } else {
                if (parseInt(current) === 1) {

                } else {
                    if (actual === parseInt(current)) {
                         current = parseInt(current) - 1;
                        $scope.QuantityToShow = current;
                     } else if (actual > parseInt(current)) {
                         current = parseInt(current) - 1;
                        $scope.QuantityToShow = current;
                     } else {
                     }
                }
            }
        }


        // Like Function
        // ------------------------------------------------------------
        $scope.product_like = function(album_id,status) {

            if ($localStorage.loggedIn) {
                if (status == "like"){
                    $scope.selectedProduct.likesCount++
                    $scope.selectedProduct.liked_by_user = true
                }else{
                    $scope.selectedProduct.likesCount--
                    $scope.selectedProduct.liked_by_user = false
                }
                var request = $http({
                    method: "POST",
                    url: '/user/like_product/',
                    data: {
                        'product_id': album_id,
                        'action': status,
                    },
                });
                request.success(function(rs) {
                    console.log(JSON.stringify(rs))
                    if(rs.status == "success"){
                        if($scope.sub_tab=='loves'){
                            $scope.get_loves(album_id)
                        }
                    }else if(rs.status == "error"){
                        if(status == 'like'){
                            $scope.selectedProduct.likesCount--
                            $scope.selectedProduct.liked_by_user = false
                        }else{
                            $scope.selectedProduct.likesCount++
                            $scope.selectedProduct.liked_by_user = true
                        }
                    }
                })
                request.error(function() {})
            } else {
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

        // Comment Functions
        // ---------------------------------------------------------------
        $scope.getComments = function(id) {
                $http({
                    method: 'GET',
                    url: "/catalogue/get_comments/?product_id=" + id,
                }).then(function successCallback(response) {
                     $scope.Comments = response.data.data;
                     mixpanel.track("User Event", {'Event Name': 'Looking at comments','Product Title':$scope.selectedProduct.title, 'number of comments':$scope.selectedProduct.commentCount, 'from page': 'product'});
                 }, function errorCallback(response) {
                 });
            }
            // -------------------------------------------------------------

        $scope.ShowComments = function() {
            $scope.CommentTrigger = true;
        }

        // -------------------------------------------------------------

        $scope.postComment = function() {
            if ($localStorage.loggedIn) {
                if(!$scope.commentText){
                    return false
                }
                var comment_txt = $scope.commentText
                $scope.commentText = ''
                $scope.selectedProduct.commentCount++
                var request = $http({
                    method: "POST",
                    url: '/catalogue/comment/',
                    data: {
                        'product': $routeParams.productId,
                        'comment': comment_txt,
                    },
                });
                request.success(function(rs) {
                    console.log(JSON.stringify(rs))
                    var new_comment = rs.data
                    new_comment['commented_by']={'id':$scope.user_id,'profile_pic': $scope.profilePic,'zap_username':$localStorage.zap_username}
                    $scope.Comments.push(new_comment)
                    $scope.commentText = "";
                    mixpanel.track("User Event", {'Event Name': 'comment on product', 'Product Title': $scope.selectedProduct.title, 'comment text': comment_txt, 'from page': 'product'});

                })
                request.error(function() {
                    selectedProduct.commentCount--
                 })
            } else {
                // window.location.href = "#/";
                // $.gritter.add({
                //     title: 'Oh Sorry. You are nt logged in!',
                // });
                $('#signup-login').addClass('is_visible');
            }
        }
        // if ($localStorage.cartList == undefined){
        //     $localStorage.cartList = []
        // }
        
        //  ` Function
        // -----------------------------------------
        //var zapCart = []
        // function addToCart(item){
        //     zapCart.push(item)
        // }

        function itemExists(item) {
          return $localStorage.cartList.some(function(el) {
            return el.product_id === item.product_id;
          }); 
        }

        function addItem(item) {
          $localStorage.cartList = []
          if (itemExists(item)) {
            alert("item already added.")
            return false; 
          }else{
            $localStorage.cartList.push(item)
            // alert("item added successfully.")
            return true
          }        
        }
        $scope.get_loves = function(id){
            $http({
                method: 'GET',
                url: "catalogue/get_likes/?product_id=" + id,
            }).then(function successCallback(response) {
                if(response.data.status == 'success'){
                    $scope.liked_users = response.data.data
                    mixpanel.track("User Event", {'Event Name': 'Looking at loves','Product Title':$scope.selectedProduct.title, 'number of loves':$scope.selectedProduct.likesCount, 'from page': 'product'});
                }else{
                    
                }
            }, function errorCallback(response) {
            });
        }
        $scope.Buy = function() {
            $localStorage.buyStartTime = Date.now()
            if($scope.item_size.category_type == 'FS'){
                //alert('FreeSize')
            }else{
                if ($('.size-item.is_selected').length) {
                    var selected_size = $('.size-item.is_selected').data('id')
                }else{
                    $('.size-item').addClass('is_selected')
                    setTimeout(function(){
                        $('.size-item').removeClass('is_selected')
                    },100)
                        
                        
                    
                    alert('Choose a size')
                    return true
                }
            }
            $scope.buy_pleasewait = true
            addItem({'product':$routeParams.productId,
                    'size':selected_size,
                    'quantity': $scope.item_quantity,
            })
            if (!$localStorage.loggedIn) {
                $('#zap_footer').removeClass('is_visible')
                $('#zap_footer').addClass('is_hidden')
                window.location.href = "#/checkout/"
                return true
            }
            var request = $http({
                    method: "POST",
                    url: '/zapcart/',
                    data: {
                        'test':'',
                        'from': 'website',
                        'cart_data': $localStorage.cartList},
                });
                request.success(function(rs) {
                    $('#zap_footer').removeClass('is_visible')
                    $('#zap_footer').addClass('is_hidden')

                    if(rs.status == 'success' || (rs.status == 'error' && rs.detail=="item already added")){
                        $scope.buy_pleasewait = false
                        window.location.href = "#/checkout/"
                    }else{
                        $scope.buy_pleasewait = false
                        alert("Zapyle server is encountering a problem. Please try later.")
                        window.location.href = "#/feeds"
                    }
             })
                request.error(function(rs) {
                    alert(JSON.stringify(rs))
            })
            
           
            // console.log($localStorage.cartList)
            // addToCart(zapCart)
            // console.log($scope.item_quantity)
            // if ($localStorage.loggedIn) {
            //     var quantity = document.getElementById("quantity").innerHTML;
            //      if (SelectedSizeId != null) {
            //         if (parseInt(quantity) != 0) {
            //             $scope.AddToCart();
            //         } else {
            //              $.gritter.add({
            //                 title: 'Please select quantity.',
            //             });
            //         }
            //     } else {
            //          $.gritter.add({
            //             title: 'Please select a size.',
            //         });
            //     }
            // } else {
            //     // window.location.href = "#/";
            //     // $.gritter.add({
            //     //     title: 'Oh Sorry. You are nt logged in!',
            //     // });
            //     $('#signup-login').addClass('is_visible');
            // }
        }


        //  Add to Cart
        // --------------------------------------------

        $scope.AddToCart = function() {
            var quantity = document.getElementById("quantity").innerHTML;
            var request = $http({
                method: "POST",
                url: '/cart/',
                data: {
                    // 'user_id': $localStorage.id,
                    // 'device_id': $localStorage.device_idx,
                    'product_id': $routeParams.productId,
                    'size': SelectedSizeId,
                    'quantity': quantity
                },
                headers: {
                    'X-UuidKey': $localStorage.uuid_keyx,
                    'X-DeviceID': $localStorage.device_idx
                }
            });
            request.success(function(rs) {
                 if (rs.error) {
                     $.gritter.add({
                        title: 'Oh Sorry. Product is not available!',
                    });

                } else {
                    $localStorage.buy_status = true;
                    window.location.href = "#/checkout/" + rs.cart_id + "/";

                }

            })
            request.error(function() {
             })
        }

        //  Delete Comment
        // ----------------------------------------------------
        $scope.test = function(){
            alert('est')
            return $scope
        }
        $scope.deleteComment = function(c) {
            if (!confirm("Are you sure you want to delete the comment?")){
                return false
            }
            if ($localStorage.loggedIn) {
                $scope.selectedProduct.commentCount--
                var request = $http({
                    method: "DELETE",
                    url: '/catalogue/comment/' + c.id +'/',
                });
                request.success(function(rs) {
                     if (rs.status == 'success') {
                        $scope.Comments.pop(c)
                    } else {
                        $scope.selectedProduct.commentCount++
                    }
                })
                request.error(function() {
                    $scope.selectedProduct.commentCount++
                 })
            } else {
                $('#signup-login').addClass('is_visible');
            }
        }
        $scope.deleteProduct = function(p_id){
            swal({   title: "Are you sure?",
                text: "",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#DD6B55",
                confirmButtonText: "Yes, delete it!",
                closeOnConfirm: false },
                function(){
                    $http({
                        method: 'DELETE',
                        url: '/catalogue/editproduct/' + p_id + '/',
                    }).error(function(error){console.log(error)
                        alert('Something went wrong')
                    }).then(function successCallback(response) {
                        console.log(response)  
                        if(response.data.status == 'success'){      
                            swal("Deleted!", "Your imaginary file has been deleted.", "success");
                            window.location = '#/feeds' 
                        }else{
                            swal("Cancelled", "Something went wrong :)", "error");
                        }
                    },
                    function errorCallback(response) {
                    });
                    
            });
            return false
            
        }
        $scope.admire = function(s_p) {
            if ($localStorage.loggedIn) {
                s_p.admire_or_not = !s_p.admire_or_not
                if (s_p.admire_or_not==true){
                    var status = 'admire'
                    s_p.admires_count++
                }else{
                    var status = 'unadmire'
                    s_p.admires_count--
                }
                $http.post('/user/admire/', {
                    'user': s_p.user.id,
                    'action' : status
                }).success(function(response) {
                    console.log(response)
                    if(response.status=="error"){
                        s_p.admire_or_not = !s_p.admire_or_not
                        if(status == 'admire'){
                            s_p.admires_count--
                        }else{
                            s_p.admires_count++
                        }
                    }
                }).error(function(response) {
                    //code here
                    
                });
            }else {
                $('#signup-login').addClass('is_visible');
            }
        }
        $scope.get_big_size = function(id,url){
            $scope.selectedProduct.image1 = url.replace(".100x100", ".1000x1000");
            $('.img_class').removeClass('is_current')
            $('#img'+id).addClass('is_current')
        }
        $scope.check_pincode = function(pin){
            $http({
                method: 'GET',
                url: "address/check_pincode/"+pin,
            }).then(function successCallback(response) {
                if(response.data.status == 'success'){
                    $scope.pin_flag = 200
                }else{
                    $scope.pin_flag = 404
                }
            }, function errorCallback(response) {
                $scope.pin_flag = 404
            });
        }
        $scope.open_size_guide = function(status){
            if(status == 'open'){
                $('.size-guide').addClass('is_visible')
            }else{
                $('.size-guide').removeClass('is_visible')
            }
        }
        $scope.open_condition_guide = function(status){
            if(status == 'open'){
                $('.condition-guide').addClass('is_visible')
            }else{
                $('.condition-guide').removeClass('is_visible')
            }
        }
    });
