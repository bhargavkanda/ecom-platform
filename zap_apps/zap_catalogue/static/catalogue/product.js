zapyle.directive('imageonload', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            element.bind('load', function() {
                // alert('image is loaded');
                $('.is_transparent').removeClass('is_transparent')
                $('.zoomimage').removeClass('is_visible')
            });
        }
    };
});

zapyle.controller('ProductController', function($scope, $http, $localStorage, $filter, $rootScope, admireService, loveService) {
    $scope.isMobile = false;
    if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent)
        || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))) $scope.isMobile = true;
    function show_loader(id, value) {
        document.getElementById(id).style.display = value ? 'block' : 'none';
    }
    $scope.get_blogs = function(product_id) {
        $http.get('/zapblog/related/'+product_id)
        .success(function(response){
            if(response.status == 'success'){
                $scope.blogs = response.data.blogs;
                $scope.look_thumbs = response.data.looks;
            }
        });
    }

    $http.get("/catalogue/singleproduct/"+window.location.pathname.split('/')[2]).
    success(function(data) {
        if(data.status == 'success'){
            $scope.product = data.data;
            setTimeout(function() {
                $('.thumbnail').first().click()
                $('.more_details .custom_tabs li').first().click()
            })
            $scope.product_title = $('.product_title').text()
            clevertap.event.push("Product Viewed", {
                "Product name":$scope.product.title,
                "Product id":$scope.product.id,
                "Category":$scope.product.product_category.name,
                "Price":$scope.product.listing_price,
            });
            // var seconds = $scope.product.flash_sale_data.end_time
            if ($scope.product['available_size'].length>0) {
                getOffers(window.location.pathname.split('/')[2]);
            }
            $http.get('/catalogue/sim/1?perpage=5&cat='+data.data['sub_cat']+'&plt=10&pht=10&pr='+data.data['listing_price']).success(function(rs){
                var b = []
                if(rs.status == 'success'){
                    var a = rs.data.data
                    for(i in a){if(a[i]['id']!=window.location.pathname.split('/')[2]){b.push(a[i])}}
                    // alert(JSON.stringify(data.data))
                    $scope.relatedProducts =  b;
                }
            });
            $scope.get_blogs(window.location.pathname.split('/')[2]);
            $rootScope.overlay('product');
        }
    });
    $scope.get_looks = function(product, look) {
        $('.product_looks').removeClass('show');
        $http.get('/catalogue/looks_for_product/'+ product.id).
            success(function(data, status, headers, config) {
            if (data.status == "success"){
                $scope.looks = data.data;
                setTimeout(function() {
                    $('.product_looks').addClass('show');
                    $('select').material_select();
                    $('#product_looks .looks .look_item:first-child').addClass('selected');
                    $('.looks .highlighter').css({'width': $('#product_looks .look_item.selected').width()});
                });
            } else {
                Materialize.toast(data.detail, 3000);
            }
        }).error(function(response) {
           Materialize.toast(response.detail, 3000);
        });
    }
    function getOffers(product_id) {
        $http.get('/catalogue/offers/'+product_id).success(function(response){
            if(response.status == 'success'){
                $scope.offers = response.data;
            }
        });
    }
    $scope.applyOffer = function(offer_id){
        var product_id = window.location.pathname.split('/')[2];
        var data = {'products':[product_id]}
        $http.post('/offer/apply/'+offer_id, data).
            success(function(rs, status, headers, config) {
                if (rs.status == "success"){
                    offer = rs.data[product_id]
                    if(offer.applied) {
                        $scope.appliedOffer = offer_id;
                        $scope.offerPrice = offer.offer_price;
                        var comma_separator_number_step = $.animateNumber.numberStepFactories.separator(',')
                        $('.product_page.product_details .price .new').prop('number', parseInt($('.product_page.product_details .price .new').text().replace(',', '')))
                          .animateNumber(
                            {
                              number: $scope.offerPrice,
                              numberStep: comma_separator_number_step
                            },
                            500
                          );
//                      $scope.product.listing_price = $scope.offerPrice
                    } else {
                        $('.offer input#'+offer_id).prop('checked', false);
                        Materialize.toast(offer.error, 3000);
                    }
                } else{
                    $('.offer input#'+offer_id).prop('checked', false);
                    Materialize.toast(rs.detail, 3000);
                }
        });
    }
    var seconds;
    function startTimer() {
        seconds = $scope.product.flash_sale_data.end_time
        timer();
    }
    function timer() {
        var days        = parseInt(seconds/86400);
        var hours       = parseInt((seconds%86400)/3600);
        var minutes     = parseInt((seconds%3600)/60);
        var remainingSeconds = seconds % 60;
        if (remainingSeconds < 10) {
            remainingSeconds = "0" + remainingSeconds;
        }
        if(document.getElementById('countdown')!== null) {
            document.getElementById('countdown').innerHTML = days + ":" + hours + ":" + minutes + ":" + remainingSeconds;
            if (seconds == 0) {
                document.getElementById('countdown').innerHTML = "";
            } else {
                seconds--;
                setTimeout(function() {
                    timer();
                }, 1000);
            }
        }
    }

    $http.get("/catalogue/get_comments?web=true&product_id="+window.location.pathname.split('/')[2]).success(function(data) {
        if(data.status == 'success'){
            if($localStorage.showcomment){
                $('.engagement_block').addClass('is_visible show_comments');
                $('body').scrollTo($('.comments_block'), 500, {offset: {top:-100}});
                $localStorage.showcomment = false
            }
            $scope.comments = data.data;
            setTimeout(function(){
                ['.compose_comment .comment_text'].forEach(function (selector) {
                    var element = document.querySelector(selector);
                    var rect = document.getElementById('mention_suggestions');
                    element.onkeyup = function(ev){ //for backspace detection
                        var key = ev.keyCode || ev.which;
                        if(key  == 8 && mentioning == 1){
                            parent = getFirstRange().startContainer
                            var q1 = $('.mention.current').text()
                            var q2 = q1.replace('@', '')
                            console.log($scope.users)
                            if (q2 == '') {
                                if(q1 == '@'){
                                    $scope.users = []
                                    $scope.$apply()
                                }else{
                                    $('.compose_comment').removeClass('mentioning');
                                    mentioning = 0;
                                }
                            }else{
                                $scope.searchUser(q2)

                            }


                        }
                    }
                    element.onkeypress = function(ev){
                        flag = 0;
                        ev = ev || window.event;
                        parent = getFirstRange().startContainer
                        var key = ev.keyCode || ev.which;
                        if (!$(parent).hasClass('mention')) {
                            parent = getFirstRange().startContainer.parentElement;
                        }
                        if (key == 64) { // if key is @
                            mentioning = 1;
                            el = insertHtmlAtCursor();
                            update(el);
                            ev.preventDefault();
                            mentionText = [];
                        } else if (mentioning == 1 && String.fromCharCode(key) == ' ') {
                            var q1 = $('.mention.current').text().replace('@', '')+String.fromCharCode(key)
                            for (i in $scope.users){
                                console.log($scope.users[i].zap_username)
                                if($scope.users[i].zap_username === q1.replace(/\s+/g, '')){//query.replace(/\s+/g, '')){
                                    $('.mention').addClass('valid')
                                    break;
                                }
                            }
                            mentioning = 0;
                            takeCursorOut(element);
                            $('.compose_comment').removeClass('mentioning');
                            ev.preventDefault();
                            flag = 1;
                            query = ''
                        } else if (mentioning == 1 && key != 64) {
                            var q1 = $('.mention.current').text().replace('@', '')
                            $scope.searchUser(q1+String.fromCharCode(key))
                            if ($(parent).html() == '@') {
                                // $scope.searchUser(String.fromCharCode(key))
                                $('.compose_comment').addClass('mentioning');
                            }
                        } else if (key == 8 || key == 46) { //space or dot
                            if ($(parent).html() == '@' || $(parent).html() == '') {
                                $('.compose_comment').removeClass('mentioning');
                                mentioning = 0;
                            }
                        }

                        if ($(parent).hasClass('mention') && !($(parent).hasClass('current')) && mentioning == 0 && flag==0) {

                            $(parent).addClass('current');
                            mentioning = 1;
                            update(parent);

                            // alert('thanx'+key+''+$('.mention.current').text())
                            $('.compose_comment').addClass('mentioning');
                        }
                    }
                })
            })
        }
    })
    $scope.gotoToCart = function(){
        $scope.cart()
        $('.goto_btn').addClass('is_hidden');
        $('.cart_btn').removeClass('is_hidden')
        $('.right_panel_inner > div').removeClass('is_visible');
        $($('.goto_btn').attr('data-activates')).addClass('is_visible');
        $('.right_panel').addClass('is_visible');
        window.history.pushState('', '', window.location.href+'/#rp_cart')
    }
//    $scope.addToCart = function(){
//        if(!$('.size_item.selected').length){
//            Materialize.toast('Please select a Size.', 3000);
//            return false;
//        }
//        $('.mobile_only #best_price_challenge').removeClass('is_visible');
//        $('.get_size_quantity').addClass('is_visible');
//        $('body').scrollToAnimate($('.buy_cta').siblings('.get_size_quantity').find('.inner').height()+40, 1000);
//        var available_size = $scope.product['available_size'].length
//        // $('.confirm_btn').removeClass('is_hidden')
//        // $('.cart_btn').addClass('is_hidden')
//        // $('.goto_btn').removeClass('is_hidden');
//        // $('.get_quantity').addClass('is_hidden')
//        if(available_size==1){
//            // alert($scope.product['available_size'][0]['quantity'])
//            $("[data-id="+$scope.product['available_size'][0]['size_id']+"]").addClass('selected')
//            $scope.availble_qty = $scope.product['available_size'][0]['quantity']
//            if($scope.availble_qty>1){$('.get_quantity').removeClass('is_hidden')}
//        }
//        var size = $('.size_item.selected').data('id')
//        var product_id = $('.product_id').data('id')
//        if(ZL == 'True' && USER_NAME!='None') {
//            var data = {'cart_data':{'quantity':$scope.qty,'product':product_id,'size':size}}
//            if ($scope.appliedOffer) {
//                data['cart_data']['offer'] = $scope.appliedOffer;
//            }
//            $http.post('/zapcart/?web=true',data).
//                success(function(rs, status, headers, config) {
//                // alert(JSON.stringify(rs))
//                if (rs.status == "success"){
//                    // $('.get_size_quantity').removeClass('is_visible')
//                    $('.cart_btn').addClass('is_hidden')
//                    $('.goto_btn').removeClass('is_hidden')
//                    // $('.confirm_btn').addClass('is_hidden')
//                    Materialize.toast(rs.data.message, 3000);
//                    $('#toteBadge').text(rs.data.count)
//                    clevertap.event.push("add_to_tote", {
//                        "user_id":USER_ID,
//                        "product_id":product_id,
//                        "size":$('.size_item.selected').text(),
//                        "quantity":$scope.qty,
//                        "price":$('.z_new').text().replace(',',''),
//                    });
//                }else{
//                    Materialize.toast(rs.detail, 3000);
//                }
//            })
//        } else {
//            var count = parseInt($('#toteBadge').text())
//            if($localStorage.tote){
//                var cart_data = $localStorage.tote['cart_data']
//                for(i in cart_data){
//                    if(cart_data[i]['product'] == product_id && cart_data[i]['size'] == size){
//                        $('.cart_btn').addClass('is_hidden')
//                        $('.goto_btn').removeClass('is_hidden')
//                        Materialize.toast("This item is already added in your tote.", 3000);
//                        return false;
//                    }
//                }
//            }else{
//                $localStorage.tote = {'cart_data' : []}
//            }
//            $localStorage.tote['cart_data'].push({
//                'product_quantity':$scope.qty,'product':product_id,
//                'quantity_available':$scope.availble_qty,
//                'size':size,
//                'product_image': $('.thumbnails li:first-child').children().attr('src'),
//                'original_price' :$scope.product.original_price,
//                'listing_price' : $('.z_new').text().replace(',',''),
//                'product_brand' : $('.z_brand').text(),
//                'title' : $('h1.product_title').text() ,
//                'product_size' : $('.size_item.selected').first().text(),
//                'offer': $scope.appliedOffer,
//                'offer_benefit': $scope.product.listing_price - $scope.offerPrice,
//                'id' : Math.floor((Math.random() * 100) + 1)
//            })
//            $('.get_size_quantity').removeClass('is_visible')
//            $('.cart_btn').addClass('is_hidden')
//            $('.goto_btn').removeClass('is_hidden')
//            Materialize.toast("Item added successfully.", 3000);
//            $('#toteBadge').text(++count)
//    	}
//    }
    $('.thumbnail').click(function(){
        $('.thumbnails .selected').removeClass('selected')
        $(this).children('img').addClass('selected')
        $('.is_transparent').addClass('is_transparent')
        $('.zoomimage').addClass('is_visible')
        $('.current_image').children("img:first-child").attr("src", $(this).children("img").attr("src").replace('100x100','1000x1000'));
        $('.current_image').children("img:last-child").attr("src", $(this).children("img").attr("src").replace('.100x100',''));
    });
    $('.size_item').click(function(){
        if(!$(this).hasClass('soldout')){
            $('.size_item').removeClass('selected')
            $(this).addClass('selected')
            $('.max_quantity').addClass('is_hidden')
            $('.goto_btn').addClass('is_hidden')
            $('.cart_btn').removeClass('is_hidden')
            $scope.availble_qty = $(this).data('qty')
            $scope.qty =  1
            $scope.$apply()
            if($scope.availble_qty>1){
                $('.get_quantity').removeClass('is_hidden')
            }else{$('.get_quantity').addClass('is_hidden')}
            $('.size_info').text($(this).data('tooltip'))
        }
    })
    $('.plus').click(function(){
        if($scope.availble_qty>$scope.qty){
            $scope.qty=$scope.qty+1
            $scope.$apply()
        }else{
            $('.max_quantity').removeClass('is_hidden') 
        }
    })
    $('.minus').click(function(){
        if($scope.qty>1){
            $scope.qty=$scope.qty-1
            $scope.$apply()
        }
    })
    $scope.like = function(user){
        console.log(user)
        if(ZL == 'True' && USER_NAME!='None'){
            if(user.length){
                $scope.product.likes.me = []
                loveService.postlove($('.product_id').data('id'),'unlike');
                $('.love').removeClass('loved')
            }else{
                $scope.product.likes.me = [{'id':USER_ID, 'zap_username':USER_NAME}]
                loveService.postlove($('.product_id').data('id'),'like');
                $('.love').addClass('loved')
            }      
        }else{
            $scope.$emit('setLoginPurpose', 'love a product' );
            $('.right_panel_inner > div').removeClass('is_visible');
            $($('.login_label').attr('data-activates')).addClass('is_visible');
            $('.right_panel').addClass('is_visible');
        }
    }
    $scope.profile_pic = $localStorage.profile_picture
    var mentioning = 0; var mentionText = [];
    var query = '';

    // document.addEventListener('touchmove', function (e) { e.preventDefault(); }, false);
    if($('.size_item:not(.soldout)').length == 1){
        var element = $('.size_item:not(.soldout)').first()
        element.addClass('selected')
        $('.size_item').removeClass('selected')
        $(element).addClass('selected')
        $('.max_quantity').addClass('is_hidden')
        $scope.availble_qty = $(element).data('qty')
        $scope.qty =  1
        // $scope.$apply()
        if($scope.availble_qty>1){
            $('.get_quantity').removeClass('is_hidden')
        }else{$('.get_quantity').addClass('is_hidden')}
        $('.size_info').text(element.data('tooltip'))
    }
    
    $('body').on('click', '.suggestion_item', function() {
        var span = $('.mention.current')
        span.addClass('valid')
        takeCursorOut(document.querySelector('.compose_comment .comment_text'));
        $('.mention.current').removeClass('current')
        span.html('@'+$(this).children('.closet_handle').text())
        
        $('.compose_comment').removeClass('mentioning');
        mentioning = 0;
        // $('.comment_text').focus();
        
    })
    $scope.loggedUser = USER_ID
    $('.new_comment').click(function(){
        if($(this).text() == 'Write your comment here'){
            $(this).text('')
        }
    })
    $scope.searchUser = function(key){
        if(key){    
            $http.get("/catalogue/user/search/"+key)
            .success(function(data) {
                if(data.status == 'success'){
                    $scope.users = data.data;
                }
            })
        }
    }
    $scope.postComment = function(){
        var comment = $('.new_comment').text()
        if(comment && comment !='Write your comment here'){
            $http.post('/catalogue/comment/',{
                'product': window.location.pathname.split('/')[2],
                'comment': $('.new_comment').text(),
                'web' : true
            })
            .success(function(data){
                if(data.status == 'success'){
                    var new_comment = data.data
                    new_comment['commented_by']={'id':USER_ID,'profile_pic': new_comment.profile_pic,'zap_username':new_comment.zap_username}
                    $scope.comments.push(new_comment)
                    $('.new_comment').text('')
                    clevertap.event.push("comment_on_product", {
                        "user_id":USER_ID,
                        "product_id":window.location.pathname.split('/')[2],
                    });
                }
            })
        }else{
            $('.new_comment').text('')
            $('.new_comment').focus()
        }
    }
    $scope.admire = function(u,status){
        if(ZL == 'True' && USER_NAME!='None'){
            status.admire_or_not=!status.admire_or_not
            if (status.admire_or_not){
                admireService.postadmire(u,'admire');
            }
            else{
                admireService.postadmire(u,'unadmire');
            }
        }else{
            $scope.$emit('setLoginPurpose', 'admire a user' );
            $('.right_panel_inner > div').removeClass('is_visible');
            $($('.login_label').attr('data-activates')).addClass('is_visible');
            $('.right_panel').addClass('is_visible');
        }
    }
    $('#current_image').zoom({ 
        touch:true, 
        on:'click',
        onZoomIn: function(){
          $(this).closest('#current_image').addClass('zooming');
        },
        onZoomOut: function(){
          $(this).closest('#current_image').removeClass('zooming');
        }
    });
    $('body').on('click', '.mobile_zoom', function() {
        $('div.pinch-zoom').each(function () {
            new RTP.PinchZoom($(this), {});
        });
    });
    $('.counts .comments').click(function(){
        $('.engagement_block').removeClass('show_loves expand');
        $('.engagement_block').addClass('is_visible show_comments');
        setTimeout(function(){
            $('.engagement_block').addClass('expand');
        })
    });
    $('.counts .loves').click(function(){
        $http.get('/catalogue/get_likes/?web=true&product_id='+$('.product_id').data('id')).
        success(function(rs){
            if(rs.status == 'success'){
                $scope.loves = rs.data
            }
        })
        $('.engagement_block').removeClass('show_comments expand');
        $('.engagement_block').addClass('is_visible show_loves');
        setTimeout(function(){
            $('.engagement_block').addClass('expand');
        })
    });
    $('.comment').click(function(){
        if(ZL == 'True' && USER_NAME!='None'){
            $('.engagement_block').removeClass('show_loves expand');
            $('.engagement_block').addClass('is_visible show_comments');
            setTimeout(function(){
                $('.engagement_block').addClass('expand');
            }) 
            $('.new_comment').text('')
            $('.new_comment').focus()
            $('body').scrollToAnimate($('.new_comment'), 500, {offset: {top:-100}});
        }else{
            $scope.$emit('setLoginPurpose', 'comment on a product' );
            $('.right_panel_inner > div').removeClass('is_visible');
            $($('.login_label').attr('data-activates')).addClass('is_visible');
            $('.right_panel').addClass('is_visible');
        }
    })    
    $scope.loginToComment = function(){
        $('.right_panel_inner > div').removeClass('is_visible');
        $($('.login_label').attr('data-activates')).addClass('is_visible');
        $('.right_panel').addClass('is_visible');
        $localStorage.showcomment = true
    }
    $scope.addToCart = function(product=null, size=null, quantity=null){
        if (product == null) {
            product_id = $('.product_id').data('id');
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
            var available_size = $scope.product.available_size.length
            if(available_size==1){
                $("[data-id="+$scope.product.available_size[0]['id']+"]").addClass('selected')
                $scope.availble_qty = $scope.product.available_size[0]['quantity']
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
                    // $('.get_size_quantity').removeClass('is_visible')
//                    $('.cart_btn').addClass('is_hidden')
//                    $('.goto_btn').removeClass('is_hidden')
                    // $('.confirm_btn').addClass('is_hidden')
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
                        Materialize.toast($scope.product.title + " is already added in your tote.", 3000);
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
            Materialize.toast($scope.product.title + " added successfully.", 3000);
            $('#toteBadge').text(++count)
    	}
    }
    $scope.addToCart_bulk = function() {
        items = $('.product_item.selected');
        if (items.length == 0) {
            Materialize.toast('Select products to add to Cart', 3000);
            return false;
        } else {
            items.each(function() {
                if ($(this).find('.sizes select option:selected').length==0 || $(this).find('.sizes select option:selected').val()=='') {
                    Materialize.toast('Select sizes for the products you add to Tote.', 3000);
                    return false;
                } else {
                    product_id = $(this).data('id');
                    product = $filter('filter')($scope.looks.look_data.products, { id: product_id  }, true)[0];
                    size = $(this).find('.sizes select option:selected').val();
                    $scope.addToCart(product, size, 1);
                }
            });
        }
    }
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
    $scope.get_look = function(blog, event) {
        if (!$(event.currentTarget).hasClass('selected')) {
            $('.looks .look_item').removeClass('selected');
            $(event.currentTarget).addClass('selected');
            $('.looks .highlighter').css({'left': $(event.currentTarget).offset().left - $(event.currentTarget).parent().offset().left, 'width': $(event.currentTarget).width()});
            $http.get('/zapblog/post/'+ blog.id).
                success(function(data, status, headers, config) {
                if (data.status == "success"){
                    $scope.looks.look_data = data.data;
                    setTimeout(function() {
                        $('select').material_select();
                    });
                } else {
                    Materialize.toast(data.detail, 3000);
                }
            }).error(function(response) {
               Materialize.toast(response.detail, 3000);
            });
        }
    }
})

zapyle.directive('checkImage', function($http) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            attrs.$observe('ngSrc', function(ngSrc) {
                $http.get(ngSrc).success(function(){
                    // alert('image exist');
                }).error(function(){
                    // alert('image not exist');
                    element.attr('src', attrs.imgsrc.replace('.100x100',''));
                });
            });
        }
    };
});