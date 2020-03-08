zapyle.filter('unsafe', function($sce) {
    return function(val) {
        return $sce.trustAsHtml(val);
    };
});
zapyle.directive('onFinishRender', function ($timeout) {
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            if (scope.$last === true) {
                $timeout(function () {
                    scope.$emit(attr.onFinishRender);
                });
            }
        }
    }
});
zapyle.controller('BlogPostController', function($scope, $http, $filter, loveService) {
    $scope.fetching=true;
    if (window.location.pathname.split('/')[3]) {
        $http.get("/zapblog/post/"+window.location.pathname.split('/')[3]).
        success(function(response) {
            if (response.status == "success") {
                $scope.posts = [response.data];
                $scope.reachedEnd = false;
                $scope.fetching = false;
                setTimeout(function() {
                    $('.medium-insert-images-slideshow').cycle({slides: 'figure'});
                });
            } else {
                Materialize.toast(response.detail.error, 3000);
            }
        }).error(function() {
            Materialize.toast('Error', 3000);
        });
    }
    $scope.$on('materializeSelect', function(ngRepeatFinishedEvent) {
        $('select').material_select();
    });
    $scope.love_or_unlove_blog = function(blog, event) {
        if (blog.loved_by_user == false) {
            $(event.currentTarget).addClass('loved');
            $http.post("/zapblog/love_blog/"+blog.id, {}).
            success(function(response) {
                if (response.status == "success") {
                    blog.loved_by_user = true;
                } else {
                    Materialize.toast(response.detail.error, 3000);
                }
            }).error(function() {
                Materialize.toast('Error', 3000);
            });
        } else if (blog.loved_by_user == true) {
            $(event.currentTarget).removeClass('loved');
            $http.delete("/zapblog/love_blog/"+blog.id, {}).
            success(function(response) {
                if (response.status == "success") {
                    blog.loved_by_user = false;
                } else {
                    Materialize.toast(response.detail.error, 3000);
                }
            }).error(function() {
                Materialize.toast('Error', 3000);
            });
        }
    }
    $scope.get_next_blog = function() {
        if(!$scope.reachedEnd) {
            last_blog = $scope.posts[$scope.posts.length - 1];
            $http.get("/zapblog/next_blog/"+last_blog.id).
            success(function(response) {
                if (response.status == "success") {
                    $scope.posts.push.apply($scope.posts, [response.data]);
                    $scope.fetching = false;
                    setTimeout(function() {
                        $('.medium-insert-images-slideshow').cycle({slides: 'figure'});
                    });
                } else {
                    $scope.reachedEnd = true;
                    Materialize.toast(response.detail.error, 3000);
                }
            }).error(function() {
                $scope.reachedEnd = true;
                Materialize.toast('Error', 3000);
            });
        }
    }

    $scope.gotoToCart = function(){
        $scope.cart();
        $('.overlay').removeClass('is_visible');
        $('.goto_btn').addClass('is_hidden');
        $('.cart_btn').removeClass('is_hidden')
        $('.right_panel_inner > div').removeClass('is_visible');
        $($('.goto_btn').attr('data-activates')).addClass('is_visible');
        $('.right_panel').addClass('is_visible');
        window.history.pushState('', '', window.location.href+'/#rp_cart')
    }
    $scope.addToCart = function(product=null, size=null, quantity=null){
        if (product == null) {
            product_id = $('.quick_product').data('id');
        } else {
            $scope.product = product;
            product_id = product.id;
        }
        if (size==null) {
            if(!$('.size_item.selected').length){
                Materialize.toast('Please select a Size.', 3000);
                return false;
            }
            size = $('.size_item.selected').data('id');
        }
        if (quantity==null) {
            quantity = $scope.qty;
            var available_size = $scope.product.size.length
            if(available_size==1){
                $("[data-id="+$scope.product.size[0]['id']+"]").addClass('selected')
                $scope.availble_qty = $scope.product.size[0]['quantity']
                if($scope.availble_qty>1){$('.get_quantity').removeClass('is_hidden')}
            }
        }
        if(ZL == 'True' && USER_NAME!='None') {
            var data = {'cart_data':{'quantity':quantity,'product':product_id,'size':size}}
            if ($scope.appliedOffer) {
                data['cart_data']['offer'] = $scope.appliedOffer;
            }
            $http.post('/zapcart/?web=true',data).
                success(function(rs, status, headers, config) {
                if (rs.status == "success"){
//                    $('.cart_btn').addClass('is_hidden')
//                    $('.goto_btn').removeClass('is_hidden')
                    Materialize.toast(rs.data.message, 3000);
                    $('#toteBadge').text(rs.data.count)
                    clevertap.event.push("add_to_tote", {
                        "user_id":USER_ID,
                        "product_id":product_id,
                        "size":$('.size_item.selected').text(),
                        "quantity":quantity,
                        "price":$('.z_new').text().replace(',',''),
                    });
                }else{
                    Materialize.toast(rs.detail, 3000);
                }
            })
        } else {
            var count = parseInt($('#toteBadge').text())
            if($localStorage.tote){
                var cart_data = $localStorage.tote['cart_data']
                for(i in cart_data){
                    if(cart_data[i]['product'] == product_id && cart_data[i]['size'] == size){
//                        $('.cart_btn').addClass('is_hidden')
//                        $('.goto_btn').removeClass('is_hidden')
                        Materialize.toast("This item is already added in your tote.", 3000);
                        return false;
                    }
                }
            }else{
                $localStorage.tote = {'cart_data' : []}
            }
            $localStorage.tote['cart_data'].push({
                'product_quantity':quantity,'product':product_id,
                'quantity_available':$scope.availble_qty,
                'size':size,
                'product_image': $scope.product.image,
                'original_price' :$scope.product.original_price,
                'listing_price' : $scope.product.listing_price,
                'product_brand' : $scope.product.listing_price.brand,
                'title' : $scope.product.title,
                'product_size' : $scope.sizes[size],
                'offer': $scope.appliedOffer,
                'offer_benefit': $scope.product.listing_price - $scope.offerPrice,
                'id' : Math.floor((Math.random() * 100) + 1)
            })
            $('.get_size_quantity').removeClass('is_visible')
//            $('.cart_btn').addClass('is_hidden')
//            $('.goto_btn').removeClass('is_hidden')
            Materialize.toast("Item added successfully.", 3000);
            $('#toteBadge').text(++count)
    	}
    }

    $scope.addToCart_bulk = function(post, event) {
        items = $(event.currentTarget).closest('.look_layout').find('.product_item.selected');
        if (items.length == 0) {
            Materialize.toast('Select products to add to Cart', 3000);
        } else {
            items.each(function() {
                if ($(this).find('.sizes select option:selected').length==0 || $(this).find('.sizes select option:selected').val()=='') {
                    Materialize.toast('Select sizes for the products you add to Tote.', 3000);
                    return false;
                } else {
                    product_id = $(this).data('id');
                    product = $filter('filter')(post.products, { id: product_id  }, true)[0];
                    size = $(this).find('.sizes select option:selected').val();
                    $scope.addToCart(product, size, 1);
                }
            });
        }
    }

    $scope.love = function(product, event){
        if(ZL == 'True' && USER_NAME!='None'){
            if(product.loved_by_user){
                loveService.postlove(product.id,'unlike');
                product.loved_by_user = false;
                $(event.currentTarget).removeClass('loved');
            }else{
                loveService.postlove(product.id,'like');
                product.loved_by_user = true;
                $(event.currentTarget).addClass('loved');
            }
        }else{
            $scope.$emit('setLoginPurpose', 'love a product' );
            $('.right_panel_inner > div').removeClass('is_visible');
            $($('.login_label').attr('data-activates')).addClass('is_visible');
            $('.right_panel').addClass('is_visible');
        }
    }

    $('body').on('click', '.look_layout .product_item *', function(event) {
        if (!$(this).is('a')) {
            if(!$(this).closest('.product_item').hasClass('sold_out')) {
                $(this).closest('.product_item').toggleClass('selected');
            }
        } else {
            event.stopPropagation();
        }
    });


    $(window).scroll(function() {
        var winTop = $(this).scrollTop();
        var $divs = $('.blog_post');
        var top = $.grep($divs, function(item) {
            return $(item).position().top <= winTop + 200 && $(item).position().bottom > winTop;
        });
        $divs.removeClass('current');
        $(top).addClass('current');
        if (winTop + $(window).height() + 300 > $('footer').position().top) {
            if(!$scope.fetching) {
                $scope.fetching = true;
                $scope.get_next_blog();
            }
        }
    });
});
