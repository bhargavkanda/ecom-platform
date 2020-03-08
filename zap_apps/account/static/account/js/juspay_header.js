var zapyle = angular.module('zapyle',['ngStorage','ngSanitize']);
zapyle.config(function($httpProvider, $interpolateProvider) {
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
    $httpProvider.defaults.headers.common["X-Requested-With"] = 'XMLHttpRequest';
    // $httpProvider.defaults.headers["PLATFORM"] = 'WEBSITE';
});
zapyle.factory('httpRequestInterceptor', function () {
    return {
        request: function (config) {
            config.headers['MOBILE'] = isMobile;
         return config;
        }
    };
});

zapyle.config(function ($httpProvider) {
    $httpProvider.interceptors.push('httpRequestInterceptor');
});
zapyle.filter('spaceless',function() {
    return function(input) {
        if (input) {
            return input.replace(/\s+/g, '-');    
        }
    }
});
zapyle.filter('spacetoplus',function() {
    return function(input) {
        if (input) {
            return input.replace(/\s+/g, '+');    
        }
    }
});
zapyle.filter('spacetounderscore',function() {
    return function(input) {
        if (input) {
            return input.replace(/\s+/g, '_');    
        }
    }
});
zapyle.directive('scrollTo', ['ScrollTo', function(ScrollTo){
    return {
      restrict : "AC",
      compile : function(){
        
        return function(scope, element, attr) {
          element.bind("click", function(event){
            ScrollTo.idOrName(attr.scrollTo, attr.offset);
          });
        };
      }
    };
  }])
  .service('ScrollTo', ['$window', 'ngScrollToOptions', function($window, ngScrollToOptions) {

    this.idOrName = function (idOrName, offset, focus) {//find element with the given id or name and scroll to the first element it finds
        var document = $window.document;
        
        if(!idOrName) {//move to top if idOrName is not provided
          $window.scrollTo(0, 0);
        }

        if(focus === undefined) { //set default action to focus element
            focus = true;
        }

        //check if an element can be found with id attribute
        var el = document.getElementById(idOrName);
        if(!el) {//check if an element can be found with name attribute if there is no such id
          el = document.getElementsByName(idOrName);

          if(el && el.length)
            el = el[0];
          else
            el = null;
        }

        if(el) { //if an element is found, scroll to the element
          if (focus) {
              el.focus();
          }

          ngScrollToOptions.handler(el, offset);
        }
        
        //otherwise, ignore
      }

  }])
  .provider("ngScrollToOptions", function() {
    this.options = {
      handler : function(el, offset) {
        if (offset) {
          var top = $(el).offset().top - offset;
          window.scrollTo(0, top);
        }
        else {
          el.scrollIntoView();
        }
      }
    };
    this.$get = function() {
      return this.options;
    };
    this.extend = function(options) {
      this.options = angular.extend(this.options, options);
    };
  });
zapyle.controller('HeaderController', function($scope, $http,  $rootScope, $localStorage, admireService) {   
	// $http.post('https://api.appvirality.com/v1/registerwebuser').
 //    success(function(rs){
 //        alert(JSON.stringify(rs))
 //    })
 $scope.isMobile = isMobile
    // $scope.getHeaderProducts = function(){
    //     $http.get('/catalogue/get_header_products').success(function(rs){
    //         $scope.prods = rs.data
    //         // alert(JSON.stringify(rs))
    //     })
    // }
    // $scope.getHeaderProducts();
    clevertap.event.push("page_change", {
        "new_page":window.location.pathname,
        "old_page":document.referrer.replace(/^[^:]+:\/\/[^/]+/, '').replace(/#.*/, ''),
        "page_view_starttime":Date()
    });
	$scope.FBLogin = function() {
        FB.login(function(response) {
            if(response.status == 'connected'){
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
                    // alert(JSON.stringify(response.data.data.profile_completed))
                    if(response.data.data.profile_completed > 1 && $localStorage.tote && $localStorage.tote['cart_data'].length){
                        $http.post('/zapcart/',$localStorage.tote).
                        success(function(rs){
                            if(rs.status == 'success' && $scope.loginPurpose == 'continue with the purchase'){
                                $localStorage.$reset();
                                window.history.pushState('', '', '#rp_checkout')
                                location.reload();  
                            }
                        })
                    }else{
                        setTimeout(function(){
                            clevertap.profile.push({"Facebook": response.data});
                            window.history.pushState('', '', '#rp_my_profile')
                            location.reload();                       
                        })
                    }
                })
            }else{
                alert('facebook login error')
            }
        }, {scope: 'public_profile,email'});
    };
    $scope.my_profile = function(){

    	$http.get('/user/myinfo/?web=true').
        success(function(data, status, headers, config) {
            if (data.status == "success"){
                $scope.user = data.data
                if($scope.user.zap_username){
                    $('#onboarding0').removeClass('is_hidden')
                    $('#onboarding1').addClass('is_hidden')
                    if($scope.user.gender == 'Male'){var gender = 'M'}else{var gender = 'F'}
                    clevertap.profile.push({
                         "Site": {
                           "Name": $scope.user.zap_username, // User's name
                           "Identity":USER_ID,
                           "email": $scope.user.email,
                           "Gender":gender,
                           // "Phone":$scope.user.phone_number,
                           "Photo":$scope.user.profile_pic
                           // "DOB":Date($scope.user.dob),
                           // "Age": 28
                         }
                    });
                }else{
                    $('#onboarding1').removeClass('is_hidden')
                    $('#onboarding0').addClass('is_hidden')
                }
                angular.copy(data.data,$scope.user1)
                if($localStorage.tote && $localStorage.tote['cart_data'].length){
                    $http.post('/zapcart/',$localStorage.tote).
                    success(function(rs){
                        if(rs.status == 'success'){
                            $localStorage.$reset();
                        }
                    })
                }
            }
        })
    }
    if(ZL != 'True' && $localStorage.tote && $localStorage.tote['cart_data'].length){
        $('#toteBadge').text($localStorage.tote['cart_data'].length)
    }
    var $input = $('.datepicker').pickadate({
        selectMonths: true,
        selectYears: 100
    });
    // var $input = $('.datepicker').pickadate()
    var picker = $input.pickadate('picker')
    $scope.my_info = function(){
        $http.get('/user/myinfo/').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
                $scope.user = data.data
                picker.set('select', $scope.user['dob'], { format: 'dd-mm-yyyy' })
                if($scope.user['selected_location_id']){
                    $scope.user['selected_location_id'] = $scope.user['selected_location_id'].toString();
                }
                setTimeout(function(){$('select').material_select()});
            }
        })
    	//Materialize.updateTextFields();  
    }
    $scope.submitDescription = function(desc){
        $http.put('/user/myinfo/',{'description':desc}).
        success(function(rs){
            if(rs.status == 'success'){
                $scope.user.description = desc
                desc = ''
            }
            
        })
    }
    $scope.updateErrors = {}
    $scope.update_myinfo = function(user){
        $scope.updateErrors = {}
        data = {}
        if($('#female').hasClass('is_selected')){data['gender'] = 'F'}else
        if($('#male').hasClass('is_selected')){data['gender'] = 'M'}else{
            $scope.updateErrors.gender = 'Select Gender'
            return false;
        }
        user['dob'] = picker.get('select', 'dd-mm-yyyy')
        if(user['dob']){
            data['dob'] = user['dob']
        }
        if(user['selected_location_id']){
            data['selected_location_id'] = user['selected_location_id']
        }
        data['description'] = user['description']
        if(user['full_name']){
            data['full_name'] = user['full_name']
        }
        // alert(JSON.stringify(data))
        // return false
        $http.put('/user/myinfo/', data).
        success(function(rs){
            if(rs.status == 'success'){
                $scope.my_profile()
                history.pushState('', '', '#rp_my_profile');
                $('#my_profile').addClass('is_visible')
                $('#my_info').removeClass('is_visible')
                $scope.desc = ''
            }else{
                var error_msg = rs.detail
                // alert(JSON.stringify(error_msg))
                if ('zap_username' in error_msg){
                    $scope.updateErrors.zap_username = error_msg['zap_username']
                }
                if ('description' in error_msg){
                    $scope.updateErrors.description = error_msg['description'][0]
                }
                if ('gender' in error_msg){
                    $scope.updateErrors.gender = error_msg['gender'][0]
                }
                if ('selected_location_id' in error_msg){
                    $scope.updateErrors.state = error_msg['selected_location_id'][0]
                }                
            }
        })
    }
    $scope.my_account = function(){

    }
    $scope.my_preferences = function(){

    }
    $scope.my_interests = function(){
        $http.get('/user/mybrandtags/').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
                $scope.mybrandtags = data.data
            }
        })
        $http.get('/onboarding/2?end=34').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
                $scope.allbrandtags = data.data
            }
        })
    }
    $('body').on('click', '.tag_item', function() {
        $(this).toggleClass('selected')
        var brandTagList = $(".tag_item.selected").map(function() {
            return $(this).data("id");
        }).get();
        $http.post("/onboarding/2",{btags_selected: brandTagList})
    })
    $scope.my_sizes = function(){
        $http.get('/user/mysizes').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
                $scope.mysize = data.data[0].size
                $scope.waist_size = data.data[0].waist_size
                $scope.foot_size = data.data[0].foot_size
            }
        })
        $http.get('/onboarding/4').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
                $scope.allsize = data.data
            }
        })
    }
    $scope.checkValue1 = function(s){
        for(var prop in $scope.mysize){
           if($scope.mysize[prop]['id'] === s.id) return true;
        }
        return false;
    }
    $scope.checkValue2 = function(s){
        for(var prop in $scope.foot_size){
           if($scope.foot_size[prop]['id'] === s.id) return true;
        }
        return false;
    }
    $scope.checkValue3 = function(s){
        for(var prop in $scope.waist_size){
           if($scope.waist_size[prop]['id'] === s.id) return true;
        }
        return false;
    }
    $('body').on('click', '.size_item1', function() {
        $(this).toggleClass('selected')
        var waistSizesList = $(".size_item.waist_sizes.selected").map(function() {
            return $(this).data("id");
        }).get();
        var footSizesList = $(".size_item.foot_sizes.selected").map(function() {
            return $(this).data("id");
        }).get();
        var clothSizesList = $(".size_item.cloth_sizes.selected").map(function() {
            return $(this).data("id");
        }).get();
        $http.post("/onboarding/4",{
                waist_sizes: waistSizesList,
                foot_sizes: footSizesList,
                cloth_sizes: clothSizesList,
        })
    })
    $scope.my_brands = function(){
        $http.get('/user/mybrands?end=300').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
                $scope.brands = data.data
            }
        })
    }
    $('body').on('click', '.follow', function() {
        $(this).toggleClass('selected')
        var selectedBrandList = $(".follow.selected").map(function() {
            return $(this).data("id");
        }).get();
        $http.post("/onboarding/3",{brands_selected: selectedBrandList})
    })
    $scope.add_adrss_btn_text = 'Add Address'
    $rootScope.my_addresses = function(set_selected){
    	$http.get('/address/crud/').
            success(function(data, status, headers, config) {
            if (data.status == "success"){

            	$scope.addrs = data.data
                setTimeout(function(){
                    if(!(set_selected == undefined)){
                        $(".address_item[data-id = "+set_selected+"]").addClass('selected')
                        var el = $(".address_item[data-id = "+set_selected+"]")
                        $('.address').text(el.find('.name .namee').text()+' - '+el.find('.name .phone').text())
                    }
                })
            }
        })
    }
    $scope.add_address = function(backto_checkout){
    	$scope.add_adrss_btn_text = 'Add Address'
    	$scope.a = {}
    	$scope.errors = {}
    	$http.get('/address/get_states/').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
            	$scope.states = data.data
        		setTimeout(function() { $('select').material_select() });
            }
        })
        if(backto_checkout == true){
            $localStorage.backto_checkout = true
        }
        //$('select').material_select();
    }
    $scope.edit_address = function(addrs){
        $scope.add_adrss_btn_text = 'Update Address'
        $scope.errors = {}
        $scope.a = addrs
        $http.get('/address/get_states/').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
                $scope.states = data.data
                setTimeout(function() { 
                    $('select').material_select()
                    $scope.pincodeTyping(addrs['pincode'])
                });
            }
        })
    }
    $scope.save_address = function(){
    	$scope.errors = {}
    	var data = $scope.a
    	data['state'] = $('#state').val()
    	if($scope.add_adrss_btn_text == 'Add Address'){var method = 'POST'}else{var method = 'PUT';data['address_id']=data['id']}
    	$http({
                method: method,
                url: "/address/crud/",
                data: data
            }, console.log($scope.new_pincode)).error(function(response) {
                console.log(response)
            }).then(function successCallback(response) {
                console.log(response)
                // alert(JSON.stringify(response))
                if(response.data.data){
                    $scope.a = {}
                    if($localStorage.backto_checkout){
	    			    $scope.my_addresses(response.data.data['id'])
                        history.pushState('', '', '#rp_checkout');
                        $('#checkout').addClass('is_visible')
                        $('#add_address').removeClass('is_visible')
                        $localStorage.backto_checkout = false
                    }else{
                        $scope.my_addresses()
                        history.pushState('', '', '#rp_my_addresses');
                        $('.right_panel_inner > div').removeClass('is_visible');
                        $("#my_addresses").addClass('is_visible');
                    }
                }else{
                	var error_msg = response.data.detail
	                if ('name' in error_msg){
	                    $scope.errors.name = error_msg['name'][0]
	                }
	                if ('address' in error_msg){
	                    $scope.errors.address = error_msg['address'][0]
	                }
	                if ('city' in error_msg){
	                    $scope.errors.city = error_msg['city'][0]
	                }
	                if ('state' in error_msg){
	                    $scope.errors.state = error_msg['state'][0]
	                }
	                if ('phone' in error_msg){
	                    $scope.errors.phone = error_msg['phone'][0]
	                }
	                if ('pincode' in error_msg){
	                    $scope.errors.pincode = error_msg['pincode'][0]
	                }
                    console.log(JSON.stringify(response.data.detail))
                }
         });
    }
    
    
    $scope.pincodeTyping = function(n){
        if (n.length == 6){
            $http.get('/address/pincode/?pincode='+n)
            .success(function(data){
                if(data.status == 'success'){
                    d = data.data
                    $scope.a.city = d.city
                    for(i in $scope.states){
                        if($scope.states[i]['name'].toLowerCase() === d.state.toLowerCase()){
                            $scope.selected_state = $scope.states[i]['id'].toString();
                            setTimeout(function(){$('select').material_select()});       
                        }
                    }
                    clevertap.event.push("pincode_check", {
                        "pincode_checked":n,
                    });
                }
            })
        }
                                
    }
    $scope.my_notifications = function(){
    	$http.get('/notification/getmynotifs/').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
            	$scope.mynotif = data.data
            	// console.log(data.data)
            }
        })
    }
    $scope.readNotification = function(notif){
        if(notif.action == 'comment'){
            $localStorage.showcomment = true
        }
        $http.post('/notification/readnotif',{'notif_id':notif.id})
    }
    $scope.my_wallet = function(){
    	$http.get('/extra/appvirality/campaign').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
            	$scope.mywallet = data.data
            	console.log(data.data)
            }
        })
    }
 
    $scope.add_bank_account = function(){

    }
    $scope.bk = {}
    $scope.save_bank_account = function(){
    	$scope.errors = {}
    	$http({
            method: 'POST',
            url: "user/accountnumber/",
            data: {
                'account_number': $scope.bk.user_acc,
                'ifsc_code': $scope.bk.ifsc_code,
                'account_holder': $scope.bk.account_holder
            }
        }).then(function successCallback(response) {
            if(response.data.status == 'success'){
            	$scope.my_bank_account()
    			$("[data-activates=#my_bank_account]").click();
    			history.pushState('', '', '#rp_my_bank_account');
                
            }else{
            	var error_msg = response.data.detail
            	if ('account_holder' in error_msg){
            		$scope.errors.account_holder = error_msg['account_holder'][0]
            	}
                if ('account_number' in error_msg){
                    $scope.errors.account_number = error_msg['account_number'][0]
                }
                if ('ifsc_code' in error_msg){
                    $scope.errors.ifsc_code = error_msg['ifsc_code'][0]
                }
                //alert(JSON.stringify(response.data.detail))                    
            }
        });
    }
    $scope.my_bank_account = function(){
    	$http.get('/user/accountnumber/').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
            	$scope.bankAC = data
            	console.log(data)
            }
        })
    }
    $rootScope.my_orders = function(){
    	$http.get('/user/myorders/').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
            	$scope.myorders = data.data.data
            	console.log(data)
            }
        })
    }
    $scope.order_details = function(id,from_page){
    	if(!id){
            $("[data-activates=#my_orders]").click();
            $($('#order_details_page_back_btn').attr('data-activates')).addClass('is_visible');
            setTimeout(function(){$('#order_details').removeClass('is_visible');})
			history.pushState('', '', '#rp_my_orders');
			$scope.my_orders()
			return false;
    	}else{
	    	$http.get('/order/details/'+id).
	            success(function(data, status, headers, config) {
	            if (data.status == "success"){
                    $scope.currentOrder = id;
	            	$scope.order = data.data
                    $scope.order = data.data
                    if($scope.order.rating) {
	            		$scope.rating = parseInt($scope.order.rating)
	            	} else {
	            		$scope.rating = false
	            	}
	            	console.log(data)
	            }
	        })
        }
    	if(from_page == 'sale_page'){
			var logObj = $("#order_details_page_back_btn")
            logObj.attr('data-activates','#my_sales')
            logObj.attr('href','#rp_my_sales')
    	}else{
    		var logObj = $("#order_details_page_back_btn")
            logObj.attr('data-activates','#my_orders')
            logObj.attr('href','#rp_my_orders')
    	}
    }
    $scope.my_sales = function(){
    	$http.get('/user/mysales/').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
            	$scope.mysales = data.data
            	console.log(data)
            }
        })
    }
    $scope.setFocus = function(){
    	setTimeout(function() { $("#search_box").focus(); });
    }
    $rootScope.USER_ID = USER_ID
    $scope.my_admiring = function(){
        $http.put('/user/admire/',{'user_id':USER_ID,'admire_type':'admiring'})
        .success(function(rs){
            $scope.admirings = rs.data
        })
    }
    $scope.my_admirers = function(){
        $http.put('/user/admire/',{'user_id':USER_ID,'admire_type':'admires'})
        .success(function(rs){
            $scope.admirers = rs.data
        })
                    
    }
    var typingTimer; 
    var doneTypingInterval = 300;
    var $input1 = $('#search_box');
    $input1.on('keyup', function () {
      clearTimeout(typingTimer);
      typingTimer = setTimeout(doneTyping, doneTypingInterval);
    });
    $input1.on('keydown', function () {
      clearTimeout(typingTimer);
    });
    function doneTyping() {
        $('#searchBox').addClass('listing_spinner')
        $scope.search_suggestions()
    }

    var s_tab = 'product'
    $scope.search_suggestions = function(tab){
    	setTimeout(function() { $("#search_box").focus(); });
        if(tab == 'product' || tab == 'closet'){
            s_tab = tab
        }
        if(s_tab == 'product'){
            if($scope.use_suggestion_flag){
                if ($scope.search_key.substring(0, $scope.use_suggestion_string.length) === $scope.use_suggestion_string)
                {
                    var key = $scope.search_key.substring($scope.use_suggestion_string.length)
                    if(!key){
                        $scope.suggestions = []
                        $scope.$apply()
                        return false;
                    }
                    $scope.search_use_suggestion(key)
                }else
                {
                    $scope.search_key = ''
                    $scope.use_suggestion_flag = false
                    $scope.$apply()
                }
                return false;
            }
        }
        if(!$scope.search_key){
            if(s_tab == 'product'){$scope.pInit = false;}else{$scope.uInit = false;}
            $scope.suggestions = []
            $scope.$apply()
            return false;
        }
    	$http({
            method: 'POST',
            url: "/search/suggestions/"+s_tab,
            data: {
                perpage : 2,
                query_string: $scope.search_key,
                filter : {
		          "Category": [],
		          "Style": [],
		          "Color": [],
		          "Occasion": [],
		          "Brand": [],
		          "SubCategory": [],
		          "string": ""
		        },
            }
        }).then(function successCallback(response) {
            if(s_tab == 'product'){$scope.pInit = true;}else{$scope.uInit = true;}
            $scope.suggestions = response.data.data
            // alert(JSON.stringify($scope.suggestions))
            console.log(response)
            // if(!$scope.$$phase) {
            //     $scope.$apply()
            // }
        })
    		
    }
    $scope.pInit = false
    $scope.uInit = false
    $scope.useSuggestion = function(obj){
        $scope.search_key = obj.string
        setTimeout(function() { $("#search_box").focus(); });
        $scope.use_suggestion_flag = true
        $scope.use_suggestion_obj = obj
        $scope.use_suggestion_string = obj.string.substring(0,obj.string.length-1)
    }
    $scope.search_use_suggestion = function(query_string){
        if(query_string){
        	$http({
                method: 'POST',
                url: "/search/suggestions/product",
                data: {
                    query_string: query_string,//$scope.search_key,
                    filter : $scope.use_suggestion_obj,
                }
            }).then(function successCallback(response) {
                $scope.suggestions = response.data.data
            })
        }
    }
    String.prototype.rtrim = function () {
        return this.replace(/((\s*\S+)*)\s*/, "$1");
    }
    $scope.searchFilter = function(filter){
        // alert(JSON.stringify(filter));
        // var str = filter.string.replace(/ /g,'+')
        // window.history.pushState('', '', '/buy?search='+str.rtrim()+getSuggestedQuery(filter))
        window.history.pushState('', '', '/buy?'+getSuggestedQuery(filter))
        location.reload();
    }
    $scope.search = function(){

    }
    $scope.searchSuggestion = function(key){       
        if($scope.use_suggestion_flag){
            var str = $scope.search_key.substring($scope.use_suggestion_string.length+1)
            window.history.pushState('', '', '/buy?search='+str.replace(/ /g,'+')+getSuggestedQuery($scope.use_suggestion_obj))
        }else{
            window.history.pushState('', '', '/buy?search='+key.replace(/ /g,'+'))
        }
        location.reload();
    }
    $('#search_box').keypress(function (e) {
        if (e.which == '13' && $scope.search_key) {
            $scope.searchSuggestion($scope.search_key); 
        }
    });

    $scope.cartLoader = true
    $rootScope.cart = function(){
        $scope.cartLoader = true
        $scope.cartTotalOffline = 0
        if(ZL == 'True'){
            $http.get('/zapcart/').
                success(function(data) {
                if (data.status == "success") {
                    $scope.carts = data.data
                    $scope.cartLoader = false
                    getOffers($scope.carts);
                }
            })
        }else if($localStorage.tote){
            var total = 0
            var cart_data = $localStorage.tote['cart_data']
            $http.post('/zapcart/quantity_availablity/',cart_data).
            success(function(rs){
                $scope.carts = rs.data
                $scope.cartLoader = false
                getOffers($scope.carts);
            })
        }else {
            $scope.cartLoader = false
        }
    }
    function getOffers(carts) {
        for (i in $scope.carts.items) {
            $http.get('/catalogue/offers/'+($scope.carts.items[i].product_id || $scope.carts.items[i].product)).success(function(response){
                if(response.status == 'success'){
                    $scope.carts.items[i]['offers'] = response.data;
                }
            });
        }
    }
    $scope.removeCartItem = function(item){
        if(item['quantity_available'] >= item['product_quantity']){
            $scope.itemToRemove = item
            $('#confirm_remove_item').addClass('is_visible')
            return false
        }
        $scope.removeSoldout(item)
    }
    $scope.removeSoldout = function(item){
        if(!item){
            item = $scope.itemToRemove
            $('#confirm_remove_item').removeClass('is_visible')
        }
        if(ZL == 'True'){
            $http.delete('/zapcart/',{params: {item_id: item.id}}).
                success(function(data) {
                if (data.status == "success"){
                    $scope.carts = data.data
                    $('.cart_btn').removeClass('is_hidden')
                    $('.goto_btn').addClass('is_hidden')
                    $('#toteBadge').text(data.data.items.length)
                    clevertap.event.push("remove_from_tote", {
                        "user_id":USER_ID,
                        "product_id":item.product_id,
                        "size":item.product_size,
                        "quantity":item.product_quantity,
                        "price":item.listing_price,
                    });
                }
            })
        }else{
            $scope.carts.items.splice($scope.carts.items.indexOf(item),1)
            $scope.carts.total_listing_price = $scope.carts.total_listing_price - item.listing_price
            var cart_data = $localStorage.tote['cart_data']
            for (i in cart_data){
                if(cart_data[i]['id'] == item.id){
                    $localStorage.tote['cart_data'].splice(i, 1)
                    $('#toteBadge').text($localStorage.tote['cart_data'].length)
                    return false;
                }
            }

        }
    }
    $scope.closeRemoveSoldoutPopup = function(){
        $('#confirm_remove_item').removeClass('is_visible')
    }
    // $rootScope.getSavedCards = function(){
    //     $http.get('/user/mysavedcards/').
    //         success(function(data) {
    //         if (data.status == "success"){
    //             $scope.savedCards= data.data.paymentOptions
    //         }
    //     })
    // }
    $rootScope.getZapCash = function(){
        $http.get('/zapcart/checkout/').
            success(function(data) {
            if (data.status == "success"){
                $scope.zapcash= data.data.zap_cash
            }
        })
    }
    $scope.removeSoldoutItem = function(){
        for(i in $scope.itemsToRemove){
            $http.delete('/zapcart/',{params: {item_id: $scope.itemsToRemove[i]}}).
                success(function(data) {
                if (data.status == "success"){
                    $scope.carts = data.data
                    $('.cart_btn').removeClass('is_hidden')
                    $('.goto_btn').addClass('is_hidden')
                    $('#toteBadge').text(data.data.items.length)
                }
            })
            
        }
        $('#sold_out_cart').removeClass('is_visible')
        $scope.itemsToRemove = []
    }
    $scope.itemsToRemove = []
    $scope.checkout = function(){
        $scope.itemsToRemove = []
        if(ZL == 'True'){
            $scope.order_id = ''
            setTimeout(function(){
                $http.get('/zapcart/').
                success(function(data) {
                    if (data.status == "success"){
                        $scope.carts = data.data
                        cart_id = data.data.cart_id
                        // if(!$scope.$$phase) {
                        //     $scope.$apply()
                        // }
                        var items = $scope.carts['items']
                        if(!items.length){
                            $('#cart').addClass('is_visible')
                            $('#checkout').removeClass('is_visible')
                            window.history.pushState('', '', '#rp_cart')
                            return false;
                        }
                        for(var i in items){
                            if(items[i]['quantity_available'] < items[i]['product_quantity']){
                                $scope.itemsToRemove.push(items[i]['id'])
                            }
                        }
                        if($scope.itemsToRemove.length){
                            $('#cart').addClass('is_visible')
                            $('#checkout').removeClass('is_visible')
                            $('#sold_out_cart').addClass('is_visible')
                            window.history.pushState('', '', '#rp_cart')
                            return false;
                        }else{
                            $('.right_panel_inner > div').removeClass('is_visible');
                            $('#checkout').addClass('is_visible');
                            $('.right_panel').addClass('is_visible');
                            window.history.pushState('', '', '#rp_checkout')
                            // $(".accordion_item").removeClass("open");
                            // $("#order_review").addClass("open");
                            // $("#checkout").removeClass("step_2").addClass("step_1");
                            $('#order_review h6.title').click()
                            $scope.getZapCash()
                            $scope.my_addresses()
                            // $scope.getSavedCards()
                            // $scope.get_accesskey_vanity();
                            cleverTapCheckout(1)
                        }
                    }
                })
            })
        }else{
            setTimeout(function(){
                $scope.$emit('setLoginPurpose', 'continue with the purchase' );
                $('.right_panel_inner > div').removeClass('is_visible');
                $('#login_options').addClass('is_visible');
                $('.right_panel').addClass('is_visible');
                
            })
        }
    }

    $scope.backToCart = function(){
        if ($scope.order_id){
            swal({
                  title: "Cancel transaction?",
                  // text: "You will not be able to recover this imaginary file!",
                  type: "warning",
                  showCancelButton: true,
                  confirmButtonColor: "#DD6B55",
                  confirmButtonText: "Yes",
                  cancelButtonText: "No",
                  closeOnConfirm: true,
                  closeOnCancel: true
                },
                function(isConfirm){
                  if (isConfirm) {
                    $http.put("/order/juspay_order", {'order_id':$scope.order_id})
                    $('#cart').addClass('is_visible')
                    $('#checkout').removeClass('is_visible')
                    window.history.pushState('', '', '#rp_cart')
                  } 
                  else {
                    window.history.pushState('', '', str.split('/#')[0])    
                  }
                });
            // swal({
            //   title: "Cancel transaction?",
            //   // text: "You will not be able to recover this imaginary file!",
            //   type: "warning",
            //   showCancelButton: true,
            //   confirmButtonColor: "#DD6B55",
            //   confirmButtonText: "Yes",
            //   closeOnConfirm: true
            // },
            // function(){
            //     window.history.pushState('', '', str.split('/#')[0])    
            //     $http.put("/order/juspay_order", {'order_id':$scope.order_id})
            // });
        }else{
            $('#cart').addClass('is_visible')
            $('#checkout').removeClass('is_visible')
            window.history.pushState('', '', '#rp_cart')
        }
    }
    // $scope.card_details = function(){
        
    // }
    $scope.enableCOD = function(){
        $scope.cod = true;
    }
    // $rootScope.get_accesskey_vanity = function(){
    //     $http({
    //         method: 'GET',
    //         url: "/payment/get_accesskey_vanity/",
    //     }).then(function successCallback(response) {
    //         if(response.data.status == 'success'){
    //             $scope.accessKey = response.data.data.access_key
    //             $scope.vanityUrl = response.data.data.vanity_url
    //             $scope.citrus_env = response.data.data.citrus_env
    //             CitrusPay.Merchant.Config = {
    //                 // Merchant details
    //                 Merchant: {
    //                     accessKey: $scope.accessKey, //Replace with your access key
    //                     vanityUrl: $scope.vanityUrl  //Replace with your vanity URL
    //                 }
    //             };
    //             if($scope.citrus_env == 'PRODUCTION')
    //                 { CitrusPay.Config.setEnv('PRODUCTION') }
    //             fetchPaymentOptions();
    //         }
    //         if(response.data.status == 'error'){
    //         }
            
    //     }, function errorCallback(response) {

    //         //alert(JSON.stringify(response.data))

    //     });             
    // }
    // $scope.netBankingOptions = function(optons){
    //     $scope.netBankOptions = optons
    //     setTimeout(function() { $('select').material_select() });
    // }

	var str = window.location.href
	if(ZL == 'True' && str.indexOf('/#') >  -1){
		var rp_str = str.split('#')[str.split('#').length-1]
		var tab = rp_str.replace('rp_', "");
        try{
            $scope[tab]();
    		$('.right_panel').addClass('is_visible');
            $('#'+tab).addClass('is_visible')
        }catch(err) {
            var t = tab.split('/')
            if((t[1]=='product' || t[1]=='profile') && t[2]!=undefined){
                window.location.href = t[1]+'/'+t[2];
            }else if(t[1] == 'feeds' || t[1] == 'discover' || t[1] == 'sell'){
                window.location.href = "/"+t[1];
            }else{
                console.log('url mismatch')
            }
            
        }
		// $('#'+tab).addClass('is_visible')
		
	}else if(ZL == 'False' && str.indexOf('/#') >  -1){
        var tab = str.split('/#rp_')[1]
        if(tab=='search'){
            $('#search').addClass('is_visible');
            setTimeout(function() { $("#search_box").focus(); });
        }else if(tab=='cart'){
            $('#cart').addClass('is_visible');
            $scope.cart()
        }else{
            window.history.pushState('', '', '#rp_login_options')
            $('#login_options').addClass('is_visible');
        }
        $('.right_panel').addClass('is_visible');
    }
	$scope.logout = function() {
        $.get('/account/logout/', function(data){
            clevertap.logout();
            location.reload();
   //          ZL = 'False'
   //          $('.right_panel_inner > div').removeClass('is_visible');
			// $('#login_options').addClass('is_visible');
			// window.history.pushState('', '', '#login_options')
			// var logObj = $('.login_label')
			// logObj.html('Login')
			// logObj.removeAttr('ng-click')
   //          logObj.attr('data-activates','#login_options')
   //          logObj.attr('href','#rp_login_options')
        })
    }
    $scope.signin = function(){
        $scope.loginError = {}
    	$http({
            method: 'POST',
            url: "/account/login/",
            data: {
                email: $scope.email,
                password: $scope.pwd,
                logged_device: "website",
                logged_from: "zapyle"
            }
        }).then(function successCallback(response) {
            if(response.data.status=="success"){
                window.history.pushState('', '', window.location.href.split('#')[0]+'#rp_my_profile')
                // alert('logged')
                location.reload()
    //             alert('reloded')
    //             $scope.my_profile()  
    //             ZL = 'True'
    //             window.history.pushState($(this).attr('data-activates'), $(this).attr('data-activates'), '#my_profile')
				// $('#my_profile').addClass('is_active');
				// $('.right_panel_inner > div').removeClass('is_visible');
				// $('#my_profile').addClass('is_visible');
				// $('.right_panel').addClass('is_visible');
            }else{
            	var error_msg = response.data.detail
                if (typeof error_msg == 'string'){
                    $scope.loginError.email = error_msg
                }else{
                    if ('email' in error_msg){
                        $scope.loginError.email = error_msg['email'][0]
                    }
                    if ('password' in error_msg){
                        $scope.loginError.password = error_msg['password'][0]               
                    }
                }
            }
        })
    }
    $scope.signup = function(){
    	$scope.errors = {}
        $http({
            method: 'POST',
            url: "/account/signup/",
            data: {
                zap_username: $scope.zapusername,
                email: $scope.email,
                password: $scope.password,
                confirm_password: $scope.password,
                phone_number: $scope.phone,
                first_name: $scope.name,
                logged_device: "website",
            }
        }).then(function successCallback(response) {
            if(response.data.status=="success"){
                window.history.pushState('', '', window.location.href.split('#')[0]+'#rp_my_profile')
                location.reload()
    //         	$scope.my_profile()  
    //             window.history.pushState($(this).attr('data-activates'), $(this).attr('data-activates'), '#my_profile')
				// $('#my_profile').addClass('is_active');
				// $('.right_panel_inner > div').removeClass('is_visible');
				// $('#my_profile').addClass('is_visible');
				// $('.right_panel').addClass('is_visible');
			}else{
    			var error_msg = response.data.detail
                if ('zap_username' in error_msg){
                    $scope.errors.username = error_msg['zap_username'][0]
                }
                if ('email' in error_msg){
                    $scope.errors.email = error_msg['email'][0]
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
            }
        })
    }
    $rootScope.setZapCash = function(used){
        if(used){
            $('.check_box').addClass('is_selected')
            $scope.zapcash_used = used  
            $scope.zapcash-=used  
            // if(!$scope.$$phase) {
            //     $scope.$apply()
            // }
        }
    }
    $scope.zapcash = 0
    $scope.zapcash_used = 0
    $('.check_box').click(function(){
        if(!$(this).hasClass('is_selected')){
            if($scope.zapcash > $scope.carts.total_listing_price){
                $scope.zapcash_used = $scope.carts.total_listing_price   
                $scope.zapcash-=$scope.carts.total_listing_price             
            }else{
                $scope.zapcash_used = $scope.zapcash
                $scope.zapcash = 0
            }
        }else{
            $scope.zapcash = $scope.zapcash_used
            $scope.zapcash_used = 0
        }
        $scope.$apply()
    })

    $('body').on('click', '.star_item', function () {
        $scope.rating = parseInt($(this).data('rating'));
        $scope.$apply();
        setTimeout(function () {
            // var order = $('#order_info').data('orderid');
            $http.post('/order/rate_order', {order_id:$scope.currentOrder, rating: $scope.rating}).
            success(function(rs){
                $('.rating_response').removeClass('is_hiddden');
            })
        })

    });

    $('.close_right_panel').click(function(){
    	$('.right_panel').removeClass('is_visible')
    	window.history.pushState('', '', window.location.href.split('#')[0])
    })

    $scope.citrusClientErrMsg = function(){
        $("#cnf_btn").text('Proceed to Payment')
        $scope.loader = false
        cnf_btn_frst_clk = true
        $http.put('/payment/confirmorder/website/',{'TxId':$scope.citrus_var.merchantTxnId})
    }
    $('body').on('click', '#delivery_address_cta', function() {
        if(!$scope.addrs){
            Materialize.toast("Add Delivery Address", 3000);
            return false
        }
        if(!($('.address_item').hasClass('selected'))){
            Materialize.toast("Select the delivery address", 3000);
            // closeAccordion($('.step.open h6.title'));
            // openAccordion($('#delivery_address h6.title'));
            // $('#delivery_address h6.title').attr('class', 'is_visible step_2');
            return false;
        }
        $('#checkout').attr('class', 'is_visible step_3');
        closeAccordion($('.step.open h6.title'));
        $('.address').addClass('is_visible')
        openAccordion($('#payment_options h6.title'));
        cleverTapCheckout(3)
    });
    $('body').on('click', '.address_item', function(){
        $('.address').text($(this).find('.name .namee').text()+' - '+$(this).find('.name .phone').text())
    })
    $('body').on('click', '.saved_card_item', function(){
        $('.saved_cards_list').find('.saved_card_item input').removeAttr('checked');
        $(this).find('input').first().prop('checked',true);
        $('#cvv').addClass('is_visible');
        $('#cvv input').val('').focus()
        $(".PayFromWallet").prop("id", "citrusWalletCardPayButton");
    })
    $('#cvv .close_btn').click(function(){
        $('.saved_card_item').removeClass('selected')
    })
    $('body').on('click', '.rp_trigger.icon-heart_empty', function () {
        $scope.$emit('setLoginPurpose', 'see your loves list' );
    });

    function juspay_create_order_api(cod){
        var data = {
            'address_id': $('.address_item.selected').data('id'),
            'apply_zapcash': $scope.zapcash_used, 
        }
        if(cod == true){
            data['cod'] = true
        }
        console.log(JSON.stringify(data))
        $scope.order_id = "juspay on processing";
        if(!$scope.$$phase) {
            $scope.$apply()
        }
        $http.post("/order/juspay_order", data).success(function(rs){
            console.log(JSON.stringify(rs))
            if(rs.status == "success"){
                if(rs.data.message == 'TXFWD'){
                    $scope.iframe_url = rs.data.iframe;
                    $("#iframe").html("<iframe src='"+rs.data.iframe+"'></iframe>"); 
                    $scope.order_id = rs.data.order_id;
                    if(!$scope.$$phase) {
                        $scope.$apply()
                    }
                }else{
                    window.history.pushState('', '', '/order/' + rs.data.order_id);
                    location.reload(); 
                }
            }else{
                Materialize.toast(rs.detail, 3000);
                if(rs.detail == 'Please add items to your cart. Cart is empty now.'){
                    window.history.pushState('', '', '#rp_cart')
                    location.reload();  
                }
            }
        })
    }
    $rootScope.juspayOrder = function(cod){
        if(!($('.address_item').hasClass('selected'))){return false;}
        if ($scope.order_id){
            $http.put("/order/juspay_order", {'order_id':$scope.order_id}).success(function(rs){
                if(rs.status == "success"){
                    juspay_create_order_api(cod);
                }
            })
        }else{
            juspay_create_order_api(cod);
        }
        
    }

    $scope.codOrder = function(){
        $('#cod_modal').openModal();
        return false;
    }
    $('#codConfirm').click(function(){
        $scope.juspayOrder(true);   
    })

    $('body').on('click', '#payment_options h6.title', function() {
        if(!($('.address_item').hasClass('selected'))){
            Materialize.toast("Please select the delivery address", 3000);
            return false;
        }else{
            $scope.juspayOrder();
            $('#checkout').attr('class', 'is_visible step_3');
            closeAccordion($('.step.open h6.title'));
            openAccordion($('#payment_options h6.title'));
            cleverTapCheckout(3)
        }
    });

    var cnf_btn_frst_clk = true
    $scope.confirmOrder = function() {
        if(!cnf_btn_frst_clk){return false;}
        console.log(new Date())
        console.log('---------------')
        // var bankName = jQuery('#citrusAvailableOptions option:selected').text();
        //     var bankCode = jQuery('#citrusAvailableOptions').val();
        //     alert(bankName+'---'+bankCode)

        //     return false
            if(!$scope.addrs){
                Materialize.toast("Please add address", 3000);
                return false
            }
            if(!($('.address_item').hasClass('selected'))){
                Materialize.toast("Please select the delivery address", 3000);
                closeAccordion($('.step.open h6.title'));
                openAccordion($('#delivery_address h6.title'));
                // $('#delivery_address h6.title').attr('class', 'is_visible step_2');
                return false;
            }
            // $scope.address_id = $('.address-card.is_selected').attr('select-card')
            // if(!$scope.address_id){alert("Select Delivery Address");return false;}
            // $("#paynow_button").text('PLEASE WAIT')
            // $("#paynow_button").prop('disabled', true)
            // if($scope.final_price > 0){
                //  if($scope.flag == 4){
                //     if(!$(".PayFromWallet").attr("id")){
                //         alert("Please select any saved card")
                //         $("#paynow_button").text('Pay Now')
                //         $("#paynow_button").prop('disabled', false)
                //         return false
                //     }else{
                //         if(!$('#CitrusMembercvv'+$scope.selected_id_for_all).val()){
                //             alert("Please enter CVV")
                //             $("#paynow_button").text('Pay Now')
                //             $("#paynow_button").prop('disabled', false)
                //             return false
                //         }
                //     }
                // }
            // }
            if($('.saved_cards_list > li').hasClass('selected')){
                if(!$('#cvv input').val()){
                    $('#cvv').addClass('is_visible');
                    $('#cvv input').val('').focus()
                    return false
                }
            }else 
            if($scope.netBankSelected){}else
            if($('#credit').hasClass('selected')){}else
            if($('#debit').hasClass('selected')){}else
            if($('#cod').hasClass('selected')){}
            else{
                Materialize.toast("Select a payment option.", 3000);
                return false;
            }
            $scope.confirm_email_num()
        }
        $scope.confirm_email_num = function(){

            $http({
                method: 'GET',
                url: "/user/get_email_and_num/",
            }).then(function successCallback(response) {
                if (response.data.status=="success"){
                    $scope.confirm_email = response.data.data.user_detail.email
                    $scope.confirm_number = response.data.data.user_detail.phone_number
                    $scope.confirm_zap_username = response.data.data.user_detail.zap_username
                    $scope.phone_number_verified = response.data.data.user_detail.phone_number_verified
                    if($scope.confirm_email && $scope.confirm_zap_username){
                        if($scope.phone_number_verified==false){
                            Materialize.toast('error phone', 3000);
                            $scope.phone_model= true
                            $scope.error_msg_phone = {}
                            return false
                        }
                        $scope.postData()
                        return false
                    }else{
                        Materialize.toast('error zapusername or phone', 3000);
                        $scope.modal_phone_pop = true
                        $scope.errors_confirm = {}
                        return false
                    }
                    $("#paynow_button").text('Pay Now')
                    $("#paynow_button").prop('disabled', false)

                    return false
                }else{
                    Materialize.toast('Sorry, please try later.', 3000);
                    // $scope.postData()
                }
            }, function errorCallback(response) {
                
            }); 
        }
        $scope.postData = function(){
            // $scope.otp_final_pop = false
            // $scope.phone_model = false
            if($('#credit').hasClass('selected')){
                 if(!$scope.check_card_fields()){
                    Materialize.toast('Please enter card number, cvv, expiry.', 3000);
            //         $("#paynow_button").text('Pay Now')
            //         $("#paynow_button").prop('disabled', false)                    
                     return false
                }
                $('#citrusCardType').val("debit");

            }else if($('#debit').hasClass('selected')){
                if(!$scope.check_card_fields()){
            //         $("#paynow_button").text('Pay Now')
            //         $("#paynow_button").prop('disabled', false)
                    Materialize.toast('Please fill all the fields in card.', 3000);
                    return false
                }
                $('#citrusCardType').val("credit");
            }
            
            if($('#cod').hasClass('selected')){
                $('#cod_modal').openModal();
                return false;
                // if(confirm("Are you sure you want to place the order?")){
                //     data['cod'] = true
                // }else{
                //     Materialize.toast('cancelled', 3000);
                //     return false
                // }
            }
            $scope.postDataApi()
        }
        
        $scope.loader = false
        // $scope.postDataApi = function(cod){
        //     // alert(cod)
        //     var data = {
        //         'address_id': $('.address_item.selected').data('id'),
        //         'apply_zapcash': $scope.zapcash_used, 
        //     }
        //     if(cod){
        //         data['cod'] = true
        //     }
        //     cnf_btn_frst_clk = false
        //     $("#cnf_btn").text('PLEASE WAIT')
        //     $scope.loader = true
            
        //     $http({
        //         method: "POST",
        //         url: '/payment/confirmorder/website/',
        //         data: data,
        //         }).success(function(rs) {
        //             console.log(rs)
        //             //alert(JSON.stringify(rs))
        //             if(rs.status=='success'){
        //                 if(rs.data.message=='TXSUCCESS'){
        //                     window.location.href = "/order/"+rs.data.transaction_id;
        //                 }else if(rs.data.message=='TXFWD'){
        //                     $scope.citrus_var = rs.data
        //                     $scope.get_my_email_and_num()
        //                     //alert('going to bank'+JSON.stringify(document.getElementById("citrusCardPayButton")))
                            
        //                 }
        //             }else{
        //                 $("#cnf_btn").text('Proceed to Payment')
        //                 $scope.loader = false
        //                 Materialize.toast(rs.detail, 3000);
        //                 cnf_btn_frst_clk = true
        //                 if($('#cod').hasClass('selected')){
        //                     $http.put('/payment/confirmorder/website/',{'TxId':$scope.citrus_var.merchantTxnId})
        //                 }
        //                 return false;
        //             }
                    
        //         })
        // }
        // $scope.get_my_email_and_num = function(){
        //     $http({
        //         method: 'GET',
        //         url: "/user/get_my_email_and_num/",
        //     }).then(function successCallback(response) {
        //         if (response.data.status=="success"){
        //             $scope.user_detail = response.data.data.user_detail
        //             setTimeout(function () {
        //                 $scope.zapMakePayment()
        //             }, 10)
        //         }else{
        //             Materialize.toast(response.data.detail, 3000);
        //             $("#cnf_btn").text('Proceed to Payment')
        //             $scope.loader = false
        //             cnf_btn_frst_clk = true
        //         }
        //     }, function errorCallback(response) {
        //         Materialize.toast("Sorry, Payment cannot be proceed now.Please try later.", 3000);
        //     });
        // }
        // $scope.zapMakePayment = function(){
        //     if($('.saved_cards_list > li').hasClass('selected')){
        //         console.log('saved selected')
        //         if($(".PayFromWallet").attr("id") == "citrusWalletCardPayButton"){
        //             console.log('here')
        //             makePayment("card", true)
        //         }else{
        //             makePayment("netbanking", true)
        //         }
        //         // makePayment("card", true)
        //     }else if($('.popular_banks_list > li').hasClass('selected') || jQuery('#citrusAvailableOptions').val()){
        //         console.log('netbanking')
        //         makePayment("netbanking")
        //     }else if($('#credit').hasClass('selected')){
        //         //alert('credit card selected')
        //         console.log('credit card selected')
        //         makePayment("card")
        //     }else if($('#debit').hasClass('selected')){
        //         console.log('debit card selected')
        //         makePayment("card") 
        //     }else{
        //          Materialize.toast("Select a payment option.", 3000);
        //          $("#cnf_btn").text('Proceed to Payment')
        //          $scope.loader = false
        //          cnf_btn_frst_clk = true
        //     }
        // }
        // $scope.changeNetBankingOptions = function(value){
        //     $scope.netBankSelected = value
        //     $('.screen_footer').addClass('net_banking').removeClass('card_cta')
        //     if(!$scope.$$phase) {
        //         $scope.$apply()
        //     }
        //     setTimeout(function() { $('select').material_select() });
        //     $('.popular_bank_item.selected').removeClass('selected')
        //     $('#payment_options .selectable').siblings().removeClass('selected');
        // }
        // $('body').on('click', '#payment_options .selectable', function() {
        //     $(this).siblings().removeClass('selected');
        //     $scope.selectedNetBank = ''
        //     $scope.changeNetBankingOptions($(this).data('bankcode'))
        // });
        // $('body').on('click', '#cod', function() {
        //     $('iframe #common_pay_btn').click()
        // });
        
        // $scope.cardValidation = function(){
        //     Materialize.toast($scope.card, 3000);
        //     // alert(JSON.stringify($scope.card))
        // }
        // $('body').on('click', '.popular_bank_item', function() {
        // })
        $scope.card = {}
        $scope.check_card_fields = function(){
            if (!($scope.card.cardNumber && $scope.card.name && $scope.card.month && $scope.card.year && $scope.card.cvv)){      
                return false
            }else{
                return true
            }
        }
        $rootScope.overlay = function(page){
            $http.get('/notif/overlay/'+page)
            .success(function(data) {
                if(data.status == 'success'){
                    $scope.overlayData = data.data
                    setTimeout(function() { 
                        $('.automated.overlay').addClass('is_visible')
                    },data.data.delay);
                }
            })
        }
        $rootScope.$on('setLoginPurpose', function (event, args) {
            $scope.loginPurpose = args
            if(!$scope.$$phase) {
                $scope.$apply()
            }     
        });
        $scope.loginPurpose = ''
        $scope.admire = function(data){
            if(ZL == 'True'){
                if (data.admired){
                    admireService.postadmire(data.user_id,'unadmire');
                }
                else{
                    admireService.postadmire(data.user_id,'admire');
                }
                data.admired = ! data.admired
            }else{
                $scope.$emit('setLoginPurpose', 'admire a user' );
                $('.right_panel_inner > div').removeClass('is_visible');
                $($('.login_label').attr('data-activates')).addClass('is_visible');
                $('.right_panel').addClass('is_visible');
            }
        }
        $('.right_panel > .glass, .right_panel_inner > .close_btn').click(function() {
            var str = window.location.href
            if ((str.split('/#')[1] == "rp_checkout" || str.indexOf('/order/')!=-1) && $scope.order_id){
                swal({
                  title: "Cancel transaction?",
                  // text: "You will not be able to recover this imaginary file!",
                  type: "warning",
                  showCancelButton: true,
                  confirmButtonColor: "#DD6B55",
                  confirmButtonText: "Yes",
                  cancelButtonText: "No",
                  closeOnConfirm: true,
                  closeOnCancel: true
                },
                function(isConfirm){
                  if (isConfirm) {
                    window.history.pushState('', '', str.split('/#')[0])    
                    $http.put("/order/juspay_order", {'order_id':$scope.order_id})
                    $scope.order_id = '';
                  } else {
                    $('.right_panel').addClass('is_visible');
                  }
                });
            }else{
                window.history.pushState('', '', str.split('/#')[0])
            }
        });
        $scope.insta_login = function(){
            window.location.href = "/account/instagram/" 
        }  
        $scope.errors = {}
        $scope.onboardingStep = 2
        $scope.submitUsername = function(){
            $http({
                method: 'POST',
                url: '/onboarding/1/',
                data : $scope.user1
            }).then(function successCallback(response) {
                if (response.data.status == "success"){
                    ZL = 'True'
                    USER_NAME = $scope.user1['zap_username']
                    $scope.user['zap_username'] = USER_NAME
                    $('.login_label').html(USER_NAME)
                    var gender_val = 'F'
                    if($('#onboarding1').hasClass('is_selected')){gender_val = 'F'}else{gender_val = 'M'}
                    $http.put('/user/myinfo/', {'gender':gender_val})
                    $scope.onboardingStep = 2
                    $('#my_interests').addClass('is_visible')
                    $('#my_profile').removeClass('is_visible')
                    $scope.my_interests()
                }else{
                    $scope.errors = response.data.detail
                    // alert(JSON.stringify($scope.errors))
                }
            })
        }
        $scope.submitBTags = function(){
            $('#my_interests').removeClass('is_visible')
            $('#my_brands').addClass('is_visible')
            $scope.onboardingStep = 3
            $scope.my_brands()
        }
        $scope.submitBrands = function(){
            $('#my_brands').removeClass('is_visible')
            $('#my_sizes').addClass('is_visible')
            $scope.onboardingStep = 4
            $scope.my_sizes()
        }
        $scope.checkUsername = function(){
            $http({
                method: 'POST',
                url: '/user/check_username/',
                data: {
                'zap_username': $scope.user1['zap_username'],
                },
            }).then(function successCallback(response) {
                // alert(JSON.stringify(response))
                if(response.data.status == 'error'){
                    $scope.errors = response.data.detail
                }else{
                    $scope.errors = {}
                }
                
            });
        }
        $scope.addCoupon = function(){
            if(ZL == 'True' && USER_NAME!='None'){
                $('#add_coupon').addClass('is_visible');
            } else {
                $scope.$emit('setLoginPurpose', 'apply a coupon' );
                $('.right_panel_inner > div').removeClass('is_visible');
                $($('.login_label').attr('data-activates')).addClass('is_visible');
                $('.right_panel').addClass('is_visible');
            }
        }
        $scope.applyCoupon = function(code){
            if(code) {
                var data = {'carts':[]}
                for (i in $scope.carts.items) data['carts'].push($scope.carts.items[i].id)
                $http.post('/offer/apply/'+code, data).
                    success(function(rs, status, headers, config) {
                        if (rs.status == "success"){
                            $('#add_coupon').removeClass('is_visible');
                            $rootScope.cart();
                        }
                    });
            }
        }
        $scope.getCredits = function(code){
            if(code){
                $http.post('/coupon/promo/',{'code':code}).
                success(function(rs){
                    if(rs.status == 'success'){
                        Materialize.toast(rs.data.message, 3000);
                        $scope.user.wallet+=rs.data.amount
                        // $scope.mywallet.zapcash+=rs.data.amount
                        $('#promocode').removeClass('is_visible')
                        $scope.promocode = ''
                        // $('#promocode .close_btn').click()
                    }else{
                        Materialize.toast(rs.detail, 3000);
                        $('#promocode input').focus();
                    }
                    // alert(JSON.stringify(rs))
                })
            }
        }
        $scope.initLoginPupose = function(){
            $scope.loginPurpose = false
        }
        window.userInteractionTimeout = null;
        window.userInteractionInHTMLArea = false;
        window.onBrowserHistoryButtonClicked = null; // This will be your event handler for browser navigation buttons clicked

        // $(document).ready(function () {  
            $(document).mousedown(function () {
                clearTimeout(window.userInteractionTimeout);
                window.userInteractionInHTMLArea = true;
                window.userInteractionTimeout = setTimeout(function () {
                    window.userInteractionInHTMLArea = false;
                }, 500);
            });

            $(document).keydown(function () {
                clearTimeout(window.userInteractionTimeout);
                window.userInteractionInHTMLArea = true;
                window.userInteractionTimeout = setTimeout(function () {
                    window.userInteractionInHTMLArea = false;
                }, 500);
            });

            if (window.history && window.history.pushState) {
                $(window).on('popstate', function () {
                    if (!window.userInteractionInHTMLArea) {
                        var rp = window.location.href.split('/#')[1]
                        if(rp){
                            var tab = rp.replace('rp_', "");
                            // $('.right_panel').addClass('is_visible');
                            // $scope[tab]();
                            // $('#'+tab).addClass('is_visible')
                            try{
                                $scope[tab]();
                                $('.right_panel').addClass('is_visible');
                                $('#'+tab).addClass('is_visible')
                            }catch(err) {
                                var t = tab.split('/')
            if((t[1]=='product' || t[1]=='profile') && t[2]!=undefined){
                window.location.href = t[1]+'/'+t[2];
            }else if(t[1] == 'feeds' || t[1] == 'discover' || t[1] == 'sell'){
                window.location.href = "/"+t[1];
            }else{
                console.log('url mismatch')
            }
                                
                            }
                        }else{
                        $('.right_panel').removeClass('is_visible');
                            
                        }
                        // alert('Browser Back or Forward button was pressed.');
                    }
                    if(window.onBrowserHistoryButtonClicked ){
                        window.onBrowserHistoryButtonClicked ();
                    }
                });
            }
            // window.onpopstate = function(e){ //for back and forth button
            //     if(e.state){
            //         document.getElementById("content").innerHTML = e.state.html;
            //         document.title = e.state.pageTitle;
            //     }
            // };
    $scope.wlError = '';
    $scope.offer_500 = true
    setTimeout(function(){
        $scope.offer_500 = getCookie('offer_500')
        if(!$scope.$$phase) {
            $scope.$apply()
        }
    },4000)
    $scope.get500 = function(){
        if(!$scope.emailId){
            $scope.wlErrorEmail = 'invalid email';
            return false;
        }
        $scope.wlError = '';
        $scope.wlErrorEmail = '';
        $http.post('/user/website_lead',{'email':$scope.emailId}).success(function(rs){
            if(rs.status == 'success'){
                document.cookie = "offer_500=true; expires=Thu, 18 Dec 2016 12:00:00 UTC; path=/";
                $scope.wlSuccess = true
                setTimeout(function(){
                    $scope.offer_500 = true
                    if(!$scope.$$phase) {
                        $scope.$apply()
                    }
                },10000)
            }else{
                if(rs.detail == 'invalid email'){
                    $scope.wlErrorEmail = 'invalid email';
                }else{
                    $scope.wlError = rs.detail;
                    document.cookie = "offer_500=true; expires=Thu, 18 Dec 2016 12:00:00 UTC; path=/";

                    setTimeout(function(){
                        $scope.offer_500 = true
                        $('#bio_ep').css('display', 'none');
                        // $('#fashion_is_unfair').removeClass('is_visible');
                        if(!$scope.$$phase) {
                            $scope.$apply()
                        }
                    },10000)
                }
            }
        })
    }
    $scope.ZL = ZL
    $scope.hideWLOverlay = function(){
        $('#bio_ep').css('display', 'none');
        $('#fashion_is_unfair').removeClass('is_visible');
        document.cookie = "offer_500=true; expires=Thu, 18 Dec 2016 12:00:00 UTC; path=/";
        $scope.offer_500 = true
        if(!$scope.$$phase) {$scope.$apply(); }
    }
    $scope.showReason = function(){
        $("#return_reason").addClass('is_visible');
    }    
    
    $scope.returnOrder = function(tracker){
        if ($('.selectable').hasClass('selected')){
            $('#returnLoader').addClass('is_visible');
            $http.post('/user/myorders',{'order_id':$scope.order['id'],'reason':$('.selectable.selected').data('reason')}).success(function(rs){
                $('#returnLoader').removeClass('is_visible');
                if(rs.status == 'success'){
                    $("#return_reason").removeClass('is_visible');
                    tracker.steps.push({'title':"Return Requested"},{'title':"Return to be confirmed"},{'title':"Product yet to be returned"})
                    tracker.current_title = "Return Requested",
                    tracker.description = "Return Requested for Approval"
                    tracker.current_step++
                    tracker.cta = false
                }else{
                    Materialize.toast(rs.detail, 3000);        
                }
            })
        }else{
            Materialize.toast("select a return reason.", 3000);
        }
    }
})

function getSuggestedQuery(filter){
    var qry = ''
    if(filter['Category'].length){
        qry += '&i_category='+filter['Category'][0].replace(/ /g,'-').toLowerCase();
    }if(filter['Style'].length){
        qry += '&i_style='+filter['Style'][0].replace(/ /g,'-').toLowerCase();
    }if(filter['Brand'].length){
        qry += '&i_brand='+filter['Brand'][0].replace(/ /g,'-').toLowerCase();
    }if(filter['Color'].length){
        qry += '&i_color='+filter['Color'][0].replace(/ /g,'-').toLowerCase();
    }if(filter['Occasion'].length){
        qry += '&i_occasion='+filter['Occasion'][0].replace(/ /g,'-').toLowerCase();
    }if(filter['SubCategory'].length){
        qry += '&i_product_category='+filter['SubCategory'][0].replace(/ /g,'-').toLowerCase();
    }
    return qry;
}

var cart_id = ''
function cleverTapCheckout(step){
    
    clevertap.event.push("checkout_step", {
        "cart_id":cart_id,
        "step":step,
        "value_of_cart":$('#total_pay').text()
    });
}