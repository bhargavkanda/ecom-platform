var zapyleAdmin = angular.module('zapyleAdmin', [
        //'ngAnimate',
        'ngCookies',
        'ngResource',
        'ngRoute',
        'ngTouch',
        'satellizer',
        'ngStorage',
        'ngMessages',
        'angular-img-cropper'
    ]);
    zapyleAdmin.config(function($routeProvider, $httpProvider, $interpolateProvider) {
        $interpolateProvider.startSymbol('[[').endSymbol(']]');
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        $httpProvider.defaults.headers.common["X-Requested-With"] = 'XMLHttpRequest';
    });
    zapyleAdmin.directive('stringToNumber', function() {
      return {
        require: 'ngModel',
        link: function(scope, element, attrs, ngModel) {
          ngModel.$parsers.push(function(value) {
            return '' + value;
          });
          ngModel.$formatters.push(function(value) {
            return parseFloat(value, 10);
          });
        }
      }
    })
    zapyleAdmin.controller('UserCtrl', function($scope,$http,$location, $localStorage) {
        var typingTimer; 
        var doneTypingInterval = 1000;
        var $input = $('#searchBox');
        $input.on('keyup', function () {
          clearTimeout(typingTimer);
          typingTimer = setTimeout(doneTyping, doneTypingInterval);
        });
        $input.on('keydown', function () {
          clearTimeout(typingTimer);
        });
        function doneTyping() {
            $('#searchBox').addClass('listing_spinner')
            $scope.get_userDetails($scope.search_product)
        }
    });
    zapyleAdmin.controller('ListingCtrl', function($scope,$http,$location, $localStorage) {
        $scope.get_productsToApprove(1)

        var typingTimer; 
        var doneTypingInterval = 700;
        var $input_listing = $('#listing_search');
        $input_listing.on('keyup', function () {
          clearTimeout(typingTimer);
          typingTimer = setTimeout(doneTyping1, doneTypingInterval);
        });
        $input_listing.on('keydown', function () {
          clearTimeout(typingTimer);
        });
        function doneTyping1() {
            $('#listing_search').addClass('listing_spinner')
            $localStorage.firstPageClick = true;
            if($scope.page=='catalogue'){
                $scope.get_productsToApprove(1)
            }else if($scope.page == 'approved'){
                $scope.get_ApprovedProducts()
            }else{
                $scope.get_disapprovedProducts(1)
            }
        }

    });
    
    zapyleAdmin.controller('AdminCtrl', function($scope,$http,$location, $localStorage) {
        $(".chosen-select").chosen()
        $('.chosen-container').css({'margin-top': '-30px', 'margin-left': '100px'})     
        $(".chosen-select").ajaxChosen({
            dataType: 'json',
            type: 'POST',
            url:'/search',
            data: {'keyboard':'cat'}, //Or can be [{'name':'keyboard', 'value':'cat'}]. chose your favorite, it handles both.
            success: function(data, textStatus, jqXHR){ 
                //$(".chosen-select").chosen()
                //alert(JSON.stringify(data))    
            }
            },{
            processItems: function(data){
                return data.results; 
            },
            useAjax: function(e){ return true},//someCheckboxIsChecked(); },
            generateUrl: function(q){ return '/zapadmin/user/search/'+q },
            loadingImg: 'https://raw.githubusercontent.com/ksykulev/chosen-ajax-addition/master/example/loading.gif',
            minLength: 3
        });
        $(".chosen-select").on('change', function(event, params) {
            $scope.change_user(params.selected)
        });

    $scope.page_title = 'Products to be approved'
    $scope.page = 'catalogue'
    $scope.template ='/zapstatic/frontend/admin_styles/templates/catalogue.html?_=ss'+ZAP_ENV_VERSION
    


    $scope.get_upload_details = function(){
        $http({
            method: 'GET',
            url: "/zapadmin/get_upload_details/",
        }).then(function successCallback(response) {
            var data = response.data.data
            $scope.cat = data['category']
            $scope.sub_cat = data['sub_category']
            $scope.sub_categories_temp = data['sub_category']
            $scope.colors = data['color']
            $scope.occasions = data['occasion']
            $scope.styles = data['fashion_types']
            $scope.states = data['states']
            $scope.brands = data['brands']
            $scope.filtered_brands = $scope.brands
            $scope.categories = data['category']
            $scope.sub_categories = data['sub_category']
            $scope.size_list = data.global_product_list
            var zap_exc_user = data.zap_exc_user
            $(".chosen-select").append($('<option></option>')
                .val(zap_exc_user.id)
                .attr('selected', 'selected')
                .html(zap_exc_user.email)).trigger("chosen:updated");
            $scope.change_user(zap_exc_user.id)
        }, function errorCallback(response) {
            // console.log(response.data.category);
        });        
    }
    $scope.get_productsToApprove = function(page){
        if(!$('#listing_search').val()){document.getElementById('loading').style.display = 'block';}
        $('.order_nav_bar').hide();
        $('.logistics_nav_bar').hide();
        $('.analytics_nav_bar').hide();
        $http({
                method: 'GET',
                url: '/zapadmin/get_productsToApprove/'+page+'/?search_word='+$('#listing_search').val(),
            }).then(function successCallback(response) {
                document.getElementById('loading').style.display = 'none';
                // console.log(response)
                $scope.productsToApprove = response.data.data
                $scope.total_pages = response.data.total_pages
                $scope.show_pagination()
            });        
    }
    $scope.get_disapprovedProducts = function(page){
        if(!$('#listing_search').val()){document.getElementById('loading').style.display = 'block';}
        $http({
                method: 'GET',
                url: '/zapadmin/get_disapprovedProducts/'+page+'/?search_word='+$('#listing_search').val(),
            }).then(function successCallback(response) {
                document.getElementById('loading').style.display = 'none';
                // console.log(response)
                $scope.productsToApprove = response.data.data
                $scope.total_pages = response.data.total_pages
                $scope.show_pagination()
            });
    }
    function show_user_pagination(){
        $('#searchBox').removeClass('listing_spinner')
        $('#paginationuser').html('');
        $('#paginationuser').html('<ul id="pagination-user" class="pagination-sm"></ul>');
        $('#pagination-user').twbsPagination({
            totalPages: $scope.total_pages,
            visiblePages: 10,
            onPageClick: function (event, page) {
                if($localStorage.firstPageClick) {
                   $localStorage.firstPageClick = false;
                   return;
                }
                $http({
                    method: 'GET',
                    url: '/zapadmin/get_userDetais/?page='+page+'&search_word='+$scope.search_product,
                }).then(function successCallback(response) {
                    console.log(response)
                    $scope.users = response.data.data
                    $scope.total_pages = response.data.total_pages
                    //show_user_pagination(response.data.total_pages)
                });
            }
        });
    }
    $scope.get_userDetails = function(string){
        $scope.search_product = string
        $http({
                method: 'GET',
                url: '/zapadmin/get_userDetais/?search_word='+string,
            }).then(function successCallback(response) {
                console.log(response)
                $scope.users = response.data.data
                $scope.total_pages = response.data.total_pages
                show_user_pagination()
            });
    }
    $scope.get_order_details = function(){
        $http({
                method: 'GET',
                url: '/zapadmin/orders/',
            }).then(function successCallback(response) {
                // console.log(response)
                $scope.orders = response.data.data.data
                 $scope.total_pages_order = response.data.data.total_pages
                $scope.show_order_pagination();
                $scope.load_pickup_addresses()
            });
    }
    $scope.get_logistics_evaluation = function(){
        $http({
                method: 'GET',
                url: '/zapadmin/logistics_evaluation/',
            }).then(function successCallback(response) {
                console.log(response)
                $scope.logistics = response.data.data.log_data
                $scope.logistics_partners = response.data.data.logistics_partners
            });
    }
    // $scope.get_logistics_rejections = function(){
    //     $http({
    //             method: 'GET',
    //             url: '/zapadmin/logistics_rejection/',
    //         }).then(function successCallback(response) {
    //             console.log(response)
    //             //alert(JSON.stringify(response))
    //             $scope.logistics_reject_data = response.data.data
    //             //$scope.logistics_partners = response.data.data.logistics_partners
    //         });
    // }
    $scope.get_Notifyuser = function(){
        $http({
                method: 'GET',
                url: '/zapadmin/get_notifyUsers/',
            }).then(function successCallback(response) {
                console.log(response)
                $scope.zapusers = response.data.users
                $scope.push_not_users = response.data.push_not_users
                $scope.marketing_actions = response.data.marketing_actions
            });
    }
    $scope.get_products_returned = function(){
         $http({
                method: 'GET',
                url: '/zapadmin/returns/',
            }).then(function successCallback(response) {
                  console.log(response.data.data)
                  $scope.returnDatas = response.data.data
                  // console.log(JSON.stringify(response)+'get_Notifyuser')
                  // $scope.zapusers = response.data.users
                  // $scope.push_not_users = response.data.push_not_users
                  // $scope.marketing_actions = response.data.marketing_actions
                  // $scope.actions = response.data.actions
            });
    }
    
    $scope.setMarketingChosen = function(type){
        // alert(type)
        $('.chosen-'+type).chosen({ width:"80%" });
        if(type == 'profile'){
            $('.chosen-profile').ajaxChosen({
                dataType: 'json',
                type: 'POST',
                url:'/search',
                data: {'keyboard':'cat'}, //Or can be [{'name':'keyboard', 'value':'cat'}]. chose your favorite, it handles both.
                success: function(data, textStatus, jqXHR){ 
                    //$(".chosen-select").chosen()
                    //alert(JSON.stringify(data))    
                }
                },{
                processItems: function(data){
                    return data.results; 
                },
                useAjax: function(e){ return true},//someCheckboxIsChecked(); },
                generateUrl: function(q){ return '/zapadmin/user/search/'+q },
                loadingImg: 'https://raw.githubusercontent.com/ksykulev/chosen-ajax-addition/master/example/loading.gif',
                minLength: 3
            });
        }
        if(type == 'product'){
        $('.chosen-product').ajaxChosen({
            dataType: 'json',
            type: 'POST',
            url:'/search',
            data: {'keyboard':'cat'}, //Or can be [{'name':'keyboard', 'value':'cat'}]. chose your favorite, it handles both.
            success: function(data, textStatus, jqXHR){ 
                //$(".chosen-select").chosen()
                //alert(JSON.stringify(data))    
            }
            },{
            processItems: function(data){
                return data.results; 
            },
            useAjax: function(e){ return true},//someCheckboxIsChecked(); },
            generateUrl: function(q){ return '/zapadmin/product/search/'+q },
            loadingImg: 'https://raw.githubusercontent.com/ksykulev/chosen-ajax-addition/master/example/loading.gif',
            minLength: 3
        });
        }
        if(type == 'filtered'){
            $http.get('/filters/f_o').
                success(function(data, status, headers, config) {
                if (data.status == "success"){
                    $scope.campaign = data.data.campaign
                    $scope.collection = data.data.collection
                    $scope.size = data.data.size.value[0].value
                    $scope.price = data.data
                    $scope.product_category = data.data.category.value
                    $scope.brand = data.data.brand.value
                    $scope.age = data.data.age.value
                    $scope.condition = data.data.condition.value
                    $scope.style = data.data.style.value
                    $scope.color = data.data.color.value
                    $scope.occasion = data.data.occasion.value
                    $scope.disc = data.data.disc.value

                }
            })
        }
        $('.chosen-container-single-nosearch').removeClass('chosen-container-single-nosearch')
        $('.chosen-search').find("input:text").attr("readonly", false)
       $('.chosen-results').css({"width": "100%"})
    }
    // $scope.get_upload_details()
    
    
    $scope.get_ApprovedProducts = function(){
        // $('#paginationholder').html('');
        // $('#paginationholder').html('<ul id="pagination-demo" class="pagination-sm"></ul>');
        if(!$('#listing_search').val()){document.getElementById('loading').style.display = 'block';}
        //document.getElementById('loading').style.display = 'block';
        $http({
                method: 'GET',
                url: '/zapadmin/get_approvedProducts/1/?search_word='+$('#listing_search').val(),
            }).then(function successCallback(response) {
                // console.log(response)
                $scope.productsToApprove = response.data.data
                $scope.total_pages = response.data.total_pages
                $scope.show_pagination()
                document.getElementById('loading').style.display = 'none';
            });        
    }
    $scope.showProduct = function(id){
        $http({
                method: 'GET',
                url: '/zapadmin/product/'+id+'/',
            }).then(function successCallback(response) {

                $scope.productDetail = response.data
            });
    }
    $scope.popup_flag1=false
    var approve_ready = true
    $scope.approve = function(product){
        if(approve_ready == false){
            return false
        }
        approve_ready = false
        console.log(product)
        $("#approve_button_"+product.id).text('PLEASE WAIT')
        $("#approve_button_"+product.id).prop('disabled', true)
        $("#disaprv_button_"+product.id).prop('disabled', true)
        $http({
                method: 'POST',
                url: '/zapadmin/approve/',
                data:{
                    product : product.id,
                    page:$scope.page
                }
            }).then(function successCallback(response) {
                approve_ready = true
                if(response.data.status == "success"){
                    for(var i=0;i<$scope.productsToApprove.length;i++){
                        if($scope.productsToApprove[i]['id']==product.id){
                            swal("successfully approved")
                            $scope.productsToApprove.splice(i,1)
                        }
                    }
                    if($scope.productsToApprove.length == 0){
                        if($scope.page == 'catalogue'){
                            $scope.get_productsToApprove(1)
                        }else{
                            $scope.get_disapprovedProducts(1)
                        }
                    }
                }else{

                }
                $("#approve_button_"+product.id).text('APPROVE')
                $("#approve_button_"+product.id).prop('disabled', false)
                $("#disaprv_button_"+product.id).prop('disabled', true)
            });
    }

    $scope.reject_product = function(id,reason,send_pushnot,index){
        if(!reason){
            alert("Select a reason for disapprove")
            return false
        }
        swal({
            title: 'Are you sure?',
            text: 'You can approve from disapproved tab!',
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, disapprove!',
            closeOnConfirm: false,
            showLoaderOnConfirm:true
        },
        function() {
            $http({
                method: 'POST',
                url: '/zapadmin/reject/'+id+'/?action='+$scope.page,
                data:{
                    'reason':reason,
                    'send_pushnot':send_pushnot
                }
            }).then(function successCallback(response) {
                if(response.data.status == "success"){
                    // for(var i=0;i<$scope.productsToApprove.length;i++){
                    //     if($scope.productsToApprove[i]['id']==id){
                    //         swal("Disapproved")
                    //         $scope.productsToApprove.splice(i,1)
                    //     }
                    // }
                    swal("Disapproved")
                    $scope.productsToApprove.splice(index,1)
                    $scope.popup_flag1=false
                    if($scope.productsToApprove.length == 0){
                        if($scope.page == 'catalogue'){
                            $scope.get_productsToApprove(1)
                        }else{
                            $scope.get_ApprovedProducts()
                        }
                    }
                    // if($scope.productDetail['id']==$scope.productToReject){
                    //     $scope.productDetail=null
                    // }
                }else{
                    console.log(response)
                    swal('Cancelled',JSON.stringify(response.data.detail),'error');
                }
            })           
        });
    }

    $scope.delete_product = function(id){
        swal({
            title: 'Are you sure?',
            text: 'You will not be able to recover this imaginary file!',
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!',
            closeOnConfirm: false,
            showLoaderOnConfirm:true
        },
        function() {
            if($scope.page=='approved'){
                var url = '/zapadmin/approve/'
            }else{
                var url = '/zapadmin/reject/'
            }
            $http({
                method: 'DELETE',
                url: url+id+'/',
            }).then(function successCallback(response) {
                if(response.data.status == "success"){
                    for(var i=0;i<$scope.productsToApprove.length;i++){
                        if($scope.productsToApprove[i]['id']==id){
                            swal("successfully Deleted")
                            $scope.productsToApprove.splice(i,1)
                        }
                    }
                    swal('Deleted!','Your file has been deleted.','success');
                    $scope.popup_flag1=false
                    if($scope.productsToApprove.length == 0){
                        if($scope.page == 'disapproved'){
                            $scope.get_disapprovedProducts(1)
                        }else{
                            $scope.get_ApprovedProducts()
                        }
                    }
                    // if($scope.productDetail['id']==$scope.productToReject){
                    //     $scope.productDetail=null
                    // }
                }else{
                    swal('Cancelled',JSON.stringify(response.data.detail),'error');
                }
            });
            
        });


        
    }
    
    $scope.age = [{'id':'0', 'name':'0-3 months'},
                        {'id':'1','name':'3-6 months'},
                        {'id':'2','name':'6-12 months'},
                        {'id':'3','name':'1-2 years'}];
    $scope.conditions=[{'id':'0','name':'New with tags'},
                        {'id':'1','name':'Mint Condition'},
                        {'id':'2','name':'Gently loved'},
                        {'id':'3','name':'Worn out'}];

    $scope.get_approved_products = function(){
        $scope.page = 'approved'
        $(".catalogue_nav_bar").children("li").removeClass("selected")
        $("#aprvd").addClass("selected")
        $scope.page_title = 'Approved Products'
        $('#listing_search').val('')
        $scope.get_ApprovedProducts()
    }
    $scope.search_key = ''
    // $scope.search_products = function(search_words){
    //     search_key = search_words
    //     firstPageClick = true;
    //     $scope.get_productsToApprove(1)
    // }
    $scope.get_products_to_approve = function(){
        $scope.page_title = 'Products to be approved'
        $scope.template ='/zapstatic/frontend/admin_styles/templates/catalogue.html?_=ss'+ZAP_ENV_VERSION
        $scope.page = 'catalogue'
        $('.order_nav_bar,.logistics_nav_bar,.analytics_nav_bar').hide();
        $('.catalogue_nav_bar').removeClass('is_hidden').show();
        $(".nav-bar,.catalogue_nav_bar").children("li").removeClass("selected")
        $("#dsaprvd,#catlg").addClass("selected")
        $('#listing_search').val('')
        $scope.get_productsToApprove(1)
    }
    // $scope.get_products_to_approve()
    $scope.get_disapproved_products = function(){
        $scope.template ='/zapstatic/frontend/admin_styles/templates/catalogue.html?_=ss'+ZAP_ENV_VERSION
        $scope.page = 'disapproved'
        $scope.page_title = 'Disapproved Products'
        $(".catalogue_nav_bar").children("li").removeClass("selected")
        $("#rejctd").addClass("selected")
        $('#listing_search').val('')
        $scope.get_disapprovedProducts(1)
        
    }
    $scope.get_user_details = function(){
        $scope.template ='/zapstatic/frontend/admin_styles/templates/user.html?_='+ZAP_ENV_VERSION
        $scope.page = 'user'
        $scope.page_title = 'Zapyle Users'
        $(".nav-bar").children("li").removeClass("selected")
        $("#usr").addClass("selected")
        $('.catalogue_nav_bar,.order_nav_bar,.analytics_nav_bar,.logistics_nav_bar').hide();
        $scope.get_userDetails()
    }
    $scope.get_orders = function(){
        $scope.template ='/zapstatic/frontend/admin_styles/templates/order.html?_=ssdfs'+ZAP_ENV_VERSION
        $scope.page = 'order'
        $scope.page_title = 'Products Orders'
        $('.logistics_nav_bar').hide();
        $('.catalogue_nav_bar').hide();
        $('.order_nav_bar').removeClass('is_hidden').show()
        $(".nav-bar").children("li").removeClass("selected")
        $(".order_nav_bar").children("li").removeClass("selected")
        $("#liorders").addClass("selected")
        $("#ordr").addClass("selected")
        $scope.get_order_details()
    }
    $scope.clevertap = true;
    $scope.marketing = function(){
        $scope.template ='/zapstatic/frontend/admin_styles/templates/marketing.html?_=sda'+ZAP_ENV_VERSION
        $scope.page = 'marketing'
        $scope.page_title = 'Zapyle Marketing'
        $('.catalogue_nav_bar,.order_nav_bar,.analytics_nav_bar').hide()
        $(".nav-bar").children("li").removeClass("selected")
        $("#marktg").addClass("selected")
        $scope.get_Notifyuser();
    }
    $scope.get_returns =function(){
        $scope.template ='/zapstatic/frontend/admin_styles/templates/return.html?_=asaa'+ZAP_ENV_VERSION
        $scope.page ='return'
        $scope.page_title = 'Products Returns'
        $(".order_nav_bar").children("li").removeClass("selected")
        $("#lireturns").addClass("selected")
        $scope.get_products_returned()
    }
    $scope.get_logistics = function(){
        $scope.template ='/zapstatic/frontend/admin_styles/templates/logistics.html'
        $scope.page = 'logistics'
        $('.order_nav_bar').hide();
        $('.catalogue_nav_bar,.analytics_nav_bar').hide();
        $('.logistics_nav_bar').removeClass('is_hidden').show();
                  //$(".nav-bar").children("li").removeClass("selected")
        $(".logistics_nav_bar,.nav-bar").children("li").removeClass("selected")
        $("#logistics,#lievaluation").addClass("selected")
        //$("#lievaluation").addClass("selected")
        $scope.page_title = 'Explore Logistics'
        $scope.get_logistics_evaluation()
    }
    // $scope.get_logistics_rejection = function(){
    //     $scope.page = 'rejection'
    //     $('.order_nav_bar').hide();
    //     $('.catalogue_nav_bar').hide();
    //     $('.analytics_nav_bar').hide();
    //     $('.logistics_nav_bar').show();
    //     $(".nav-bar").children("li").removeClass("selected")
    //     $(".logistics_nav_bar").children("li").removeClass("selected")
    //     $("#logistics").addClass("selected")
    //     $("#lirejection").addClass("selected")
    //     $('.logistics_nav_bar').show();
    //     $scope.page_title = 'Order Rejection'
    //     $scope.get_logistics_rejections()
    // }
    
    $scope.get_analytics_users = function(){
        $scope.template ='/zapstatic/frontend/admin_styles/templates/analytics_users.html'
        $scope.page = 'analytics_users'
        $('.order_nav_bar').hide();
        $('.catalogue_nav_bar').hide();
        $('.logistics_nav_bar').hide();
        $('.analytics_nav_bar').removeClass('is_hidden').show()
        $(".nav-bar").children("li").removeClass("selected")
        $(".analytics_nav_bar").children("li").removeClass("selected")
        $("#li_ana_user").addClass("selected")
        $("#analytics").addClass("selected")
        $scope.page_title = 'Users Analytics'
        $http({
            method: 'GET',
            url: '/zapadmin/get_users_details/',
        }).then(function successCallback(response) {
            console.log(response)
            $scope.ud = response.data.data
        });
    }
    $scope.get_analytics_products = function(){
        $scope.template ='/zapstatic/frontend/admin_styles/templates/analytics_products.html?_='+ZAP_ENV_VERSION
        $scope.page = 'analytics_products'
        $(".analytics_nav_bar").children("li").removeClass("selected")
        $("#li_ana_products").addClass("selected")
        $scope.page_title = 'Products Analytics'
        $http({
            method: 'GET',
            url: '/zapadmin/get_products_count/',
        }).then(function successCallback(response) {
            console.log(response)
            $scope.productsCount = response.data.data
        });

    }
    $scope.get_analytics_orders = function(){
        $scope.template ='/zapstatic/frontend/admin_styles/templates/analytics_orders.html?_=sdsa'
        $scope.page = 'analytics_orders'
        $(".analytics_nav_bar").children("li").removeClass("selected")
        $("#li_ana_orders").addClass("selected")
        $scope.page_title = 'Orders Analytics'
        $http({
            method: 'GET',
            url: '/zapadmin/get_order_details/',
        }).then(function successCallback(response) {
            console.log(response)
            $scope.order_dict = response.data.data
        });
    }
    
    $scope.load_filtered_products = function(p,q){
        $http({
            method: 'GET',
            url: '/zapadmin/get_products_count/?type='+p+'&cat='+q,
        }).then(function successCallback(response) {
            if(p == 'interaction'){
                $scope.table_flag2 = true
                $scope.interact = response.data.data
            }else{
                $scope.table_flag = true
                console.log(response.data.count)
                $scope.productCount = response.data.data
            }
        });
    }
    $scope.showBrandProducts = function(brand,type,segment,closeModal){
        if(closeModal){
            $('#show_brand_products').removeClass('is_visible')
            return false;
        }
        $('#show_brand_products').addClass('is_visible')
        $http.get('/zapadmin/get_brand_products/?brand='+brand+'&type='+type+'&segment='+segment).
        success(function(rs){
            if(rs.status == 'success'){
                $scope.brandProducts = rs.data
            }
        })
    }
    $scope.load_filtered_users = function(p,q){
        $http({
            method: 'GET',
            url: '/zapadmin/get_users_details/?type='+p,
        }).then(function successCallback(response) {
            if(q =='segmentation'){
                $scope.table_flag = true
                console.log(response.data.count)
                $scope.userCount = response.data.data
            }else{
                $scope.interaction = response.data.data
            }
        });
    }
    $scope.load_filtered_orders = function(p,q){
        $http({
            method: 'GET',
            url: '/zapadmin/get_order_details/?type='+p,
        }).then(function successCallback(response) {
                $scope.table_flag = true
                console.log(response.data.count)
                $scope.orderCount = response.data.data
        });
    }
    
    $scope.change_table_flag = function(str){
        if (str == 'segment'){
            $scope.table_flag = false
        }else{
            $scope.table_flag2 = false
        }
    }
    $scope.send_sms = function(sms){
        swal({
            title: '',
            text: 'Are you sure?',
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, Send!',
            closeOnConfirm: false,
            showLoaderOnConfirm:true
        },
        function() {
            $("#send_button").val("Please Wait...").attr('disabled', 'disabled');
            $http({
                method: 'POST',
                url: '/notification/send_sms/',
                data:{
                    'message':sms.text,
                    'users':sms.users,
                    'type':sms.type
                }
            }).then(function successCallback(response) {
                console.log(response)
                sms.text = ''
                sms.users = ''
                swal(JSON.stringify(response.data.status))
                $("#send_button").val("Send").prop('disabled', false);
            });
        })
    }

    $scope.send_email = function(email){
        var datetimepicker = $("#datetimepicker").data("kendoDateTimePicker");
        email.time = datetimepicker.value()
        swal({
            title: '',
            text: 'Are you sure?',
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, Send!',
            closeOnConfirm: false,
            showLoaderOnConfirm:true
        },
        function() {
            $("#email_button").val("Please Wait...").attr('disabled', 'disabled');
            $http({
                method: 'POST',
                url: '/notification/send_email/',
                data:{
                    data:email
                }
            }).then(function successCallback(response) {
                console.log(response)
                email.from = ''
                email.subject = ''
                email.template = ''
                email.message = ''
                email.users = ''
                email.raw_users = ''
                // swal(JSON.stringify(response.data.status))
                $("#email_button").val("Send").prop('disabled', false);
            });
        })
    }
    $scope.send_push_data = function(data, clevertap){
        if(!data.action_type){
            swal("Select Action Type.")
            return false;
        }
        $scope.json_data = ''
        var datepicker = $("#datetimepicker").data("kendoDateTimePicker");
        var client = new XMLHttpRequest();
        var file = document.getElementById("img2");
        var formData = new FormData();
        var filteredDict = {}
        if(data.action_type == 'filtered'){
            if($('.filled-in:checked').length || $('.campaign_option').is(':checked')){
                var name
                var id
                $(".filled-in:checked").map(function() {
                    id = $(this).data("ids")
                    name = $(this).data("name")
                    if(name in filteredDict){
                        filteredDict[name].push(id)
                    }else{
                        filteredDict[name] = [id]
                    }
                })
                if($('.campaign_option').is(':checked')) { filteredDict['campaign'] = [$('.campaign_option:checked').data('ids')]; }
                formData.append("data", JSON.stringify(filteredDict));
            }else{
                swal("Select filtered options")
                return false;
            }
        }else if (data.action_type == 'profile') {
            if(!$(".chosen-profile").val().split(',')[0]){swal('Select a profile.');return false;}
            formData.append("data", JSON.stringify({'id':$(".chosen-profile").val().split(',')[0]}));
        }else if(data.action_type == 'product'){
            if(!$(".chosen-product").val().split(',')[0]){swal('Select a product.');return false;}
            formData.append("data", JSON.stringify({'id':$(".chosen-product").val().split(',')[0]}));
        }else{

        }

        formData.append("image", file.files[0]);
        for ( var key in data ) {
            formData.append(key, data[key]);
        }
        formData.append("text", data.text)
        formData.append("time", $("#datetimepicker").val())//datepicker.value())
        $("#push_button").val("Please Wait...").attr('disabled', 'disabled');
        formData.append("clevertap", clevertap);
        swal({
            title: '',
            text: 'Are you sure?',
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, Send!',
            closeOnConfirm: false,
            showLoaderOnConfirm:true
        },
        function() {
            $http({
                method: 'POST',
                url: '/zapadmin/send_notification/',
                'data' : formData,
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            }).then(function successCallback(response) {
                $("#push_button").val("Send Push Notification").attr('disabled', false);
                // alert(JSON.stringify(response))
                if(response.data.status == 'success'){
                    swal("Success");
                    if(clevertap){
                        $scope.json_data = JSON.stringify(response.data.json_data);
                        $scope.branch_url = response.data.branch_url;
                        // swal("Copy and paste json in clevertap.");
                    }else{
                        $scope.push_data = {'text' : ''}
                    }
                }else{
                    swal(JSON.stringify(response.data.detail))
                }
            })
        })
    }
    $scope.approve_return = function(object){
        $http({
                method: 'POST',
                url: '/zapadmin/returns/',
                data:{
                    id:object.id
                }
            }).then(function successCallback(response) {
                if (response.data.status == 'success'){
                    object.approved = true;
                    // for(var i=0;i<$scope.returnDatas.length;i++){
                    //     if($scope.returnDatas[i]['id'] == id){
                    //         $scope.returnDatas.splice(i, 1)
                    //     }
                    // }
                }else{
                    swal('Something went wrong')
                }
                console.log(response)
                //swal(JSON.stringify(response))
            });
    }

    $scope.return_logistics = function(r, status){
        if(status == 'pickup'){
            $('#btn_pickup_return'+r.id).prop('disabled', true);
            $("#btn_pickup_return"+r.id).text('Please wait..');
        }else if(status == 'delivery'){
            $('#btn_delivery_return'+r.id).prop('disabled', true);
            $("#btn_delivery_return"+r.id).text('Please wait..');
        }else if(status == "approve"){
            $('#btn_approve_return'+r.id).attr('disabled', true)
            $('#btn_approve_return'+r.id).attr('value','Please wait..')
        }else{
            $('#btn_trigger_return'+r.id).attr('disabled', true)
            $('#btn_trigger_return'+r.id).attr('value','Please wait..')
        }

        $http.post("/zapadmin/return_trigger/",{'step': status, 'return_id':r.id}).
        success(function(res){
            if(res.status == "success"){
                if(status == 'pickup'){
                    r.return_status = 'pickup_in_process'
                }else if(status == "delivery"){
                    r.return_status = ''
                }else if(status == "approve"){
                    r.return_status = 'product_approved'
                }else{
                    r.return_status = 'confirmed';
                    r.logistic_partner.pickup_partner = res.partners[r.id]['pickup_logistics'];
                }
            }else{
                $('#btn_trigger_return'+r.id).attr('disabled', false)
                $('#btn_trigger_return'+r.id).attr('value','Trigger Return')
                
            }
        })
    }

    $scope.confirm_order = function(order,c_type){
        if(c_type == "seller"){
            $('#btn_seller'+order.id).attr('disabled', true)
            $('#btn_seller'+order.id).attr('value','Confirming..')
        }else{
            $('#btn_buyer'+order.id).attr('disabled', true)
            $('#btn_buyer'+order.id).attr('value','Confirming..')
        }
        $http.put('/zapadmin/orders/',{'order_id':order.id,'c_type':c_type}).
        success(function(rs){
            if(rs.status == 'success'){
                if(c_type == 'seller'){
                     order.confirmed_with_seller = true                               
                }else{
                     order.confirmed_with_buyer = true   
                }
                if(rs.message == 'confirmed'){
                    order.order_status = 'confirmed'
                }
            }else{
                if(c_type == "seller"){
                    $('#btn_seller'+order.id).attr('disabled', false)
                    $('#btn_seller'+order.id).attr('value','Confirm')
                }else{
                    $('#btn_buyer'+order.id).attr('disabled', false)
                    $('#btn_buyer'+order.id).attr('value','Confirm')
                }
            }
        })
    }
    $scope.search_order = function(search_id){
        $scope.page = 'order'
        $('.order_nav_bar').removeClass('is_hidden').show();
        $(".nav-bar").children("li").removeClass("selected")
        $(".order_nav_bar").children("li").removeClass("selected")
        $("#liorders").addClass("selected")
        $("#ordr").addClass("selected")
        $scope.page_title = 'Products Orders'
        $('.catalogue_nav_bar').hide();
        // $scope.get_order_details()
        $http.post('/zapadmin/orders/',{order_id:search_id}).success(function(response) {
            if(response.status == 'success'){
                $scope.orders = response.data.data
                $scope.total_pages_order = 1
                // $scope.orders = response.data
            }else{
                swal('Order Not Found')
            }
        });
    }
    
    $scope.search_by_partner = function(partner){
        $http({
                method: 'GET',
                url: '/zapadmin/logistics_evaluation/?partner='+partner,
            }).then(function successCallback(response) {
                console.log(response)
                $scope.logistics = response.data.data.log_data
                $scope.logistics_partners = response.data.data.logistics_partners
            });
    }
    $scope.get_big_size = function(id,url,product){
        product.image1 = url.replace("100x100", "1000x1000");
        $('.img_class').removeClass('is_current')
        $('#img'+id).addClass('is_current')
    }
    $scope.get_upload_page = function(){
        $scope.get_upload_details()
        $scope.template =''///zapstatic/frontend/admin_styles/templates/upload.html'
        $(".catalogue_nav_bar").children("li").removeClass("selected")
        $("#upload").addClass("selected")
        $scope.page_title = 'Upload Products'
        //$scope.get_users()
        $scope.page = 'upload'
    }

    // $scope.get_users = function(search_word){
    //     $http({
    //         method: 'GET',
    //         url: "/zapadmin/get_users/",
    //     }).then(function successCallback(response) {
    //         $scope.all_users = response.data.data
    //         console.log($scope.all_users)
    //     }, function errorCallback(response) {
    //         console.log(response);
    //     });        
    // }
    $scope.load_zapexc_accounts = function(){
        $http({
            method: 'GET',
            url: "/zapadmin/load_zapexc_accounts/",
        }).then(function successCallback(response) {
            $scope.selleraccounts = response.data.data
        }, function errorCallback(response) {
            console.log(response);
        });
    }
    $scope.change_user = function(params){
        //alert(JSON.stringify(params))
        var param = params.split(',')
        var id = param[0]
        $scope.user_selected = {'type':param[1]}
        $http({
            method: 'GET',
            url: "/zapadmin/address/"+id+"/",
        }).then(function successCallback(response) {
            $scope.addresses = response.data.data
            if ($scope.user_selected && ($scope.user_selected.type == 'zap_exclusive' || $scope.user_selected.type == 'zap_dummy')){
                $scope.load_zapexc_accounts()
            }
        }, function errorCallback(response) {
            console.log(response);
        });  

        $http({
                method: 'GET',
                url: "/zapadmin/accountnumber/"+id+"/",
            }).then(function successCallback(response) {
                $scope.account_num = response.data.user_acc
                $scope.confirm_account_num = response.data.user_acc
                $scope.ifsc_code = response.data.ifsc_code
                if($scope.account_num && $scope.ifsc_code){
                    $scope.account_num_edit = 0
                }
                else{
                    $scope.account_num_edit = 1
                }
            }, function errorCallback(response) {
                console.log(response.data.category);
            });        
    }
    $scope.save_address=function(){
        if($scope.page == 'upload'){
            $scope.userid = $(".chosen-select").val().split(',')[0]
        }else{
            $scope.userid = $scope.user_product_id
        }
        $http({
                method: 'POST',
                url: "/zapadmin/address/"+$scope.userid+"/",
                data:{
                    'name': $scope.new_name,
                    'address': $scope.new_address,
                    'city': $scope.new_city,
                    'state': $scope.new_state,
                    'phone': $scope.new_phone,
                    'pincode': $scope.new_pincode,
                    'email': $scope.new_email,
                }
            }, console.log($scope.new_pincode)).error(function(response) {
                console.log(response)
            }).then(function successCallback(response) {
                console.log(response)
                if(response.data.data){
                    response.data.data.state=$scope.new_state
                    if($scope.page == 'upload'){
                        $scope.addresses.push(response.data.data)
                        $scope.new_name = ''
                        $scope.new_address = ''
                        $scope.new_city = ''
                        $scope.new_state = ''
                        $scope.new_phone = ''
                        $scope.new_pincode = ''
                        $scope.new_email = ''
                        document.getElementById('add-address').style.display = 'none';
                    }
                    else{
                        //alert(JSON.stringify(response.data.data))
                        $scope.user_addresses.push(response.data.data) 
                        $scope.user_pick_id = response.data.data.id   
                    }
                    // else{
                    //     $scope.add.address.push(response.data.data)
                    //     $scope.add.id = response.data.data['id']
                    //     alert(JSON.stringify($scope.add))
                    // }
                    //$scope.modal_pop=0

                }else{
                    alert(JSON.stringify(response.data.detail))
                }
         });
    }

    $scope.img_id = 1;
    //$scope.new_img=1;
    $scope.images_selected=[]
    // $scope.cropper = {};
    //$scope.custom_cropper = [1, 0, 0]
    // $scope.cropper.sourceImage = null;
    // $scope.cropper.croppedImage   = null;
    // $scope.bounds = {};
    // $scope.bounds.left = 50;
    // $scope.bounds.right = 50;
    // $scope.bounds.top = 50;
    // $scope.bounds.bottom = 50;
    $scope.age = [{'id':0, 'name':'0-3 months'},
                    {'id':1,'name':'3-6 months'},
                    {'id':2,'name':'6-12 months'},
                    {'id':3,'name':'1-2 years'}];
    $scope.conditions=[{'id':0,'name':'New with tags'},
                    {'id':1,'name':'Mint Condition'},
                    {'id':2,'name':'Gently loved'},
                    {'id':3,'name':'Worn out'}];
    $scope.free_size=1   
    $scope.addresses = []    
    $scope.size_selected = [{}]  
    $scope.addChoice = function(){
        $scope.size_selected.push({})
    }    
    $scope.removeChoice = function(item){
        $scope.size_selected.shift(item)
    }
    $scope.add_visible_crop=function (id) {
        $('.crop-image').addClass('is_visible');
    
    }
    // $scope.get_brands = function(search_word){
    //         $http({
    //             method: 'GET',
    //             url: "/getbrand/?q="+search_word,
    //         }).then(function successCallback(response) {
    //             $scope.brands = response.data
    //             // $scope.brands.unshift({'brand':'--Select Brand--','id':'00000'})
    //             $scope.brand_selected = $scope.brands[0]
    //         }, function errorCallback(response) {
    //             console.log(response);
    //         });        
    // }
    // $scope.get_addresses = function(){
    //         $http({
    //             method: 'GET',
    //             url: "/address/crud/",
    //         }).then(function successCallback(response) {
    //             console.log(response)
    //             $scope.addresses=response.data.data
    //         }, function errorCallback(response) {
    //             console.log(response);
    //         });        
    // }
    $scope.get_styles = function(search_word){
            $http({
                method: 'GET',
                url: "/getfashion/",
            }).then(function successCallback(response) {
                $scope.styles = response.data
                // $scope.styles.unshift({'brand':'--Select Brand--','id':'00000'})
                $scope.style_selected = $scope.styles[0]
            }, function errorCallback(response) {
                console.log(response);
            });        
    }
    var UploadStart = Date.now()
    // $scope.get_upload_details = function(search_word){
    //         $http({
    //             method: 'GET',
    //             url: "/catalogue/crud/",
    //         }).then(function successCallback(response) {
    //             $scope.cat=response.data.data['category']
    //             $scope.sub_cat = response.data.data['sub_category']
    //             $scope.sub_categories_temp=response.data.data['sub_category']
    //             $scope.colors = response.data.data['color']
    //             $scope.occasions = response.data.data['occasion']
    //             $scope.styles = response.data.data['fashion_types']
    //             $scope.states = response.data.data['states']
    //             console.log($scope.sub_categories+'=====')
    //             console.log(response.data.data);
    //             $scope.brands = response.data.data['brands']
    //             //$scope.brand_selected = $scope.brands[0]
    //             $scope.categories = response.data.data['category']
    //             $scope.sub_categories = response.data.data['sub_category']
    //             $scope.size_list = response.data.data.global_product_list
    //         }, function errorCallback(response) {
    //             console.log(response.data.category);
    //         });        
    // }
    
    // $scope.get_brands("")
    // $scope.get_styles()
    //$scope.get_upload_details()
    // $scope.get_addresses()
    $scope.set_brand = function(){
        console.log(typeof($scope.brand_selected))
        if(typeof($scope.brand_selected) == 'object'){
            $scope.brand_selected = $scope.brand_selected
            $scope.search_word = $scope.brand_selected.brand
         }else{
            $scope.search_word = ''
        }
    }   
    $scope.change_brands = function(search_word){
        if(search_word){
            $scope.filtered_brands = []
            for(i in $scope.brands){
                if($scope.brands[i]['brand'].toLowerCase().indexOf(search_word.toLowerCase()) > -1){
                    $scope.filtered_brands.push($scope.brands[i])
                } 
            }
        }else{
            $scope.filtered_brands = $scope.brands
        }
    }



    // $scope.hide_crop=function() {
    //     $('.crop-image').removeClass('is_visible');
    //         $scope.images_selected.push({'id':$scope.img_id,'img_url':$scope.cropper.croppedImage})
    //         $scope.img_id=$scope.img_id+1;
    //         if ($scope.images_selected.length==6){
    //             $scope.new_img=0;
    //         }
    //         $scope.img1=$scope.cropper.croppedImage;
    //         $scope.cropper.croppedImage=null
    // }
    $scope.cancel_crop = function(){
        $('.crop-image').removeClass('is_visible');
    }
    $scope.remove_img=function(id){
        for(var i=0;i<$scope.images_selected.length;i++){
            if($scope.images_selected[i].id==id){
                $scope.images_selected.splice(i,1)
            }
        }
        //$scope.new_img=1;
    }
    $scope.post_account_num = function(id){
        if($scope.account_num && $scope.ifsc_code  && $scope.account_num == $scope.confirm_account_num)
        {
            $http({
                method: 'POST',
                url: "/zapadmin/accountnumber/"+id+"/",
                data: {
                    'account_number': $scope.account_num,
                    'ifsc_code': $scope.ifsc_code,
                    'account_holder': $scope.account_holder
                }
            }).then(function successCallback(response) {
                if(response.data.status == 'success'){
                    $scope.account_num_edit = 0
                }else{
                    if ('ifsc_code' in response.data.detail){
                        alert("ifsc code needs 5 character")
                    }
                }
            }, function errorCallback(response) {
                console.log(response.data.category);
            }); 
        }
    }
    $scope.changeSize = function(size){
        var count = 0
        for (i in $scope.size_selected){
            if(size.size == $scope.size_selected[i].size){
                if(++count == 2){
                    alert("This size already selected")
                    size.size = ''
                    return false
                } 
            }
        }
    }
    $scope.reject_reasons =[{'id':'0','reason':'The images are unclear'},
                            {'id':'1','reason':'Brand of product not shown in images'},
                            {'id':'2','reason':'The brand not accepted'},
                            {'id':'3','reason':'Incorrect information'},
                            {'id':'4','reason':'Other'}]
    $scope.product_type = '2'
    $scope.size_selected = [{}]
    //$scope.sellerDetail = {}
    $scope.submit=function(){
        var image_ids = []
        if($scope.images_selected.length==0){
            swal('Oops...','Select atleast one image!','error')
            return false;
        }
        if($scope.product_type == 2){
            if($('.address-card.is_selected').length==0){
                swal('Oops...','Select Pickup address!','error')
                return false;
            }
            if($scope.original_price<$scope.listing_price){
                swal('Oops...','Listing price must be less than Original price!','error')
                return false;
            }
            server_data={
                    'pickup_address': $('.address-card.is_selected').attr('select-card'),
                    //'images': $scope.images_selected,
                    'title': $scope.product_title,
                    'description': $scope.product_description,
                    'style': $scope.style_selected,
                    'brand': $scope.brand_selected.id,
                    'original_price':Math.round($scope.original_price),
                    'listing_price': Math.round($scope.listing_price),
                    'occasion': $scope.occasion_selected,
                    'sale': $scope.product_type,
                    'product_category': $scope.sub_cat_selected,
                    'color': $scope.color_selected,
                    'age': $scope.age_selected['id'],
                    'condition': $scope.condition['id'],
                    'discount': $scope.discount,
                    'free_quantity':$scope.free_quantity,
                    'size_type':$scope.size_selected[0].size_type,
                    'user': $(".chosen-select").val().split(',')[0],//$scope.user_selected.id,
                    'seller':$scope.sellerDetail,
                    'email':$scope.sellerDetailSelected

                }
        }else{
            server_data={
                    'pickup_address': $('.address-card.is_selected').attr('select-card'),
                    //'images': $scope.images_selected,
                    'title': $scope.product_title,
                    'description': $scope.product_description,
                    'style': $scope.style_selected,
                    'brand': $scope.brand_selected.id,
                    'occasion': $scope.occasion_selected,
                    'sale': $scope.product_type,
                    'product_category': $scope.sub_cat_selected,
                    'color': $scope.color_selected,
                    'free_quantity':$scope.free_quantity,
                    'size_type':$scope.size_selected[0].size_type,
                    'user':$(".chosen-select").val().split(',')[0],
                    'seller':$scope.sellerDetail
                }
        }

        $("#addProduct").val("Please Wait...").attr('disabled', 'disabled');
        
        if($scope.free_size==false){
            server_data['global_size'] = $scope.size_selected
        }else{
            server_data['global_size'] = 'Free Size'
        }
        server_data['time_to_make'] = $scope.timetomake
        if($scope.commision<0 || $scope.commision>100){
            swal('Oops...','Percentage Commission should be between 0 - 100.','error')
            return false;
        }
        server_data['percentage_commission'] = $scope.commision
        // alert(JSON.stringify(server_data))
        // return false;
        // $http({
        //     method: 'PUT',
        //     url: "/zapadmin/upload/",
        //     data:server_data
        // }).error(function(error){console.log(error)
        //     $("#addProduct").val("Upload").prop('disabled', false);
        // }).then(function successCallback(response) {
        //     console.log(response)  
        //     if(response.data.status == 'error'){   
        //         alert(JSON.stringify(response.data.detail))
        //         $("#addProduct").val("Upload").prop('disabled', false);
        //     }else{
                for(i in $scope.images_selected){
                    $scope.images_selected[i]['pos'] = i
                    $http({
                        method: 'POST',
                        url: "/zapadmin/upload/image",
                        data:$scope.images_selected[i]
                    }).then(function successCallback(response) {
                        console.log(response)  
                        if(response.data.status == 'success'){   
                            image_ids.push(response.data.img_id)
                            console.log(image_ids.length+' == '+$scope.images_selected.length)
                            if(image_ids.length == $scope.images_selected.length){
                                server_data['images'] = image_ids 
                                $http({
                                    method: 'POST',
                                    url: "/zapadmin/upload/",
                                    data:server_data
                                }).error(function(error){console.log(error)
                                    $("#addProduct").val("Upload").prop('disabled', false);
                                }).then(function successCallback(response) {
                                    console.log(response)  
                                    if(response.data.status == 'success'){      
                                        swal("Success!", "Product Uploaded Successfully!", "success")
                                        $("#addProduct").val("Upload").prop('disabled', false);
                                        $scope.images_selected = []
                                        $scope.product_title = ''
                                        $scope.product_description = ''
                                        $scope.brand_selected = ''
                                        $scope.search_word = ''
                                        $scope.category = ''
                                        $scope.sub_cat_selected = ''
                                        $scope.color_selected = ''
                                        $scope.style_selected = ''
                                        $scope.occasion_selected = ''
                                        $scope.size_selected = [{}]
                                        $scope.original_price = ''
                                        $scope.age_selected = ''
                                        $scope.condition = ''
                                        $scope.listing_price = 0
                                        if($scope.sellerDetailSelected){$scope.sellerDetailSelected['email'] = ''}
                                    }else{
                                        alert("Something went wrong")
                                        $("#addProduct").val("Upload").prop('disabled', false);
                                    }
                                });
                            }
                        }else{
                            $("#addProduct").val("Upload").prop('disabled', false);
                        }
                    })
                }    
                
        //     }
        // })          
    }
    $scope.cat_change=function(){
        $scope.free_size=false
        if($scope.sub_cat_selected==undefined){
            $scope.free_size=true
            return true
        }
        // else if($scope.category.category_type == "FS"){
        //     $scope.free_size=true
        // }else{
        //     $scope.free_size=false
        // }

        // var sub_new=[]
        // for(var i=0;i<$scope.sub_categories.length;i++){

        //     if($scope.sub_categories[i].parent['name']==$scope.category){
        //         sub_new.push($scope.sub_categories[i])
        //     }
        // }

        for(i in $scope.sub_cat){
            if($scope.sub_cat[i].id == $scope.sub_cat_selected){
                if($scope.sub_cat[i].parent.category_type == "FS"){
                    $scope.free_size=true
                }
            }
        }
        //$scope.sub_categories_temp=sub_new
        $scope.sizes = []
        $scope.size_type_list=[]
        // $scope.free_size=true
        // for(var j=0;j<$scope.size_list.length;j++){
        //     if(($scope.size_list[j]['category_type']==$scope.category['category_type']) && !($scope.size_list[j]['size_type'] == "FS")){
        //         $scope.free_size=false
        //     }
        // }
        
    }
    $scope.size_type_change = function(size_type){
        $scope.sizes = $scope.size_list.filter(function(i){if((i.size_type==size_type) && (i.category==$scope.category)){return true}})
        alert($scope.sizes)
    }
    $scope.deleteAddress=function(id){
        $http({
                method: 'DELETE',
                url: "/address/crud/?address_id="+id,
                data:
                {'address_id':id}
            }).error(function(response) {
                console.log(response)
            }).then(function successCallback(response) {
                if(response.data.data){
                    for(var i=0;i<$scope.addresses.length;i++){
                    if($scope.addresses[i]['id']==id){
                        $scope.addresses.splice(i,1)
                    }
                }
            }
         });
    }
    

    $scope.fasioncalculator = function(){
        if($scope.age_selected && $scope.condition && $scope.original_price){
            $http({
                    method: 'POST',

                    url: "/catalogue/zapfashioncalculator/",
                    data:{
                        'age':$scope.age_selected['id'],
                        'condition':$scope.condition['id'],
                        'original_price':$scope.original_price,
                    }
                }).error(function(response) {
                    console.log(response)
                }).then(function successCallback(response) {
                    console.log(response)
                    $scope.listing_price = response.data.data.max_listing_price
                    // alert(JSON.stringify(response.data.data))
                    $("#slider").attr('max', response.data.data.max_listing_price);
                    $("#slider").val(response.data.data.max_listing_price);  
                    //$("#slider").slider('refresh');
            });
        }
    }
    $scope.slider_change = function(){
        //alert($scope.listing_price)
    }
    $( "div" ).delegate( ".address-card", "click", function() {
            $('.address-card').removeClass('is_selected');
            $(this).addClass('is_selected');
        });
    
    $('.new-address-card').click(function() {
        $('#add-address').fadeIn(500);
    });
    $('#add-address .cancel').click(function() {
        $('#add-address').fadeOut(500);
    })


    $scope.open_popup = function(userid,add) {
        $scope.add = add
        $scope.userid = userid
        $scope.modal_pop=true
        alert(userid)
    }

    $scope.change_logistic = function(logistic) {

        $http({
            method: 'POST',
            url: '/zapadmin/logistics_evaluation/',
            data:{
                'logistic':logistic.id,
                'consignee':parseInt(logistic.consignee.id),
                'consignor':parseInt(logistic.consignor.id),
                'packaging_material_delivered':logistic.pm_check,
                'triggered_packaging_material': logistic.pro_check,
                'status': logistic.status_str,
                'packaging_material_partner': logistic.pm_partner,
                'product_delivery_partner': logistic.pro_partner,
            }

        }).error(function(response) {
                console.log(response)
            }).then(function successCallback(response) {
                console.log(response)
                logistic.consignee.full_address = response.data.data.consignee
                logistic.consignor.full_address = response.data.data.consignor
                logistic.status = logistic.status_str
                logistic.packaging_material_partner.value = response.data.data.pm_partner
                logistic.product_delivery_partner.value = response.data.data.pro_partner




                // alert(JSON.stringify(response.data.data.consignee))
                // $scope.listing_price = response.data.max_listing_price
                // $("#slider").attr('max', response.data.max_listing_price);
                // $("#slider").val(response.data.max_listing_price);  
                // //$("#slider").slider('refresh');
        });

        // alert(logistic.pm_check)
    }

    $scope.goto_edit_page = function(id,index){
        if($scope.page == 'catalogue'){
            window.location.href = "/zapadmin/edit/"+id+"/tobeapproved/"
            $localStorage.editproduct_id = id
            $localStorage.index = index
        }
        else if($scope.page == 'disapproved'){
            window.location.href = "/zapadmin/edit/"+id+"/disapproved/"            
        }else{
            window.location.href = "/zapadmin/edit/"+id+"/approved/"
        }
        // $http({
        //     method: 'GET',
        //     url: "/zapadmin/check_product_sold/?id="+id+"&type="+$scope.page,
        // }).then(function successCallback(response) {
        //     alert(JSON.stringify(response))
        //     $scope.action_datas = response.data.data
        // })
    }

    // $scope.get_action_datas = function(action){
    //     if(action == 'product' || action == 'profile'){    
    //         $http({
    //             method: 'GET',
    //             url: "/zapadmin/get_action_datas/?action="+action,
    //         }).then(function successCallback(response) {
    //             $scope.action_datas = response.data.data
    //         })
    //     }
    // }
    // var p_to_update
    // $scope.load_users = function(old_user,pick_id,product,c_pta){
    //     $scope.change_user_flag = 1
    //     $scope.user_product_id = old_user
    //     //$scope.user_pick_id = pick_id
    //     p_to_update = product
    //     $scope.c_pta_index = c_pta
    //     $http({
    //         method: 'GET',
    //         url: "/zapadmin/load_users/",
    //     }).then(function successCallback(response) {
    //         $scope.zapylers = response.data.data
    //         //alert(JSON.stringify($scope.zapylers))
    //     })
    //     $scope.load_pickup_addresses(old_user)
    // }
    $scope.load_pickup_addresses = function(){
        $http({
            method: 'GET',
            url: "/zapadmin/load_user_addresses/",
        }).then(function successCallback(response) {
            $scope.all_addresses = response.data.data
            //alert(JSON.stringify($scope.zapylers))
        })
    }
    $scope.load_single_product_datas = function(product_id){
        $http({
            method: 'POST',
            url: "/zapadmin/update_product/?product_id="+product_id,
        }).then(function successCallback(response) {
            alert(JSON.stringify($scope.productsToApprove))
            $scope.productsToApprove[$localStorage.index] = response.data.data;
        })
    }
    //if($localStorage.editproduct){
        //$scope.load_single_product_datas($localStorage.editproduct_id)
        //$localStorage.editproduct = false
    //}
    $localStorage.firstPageClick = true;
    $scope.show_pagination = function(){
        $('#paginationholder').html('');
        $('#paginationholder').html('<ul id="pagination-demo" class="pagination-sm"></ul>');
        $('#pagination-demo').twbsPagination({
            totalPages: $scope.total_pages,
            visiblePages: 10,
            onPageClick: function (event, page) {
                if($localStorage.firstPageClick) {
                   $localStorage.firstPageClick = false;
                   return;
                }
                if($scope.page == 'catalogue'){
                    document.getElementById('loading').style.display = 'block';
                    $http({
                        method: 'GET',
                        url: '/zapadmin/get_productsToApprove/'+page+'/?search_word='+$('#listing_search').val(),
                    }).then(function successCallback(response) {
                        document.getElementById('loading').style.display = 'none';
                        $scope.productsToApprove = response.data.data
                        $scope.total_pages = response.data.total_pages
                        //$scope.show_pagination()
                    });
                }
                else if($scope.page == 'approved'){
                    document.getElementById('loading').style.display = 'block';    
                    $http({
                        method: 'GET',
                        url: '/zapadmin/get_approvedProducts/'+page+'/?search_word='+$('#listing_search').val(),
                    }).then(function successCallback(response) {
                        document.getElementById('loading').style.display = 'none';
                        $scope.productsToApprove = response.data.data
                        $scope.total_pages = response.data.total_pages
                    }); 
                }else{
                    document.getElementById('loading').style.display = 'block';                    
                    $http({
                        method: 'GET',
                        url: '/zapadmin/get_disapprovedProducts/'+page+'/?search_word='+$('#listing_search').val(),
                    }).then(function successCallback(response) {
                        document.getElementById('loading').style.display = 'none';
                        $scope.productsToApprove = response.data.data
                        $scope.total_pages = response.data.total_pages
                    });
                }
            }
        });
        $('#listing_search').removeClass('listing_spinner')
    }

    $scope.in_process = function(){
        $scope.template ='/zapstatic/frontend/admin_styles/templates/in_process.html'
        $('.logistics_nav_bar').children("li").removeClass("selected")
        $("#inprocess").addClass("selected")
       $http({
            method: 'GET',
            url: '/zapadmin/in_process/',
        }).then(function successCallback(response) {
            $scope.in_process_data = response.data.data
        }); 
    }
    $scope.verify_logistics = function(log){
        $http({
            method: 'POST',
            url: '/zapadmin/in_process/',
            data:{'action':'verify_logistics','logistic':log.id}
        }).then(function successCallback(response) {
            if(response.data.status == 'success'){
                log.verified = true
            }
        })
    }
    $scope.reject_order = function(order,log,child,parent){
        $http({
            method: 'POST',
            url: '/zapadmin/in_process/',
            data:{'action':order,'logistic':log.id,'order':log.orders,'return':log.returns}
        }).then(function successCallback(response) {
            if(response.data.status == 'success'){
                if(order == 'trigger'){
                    log.triggered_pickup = true
                    log.pick_status = 'Menifested'
                }else if(order == 'trigger_delivery'){
                    log.trigger_delivery = true
                    log.del_status = 'Menifested'
                }else{
                    log.orders.splice(child,1)
                    if (log.orders==''){
                        $scope.in_process_data.splice(parent,1)
                    }
                }
            }
        }); 
        
    }
    $localStorage.firstPageClick1 = true;
    $scope.show_order_pagination = function(){
        $('#orderpagination').html('');
        $('#orderpagination').html('<ul id="orderpagination-demo" class="pagination-sm"></ul>');
        $('#orderpagination-demo').twbsPagination({
            totalPages:$scope.total_pages_order,
            visiblePages: 10,
            onPageClick: function (event, page) {
                if($localStorage.firstPageClick1) {
                   $localStorage.firstPageClick1 = false;
                   return;
                }
                document.getElementById('loading').style.display = 'block';                    
                $http.get('/zapadmin/orders/?page='+page).success(function(response){
                    $scope.orders = response.data.data
                    $scope.total_pages_order = response.data.total_pages
                    document.getElementById('loading').style.display = 'none';

                });
            }
        });
        $('#listing_search').removeClass('listing_spinner')
    }
    // $scope.before_process = function(){
    //     $scope.template ='/zapstatic/frontend/admin_styles/templates/before_process.html'
    //     $('.logistics_nav_bar').children("li").removeClass("selected")
    //     $("#befrprocess").addClass("selected")
    //    $http({
    //         method: 'GET',
    //         url: '/zapadmin/before_process/',
    //     }).then(function successCallback(response) {
    //         $scope.before_process_data = response.data.data
    //     }); 
    // }
    // $scope.done_process = function(){
    //     $scope.template ='/zapstatic/frontend/admin_styles/templates/done_process.html'
    //     $('.logistics_nav_bar').children("li").removeClass("selected")
    //     $("#doneprocess").addClass("selected")
    //    $http({
    //         method: 'GET',
    //         url: '/zapadmin/done_process/',
    //     }).then(function successCallback(response) {
    //         $scope.done_process_data = response.data.data
    //     }); 
    // }
    $scope.payout = function(d){
        swal({
            title: 'Are you sure?',
            text: 'test message',
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, disapprove!',
            closeOnConfirm: false,
            showLoaderOnConfirm:true
        },
        function() {
            $http({
                method: 'POST',
                url: '/zapadmin/done_process/',
                'data':{'log_id':d.log},
            }).then(function successCallback(response) {
                if(response.data.status == 'success'){
                    d.initiate_payout = false
                    $scope.$apply()
                    swal("Success")
                }
            }); 
        })
    }
    $scope.amzadDelivery = function(order){
        $('#btn_amzad'+order.id).prop('disabled', true);
        $("#btn_amzad"+order.id).text('PLEASE WAIT');
        $http.post('/zapadmin/before_process/',{'id':order.id, 'status':'amzadDelivery','type':'order'}).success(function(rs){
            if(rs.status == 'success'){
                order.order_status = 'delivered'
            }else{
                $('#btn_amzad'+order.id).prop('disabled', false);
                $("#btn_amzad"+order.id).text('Amzad Delivered');
            }
        })
    }
    $scope.amzadPicked = function(order, status){
        if (status == 'picked'){
            $('#btn_amzad_pick'+order.id).prop('disabled', true);
            $("#btn_amzad_pick"+order.id).text('PLEASE WAIT');
            $http.post('/zapadmin/before_process/',{'id':order.id, 'status':'amzadPicked','type':'order','activity':'picked'}).success(function(rs){
                if(rs.status == 'success'){
                    order.order_status = 'picked_up'
                }else{
                    $('#btn_amzad_pick'+order.id).prop('disabled', false);
                    $("#btn_amzad_pick"+order.id).text('Amzad Pickup');
                }
            })
        }else{
            $('#btn_amzad_reach'+order.id).prop('disabled', true);
            $("#btn_amzad_reach"+order.id).text('PLEASE WAIT');
            $http.post('/zapadmin/before_process/',{'id':order.id, 'status':'amzadPicked','type':'order','activity':'reached'}).success(function(rs){
                if(rs.status == 'success'){
                    order.order_status = 'verification'
                }else{
                    $('#btn_amzad_reach'+order.id).prop('disabled', false);
                    $("#btn_amzad_reach"+order.id).text('Amzad Reached');
                }
            })
        }
    }
    $scope.triggerLogistics = function(order,status, delivery_type){

        if(status == 'logistics'){
            $('#btn_logistics'+order.id).prop('disabled', true);
            $("#btn_logistics"+order.id).text('PLEASE WAIT');
        }else
        if(status == 'pickup'){
            $('#btn_pickup'+order.id).prop('disabled', true);
            $("#btn_pickup"+order.id).text('PLEASE WAIT');
        }else
        if(status == 'cancel'){
            if (confirm("press ok to cancel order!") == true) {
                $('#btn_cancel'+order.id).prop('disabled', true);
                $("#btn_cancel"+order.id).text('PLEASE WAIT');
            } else {
                return false;
            }
        }else
        if(status == 'delivery'){
            if(order.delivery_partner=='ZP'){
                // $scope.amzadDelivery(order)
                // return false;
                status="amzadDelivery";
            }else{
            }
            $(".btn_delivery"+order.id).text('PLEASE WAIT');
            $('.btn_delivery'+order.id).prop('disabled', true);
        }
        $http.post('/zapadmin/before_process/',{'id':order.id, 'status':status,'type':'order', 'delivery_type':delivery_type}).
        success(function(rs){
            if(rs.status == 'success'){
                if(status == 'amzadDelivery'){
                    order.order_status = 'on_the_way_to_you';
                    order.delivery_order_logistics = 1;
                }else if(status == 'pickup'){
                    order.pickup_orders_logistics = 1
                }else if(status == 'cancel'){
                    order.order_status = 'cancelled'
                }else if(status == 'delivery'){
                    order.delivery_order_logistics = 1
                }else{
                    order.pickup_partner = rs['partners'][order.id]['pickup_logistics'];
                    order.delivery_partner = rs['partners'][order.id]['delivery_logistics'];
                    order.new_pickup_seller = order.pickup_partner;
                    if(order.with_zapyle){
                        order.product_verification = 'approved'
                        order.order_status = 'verification'
                    }else{
                        order.order_status = 'pickup_in_process'
                        order.pickup_partner = rs.partners[order.id]['pickup_logistics'];
                    }

                    // for(i in rs.data){
                    //     for(j in $scope.orders){
                    //         if($scope.orders[j]['id'] == rs.data[i]){
                    //             $scope.orders[j]['order_status'] = 'pickup_in_process';
                    //         }
                    //     }
                    // }
                }
            }else{
                $('#btn_pickup'+order.id).prop('disabled', false);
                $("#btn_pickup"+order.id).text('Trigger Pickup');
                $('#btn_logistics'+order.id).prop('disabled', false);
                $("#btn_logistics"+order.id).text('Trigger Logistics');
                $('.btn_delivery'+order.id).prop('disabled', false);
                $(".btn_delivery"+order.id).text('Trigger Delivery');
            }
        })
    }

    $scope.TrackOrder = function(order){
        $("#btn_track"+order.id).text('PLEASE WAIT');
        $('#btn_track'+order.id).prop('disabled', true);
        $http.post('/zapadmin/track_order/',{'order_id':order.id, 'status':order.order_status}).
        success(function(rs){
            // alert(JSON.stringify(rs))
            if(rs.status == 'success'){
                alert(JSON.stringify(rs.data))
            }
            $('#btn_track'+order.id).prop('disabled', false);
            $("#btn_track"+order.id).text('TrackOrder');
        });
    }
    $scope.verifyPickedUp = function(order,status){
        if(status == "product_approved"){
            $('#btn_approve'+order.id).prop('disabled', true);            
            $('#btn_approve'+order.id).text('PLEASE WAIT');
        }else{
            $('#btn_reject'+order.id).prop('disabled', true);            
            $('#btn_reject'+order.id).text('PLEASE WAIT');
        }
        $http.post('/zapadmin/verify_pickedup/',{'id':order.id,'status':status}).
        success(function(rs){
            if(rs.status == 'success'){
                order.order_status = status;
                order.product_verification = status.replace('product_','')
            }else{
                if(status == "product_approved"){
                    $('#btn_approve'+order.id).prop('disabled', false);            
                    $('#btn_approve'+order.id).text('Approve');
                }else{
                    $('#btn_reject'+order.id).prop('disabled', false);            
                    $('#btn_reject'+order.id).text('Reject');
                }
            }
        })

    }

    $scope.triggerReturn = function(order){
        $('#btn_return_trig'+order.id).prop('disabled', true);            
        $('#btn_return_trig'+order.id).text('PLEASE WAIT');
        $http.post("/zapadmin/trigger_return/",{"order_id":order.id}).
        success(function(rs){
            console.log(rs)
            if(rs.status == "success"){
                order.order_status = "return_requested";
                order.return_delivery_partner = rs.partners[order.id]['delivery_logistics'];
            }
        })
    }

    $scope.cancel_before_process = function(data,status){
        $http({
            method: 'POST',
            url: '/zapadmin/before_process/',
            data:{
                'id':data['id'],
                'status':status,
                'type':data['type']
            }
        }).then(function successCallback(response) {
            if (status == 'logistics'){
                o_ids = response.data.data
                for (j in o_ids){
                    for(i in $scope.before_process_data){
                        if($scope.before_process_data[i]['id'] == o_ids[j] && $scope.before_process_data[i]['type'] == data['type']){
                            $scope.before_process_data.splice(i, 1)
                        }
                    }
                }
            }else if(status=='cancel'){
                data.cancelled = true
            }else{
                data.cancelled = false
            }
        }); 
    }
    $scope.change_buyer_seller = function(pickup,type,order){
        $http({
                method: 'PUT',
                url: '/zapadmin/orders/',
                data:{
                    'pick_id':pickup.id,
                    'type':type,
                    'order_id':order.id
                }
            }).then(function successCallback(response) {
                
                if(response.data.status == 'success'){
                    if (type == 'seller'){
                        order.seller = pickup.name+' ('+pickup.address+') '+pickup.phone
                        order.change_seller = false
                    }else{
                        order.buyer = pickup.name+' ('+pickup.address+') '+pickup.phone 
                        order.change_buyer = false           
                    }
                }
            });
        
    }
    $scope.change_partner = function(order, type, partner){
        if(type == 'pickup'){
            $('#btn_pickup'+order.id).prop('disabled', true);
            $("#btn_pickup"+order.id).text('PLEASE WAIT');
            
        }else{
            $('.btn_delivery'+order.id).prop('disabled', true);
            $(".btn_delivery"+order.id).text('PLEASE WAIT');
        }
        $http.post('/zapadmin/before_process/',{'id':order.id, 'status':'change_partner','partner':partner,'type':type}).
        success(function(rs){
            if(rs.status == 'success'){
                if(type == 'pickup'){
                    order.pickup_partner = partner
                    $('#btn_pickup'+order.id).prop('disabled', false);
                    $("#btn_pickup"+order.id).text(partner+' Pickup');
                }else{
                    order.delivery_partner = partner
                    $('.btn_delivery'+order.id).prop('disabled', false);
                    if(partner == 'ZP'){
                        $(".btn_delivery"+order.id).text('Amzad Delivery');
                    }else{
                        $(".btn_delivery"+order.id).text("Trigger "+partner+" Delivery");
                    }
        



                }
            }
        });
    }
    $scope.showAcDetails = function(order_number,close){
        if(close){
            $('#acc_details').removeClass('is_visible')
            return false;
        }
        $http.get('/zapadmin/seller_buyer_account?order_number='+order_number).
        success(function(rs){
            // alert(JSON.stringify(rs))
            $scope.ac = rs.data
        // $scope.show_ac_details = 1
        $('#acc_details').addClass('is_visible')
        })
    }
// });

    $scope.sellerDetail_edit_flag = 'edit_hide'
    $scope.seller_edit = function(data){
        for(i in $scope.selleraccounts){
            if($scope.selleraccounts[i]['email'] == data){
                $scope.sellerDetail = $scope.selleraccounts[i]
                $scope.sellerDetail_edit_flag = 'edit'
            }
        }
    }
    $scope.update_seller_account = function(data){
        if($scope.sellerDetail_edit_flag=='add_new'){
            for(i in $scope.selleraccounts){
                if(data['email'] == $scope.selleraccounts[i]['email']){
                    alert('This email is already in list')
                    return false
                }
            }
        }
        $http({
            method: 'POST',
            url: "/zapadmin/load_zapexc_accounts/",
            'data':data
        }).then(function successCallback(response) {
            if(response.data.status == 'success'){
               $scope.load_zapexc_accounts()
               $scope.sellerDetail_edit_flag = 'edit_hide'
               if($scope.sellerDetail_edit_flag=='add_new'){
                   $scope.selleraccounts.push(data)
                   $scope.sellerDetailSelected = data['email']
                }else{
                    for(i in $scope.selleraccounts){
                        if(data['email'] == $scope.selleraccounts[i]['email']){
                            $scope.selleraccounts[i] = data
                        }
                    }
                }
            }else{
                alert(JSON.stringify(response.data.detail))
            }
        }, function errorCallback(response) {
            console.log(response);
        });
    }
    
    $(function () {
        'use strict';

      var console = window.console || { log: function () {} };
      var $image = $('#image');
      // var $download = $('#download');
      var $dataX = $('#dataX');
      var $dataY = $('#dataY');
      var $dataHeight = $('#dataHeight');
      var $dataWidth = $('#dataWidth');
      var $dataRotate = $('#dataRotate');
      var $dataScaleX = $('#dataScaleX');
      var $dataScaleY = $('#dataScaleY');
      var options = {
            aspectRatio: 3 / 4,
            modal: false,
            preview: '.img-preview',
            crop: function (e) {
              $dataX.val(Math.round(e.x));
              $dataY.val(Math.round(e.y));
              $dataHeight.val(Math.round(e.height));
              $dataWidth.val(Math.round(e.width));
              $dataRotate.val(e.rotate);
              $dataScaleX.val(e.scaleX);
              $dataScaleY.val(e.scaleY);
            }
          };

      


          // Cropper
          $image.on({
            'build.cropper': function (e) {
              console.log(e.type);
            },
            'built.cropper': function (e) {
              console.log(e.type);
            },
            'cropstart.cropper': function (e) {
              console.log(e.type, e.action);
            },
            'cropmove.cropper': function (e) {
              console.log(e.type, e.action);
            },
            'cropend.cropper': function (e) {
              console.log(e.type, e.action);
            },
            'crop.cropper': function (e) {
              console.log(e.type, e.x, e.y, e.width, e.height, e.rotate, e.scaleX, e.scaleY);
            },
            'zoom.cropper': function (e) {
              console.log(e.type, e.ratio);
            }
          }).cropper(options);


          // Buttons
          if (!$.isFunction(document.createElement('canvas').getContext)) {
            $('button[data-method="getCroppedCanvas"]').prop('disabled', true);
          }

          if (typeof document.createElement('cropper').style.transition === 'undefined') {
            $('button[data-method="rotate"]').prop('disabled', true);
            $('button[data-method="scale"]').prop('disabled', true);
          }


          // Download
          // if (typeof $download[0].download === 'undefined') {
          //   $download.addClass('disabled');
          // }


          // Options
          $('.docs-toggles').on('change', 'input', function () {
            var $this = $(this);
            var name = $this.attr('name');
            var type = $this.prop('type');
            var cropBoxData;
            var canvasData;

            if (!$image.data('cropper')) {
              return;
            }

            if (type === 'checkbox') {
              options[name] = $this.prop('checked');
              cropBoxData = $image.cropper('getCropBoxData');
              canvasData = $image.cropper('getCanvasData');

              options.built = function () {
                $image.cropper('setCropBoxData', cropBoxData);
                $image.cropper('setCanvasData', canvasData);
              };
            } else if (type === 'radio') {
              options[name] = $this.val();
            }

            $image.cropper('destroy').cropper(options);
          });


          // Methods
          $('.docs-buttons').on('click', '[data-method]', function () {
            $().cropper('getCroppedCanvas', {
                fillColor: '#fff'
            });
            var $this = $(this);
            var data = $this.data();
            var $target;
            var result;

            if ($this.prop('disabled') || $this.hasClass('disabled')) {
              return;
            }

            if ($image.data('cropper') && data.method) {
              data = $.extend({}, data); // Clone a new one

              if (typeof data.target !== 'undefined') {
                $target = $(data.target);

                if (typeof data.option === 'undefined') {
                  try {
                    data.option = JSON.parse($target.val());
                  } catch (e) {
                    console.log(e.message);
                  }
                }
              }
              if(!data.option){
                data.option = {}
                data.option.fillColor = '#FFF'}
              result = $image.cropper(data.method, data.option, data.secondOption);

              switch (data.method) {
                case 'scaleX':
                case 'scaleY':
                  $(this).data('option', -data.option);
                  break;

                case 'getCroppedCanvas':
                  if (result) {

                    // Bootstrap's Modal
                    // console.log(result.toDataURL())
                    setTimeout(function(){

                    $('.crop-image').removeClass('is_visible');
                    $scope.images_selected.push({'id':$scope.img_id,'img_url': result.toDataURL('image/jpeg')})
                    $scope.img_id=$scope.img_id+1;
                    $scope.$apply()
                    $scope.show_crop = false
                    })
                    // $('#getCroppedCanvasModal').modal().find('.modal-body').html(result);

                    // if (!$download.hasClass('disabled')) {
                    //   $download.attr('href', result.toDataURL('image/jpeg'));
                    // }
                  }

                  break;
              }

              if ($.isPlainObject(result) && $target) {
                try {
                  $target.val(JSON.stringify(result));
                } catch (e) {
                  console.log(e.message);
                }
              }

            }
          });


              // Keyboard
              $(document.body).on('keydown', function (e) {

                if (!$image.data('cropper') || this.scrollTop > 300) {
                  return;
                }

                switch (e.which) {
                  case 37:
                    e.preventDefault();
                    $image.cropper('move', -1, 0);
                    break;

                  case 38:
                    e.preventDefault();
                    $image.cropper('move', 0, -1);
                    break;

                  case 39:
                    e.preventDefault();
                    $image.cropper('move', 1, 0);
                    break;

                  case 40:
                    e.preventDefault();
                    $image.cropper('move', 0, 1);
                    break;
                }

              });


              // Import image
              var $inputImage = $('#inputImage');
              var URL = window.URL || window.webkitURL;
              var blobURL;
              if (URL) {
                $inputImage.change(function () {
                  $scope.show_crop = true
                  $('.img-container').removeClass('ng-hide')
                  $('.clearfix').removeClass('ng-hide')
                  var files = this.files;
                  var file;

                  if (!$image.data('cropper')) {
                    return;
                  }

                  if (files && files.length) {
                    file = files[0];

                    if (/^image\/\w+$/.test(file.type)) {
                      blobURL = URL.createObjectURL(file);
                      $image.one('built.cropper', function () {

                        // Revoke when load complete
                        URL.revokeObjectURL(blobURL);
                      }).cropper('reset').cropper('replace', blobURL);
                      $inputImage.val('');
                    } else {
                      window.alert('Please choose an image file.');
                    }
                  }
                });
              } else {
                $inputImage.prop('disabled', true).parent().addClass('disabled');
              }
    })    
});