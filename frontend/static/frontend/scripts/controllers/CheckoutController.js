'use strict';

angular.module('zapyle')
    .controller('CheckoutController', function($location, $rootScope,$window, $scope, $routeParams, $http, addressService, productService, $localStorage) {
        $('#zap_footer').addClass('is_hidden')
        var delta = Math.abs(Date.now() - PageStartTime) / 1000;
        var minutes = Math.floor(delta / 60) % 60;
        delta -= minutes * 60;
        var seconds = delta % 60;
        mixpanel.track("User Event", {'Event Name': 'Changed page','to':window.location.href,  'time spent on page':minutes+'minutes '+seconds+'seconds', 'from':CurrentPage});    
        CurrentPage = window.location.href
        PageStartTime = Date.now()
        $scope.zap_username = $localStorage.zap_username
        var cartListCopy = $localStorage.cartList
        $rootScope.$on('parent', function(event, data) {
            if(data == 'pop'){
            $('#login-step').removeClass('open')
            $('#login-step').addClass('done')
            $('#address').addClass('open')
            $scope.zap_username = $localStorage.zap_username
            $localStorage.cartList = cartListCopy
            $scope.get_datas()
        }
        });
        $scope.check_login = function(noredirect){
            $http.get('/user/mydetails/').
                success(function(data, status, headers, config) {
                if (data.status == "success"){
                    show_loader('page', true);
                    show_loader('loading', false);

                    $('#login-step').removeClass('open')
                    $('#login-step').addClass('done')
                    $('#address').addClass('open')
                    $scope.loggedIn_request = false
                    $localStorage.user_type = data.data.user_type
                    $localStorage.loggedIn = $scope.loggedIn = true
                    $localStorage.email = data.data.email || ""
                    $localStorage.full_name = data.data.full_name
                    $localStorage.zap_username = data.data.zap_username || ""
                    $scope.zap_username = data.data.zap_username || data.data.full_name
                    $localStorage.stage = data.data.profile_completed
                    $localStorage.profile_picture = data.data.profile_pic
                    $localStorage.user_id = data.data.user_id
                    $localStorage.username = data.data.username
                    $rootScope.$broadcast('parent', 'Sathyalog')
                    console.log($localStorage.stage)
                    ga('set', 'dimension3', $localStorage.zap_username );
                    if(!noredirect){
                        if ($localStorage.stage < 5) {
                            $location.url('/onboarding')
                            return false
                        }                        
                    }

                }else{
                    $('#login-step').addClass('open')
                    show_loader('page', true);
                    show_loader('loading', false);
                    $scope.loggedIn = false
                    $('#zap_footer').removeClass('is_hidden')
                    $('#zap_footer').addClass('is_visible')
                    // $localStorage.$reset();

                    // $localStorage.loggedIn = false
                }
                

              }).
              error(function(data, status, headers, config) {
              // show_loader('page', true);
              // show_loader('loading', false);
                // called asynchronously if an error occurs
                // or server returns response with an error status.
              });
        }
        $scope.check_login()
        $scope.insta_please_wait = function(){
            $('#please-wait').addClass('is_visible')
            window.location.href = "/account/instagram/?from=checkout"
        }
        $scope.add_cart_to_logged_user = function(){
            var request = $http({
                    method: "POST",
                    url: '/zapcart/',
                    data: {
                        'from': 'website',
                        'cart_data': $localStorage.cartList},
                });
                request.success(function(response) {
                    console.log(response, "eeeeeeee")
                    if(response.status == 'success'){
                        //alert(JSON.stringify(response.data.data))
                        $('#login-step').removeClass('open')
                        $('#login-step').addClass('done')
                        $('#address').addClass('open')
                        $('#login-step').removeClass('open')
                        $('#login-step').addClass('done')
                        $scope.get_carts()
                        $scope.get_addresses()
                        $scope.check_login('noredirect')
                        $scope.get_saved_cards()
                        //FetchWallet();
                    }
                    if(response.status == 'error'){
                        var res = response.detail
                        if (res.available == 'No such cart'){
                            alert("No Cart selected")
                        }else
                        if (res.available == 0){
                            alert("Sorry Product is Sold Out")
                        }else{
                            alert("Sorry! Only "+res.available+" pieces available. You ordered "+res.ordered_quantity)
                        }
                        $location.url('/feeds')                            
                    }
                 })
                request.error(function(rs) {
                    // console
                    alert("Something doesn't seem right. We are on it! Please try after some time.");
            })
        }

        $scope.filterSavedCards = function(card) {
            if ($scope.flag==1){
                return card.type == 'debit'
            }
            if ($scope.flag==2){
                return card.type == 'credit'
            }            
        };
        $scope.FBLogin = function() {
            var cartListCopy = $localStorage.cartList
            $localStorage.$reset()
            $localStorage.cartList = cartListCopy;
            FB.login(function(response) {
                $scope.loggedIn_request = true
                $('#please-wait').addClass('is_visible')
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

                        //alert(JSON.stringify(response))
                        mixpanel.track("User Event", {'Event Name': 'Logged In', 'Channel':'Fb'});
                        $scope.check_login("noredirect")
                        $scope.get_datas()

                            console.log(response.data.data.profile_completed, "ooo")
    //                     if(response.data.data.profile_completed == 5){

    // //                            $location.url('/feeds')
    //                         $scope.add_cart_to_logged_user();
    //                     }
                        //window.location = '#/onboarding'
                        // $location.url('/onboarding')
                    }, function errorCallback(response){
                        $scope.loggedIn_request = false

                    })
                }else{
                    $('#please-wait').removeClass('is_visible')
                    $scope.loggedIn_request = false
                }
            }, {scope: 'public_profile,email'});
        };


        $scope.checkout_signup = function(){
            $(".btn_signup").text('PLEASE WAIT')
            $(".btn_signup").prop('disabled', true)
            $scope.errors = {}
            $http({
                method: 'POST',
                url: "/account/signup/",
                data: {
                    zap_username: $scope.signup_zap_username,
                    email: $scope.signup_email,
                    password: $scope.signup_password,
                    confirm_password: $scope.signup_confirm_password,
                    phone_number: $scope.signup_phone_number,
                    first_name: $scope.signup_first_name,
                    logged_device: "website",
                }
            }).then(function successCallback(response) {
                if(response.data.status=="success"){
                    mixpanel.track("User Event", {'Event Name': 'Signed up', 'Channel':'Email'});
                    $scope.check_login("noredirect")
                    $scope.get_datas()
                }else{
                    var error_msg = response.data.detail
                    if ('zap_username' in error_msg){
                        $scope.errors.username = error_msg['zap_username'][0]
                    }
                    if ('email' in error_msg){
                        $scope.errors.Email = error_msg['email'][0]
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
                    $(".btn_signup").text('Signup with Email')
                    $(".btn_signup").prop('disabled', false)
                    //console.log(JSON.stringify(response.data.detail))
                }
            }, function errorCallback(response) {

            });   
        }
        $scope.checkout_signin = function(){
            $(".btn_signin").text('PLEASE WAIT')
            $(".btn_signin").prop('disabled', true)
            $scope.errors = {}
            $http({
                method: 'POST',
                url: "/account/login/",
                data: {
                    email: $scope.email_login,
                    password: $scope.password_login,
                    logged_device: "website",
                    logged_from: "zapyle"
                }
            }).then(function successCallback(response) {
                console.log(response.data)
                if(response.data.status=="success"){
                    mixpanel.track("User Event", {'Event Name': 'Logged In', 'Channel':'Email'});
                    $scope.check_login("noredirect")
                    $scope.get_datas()
                }else{
                    var error_msg = response.data.detail
                    if (typeof error_msg == 'string'){
                        $scope.errors.password = error_msg
                    }else{
                        if ('email' in error_msg){
                            $scope.errors.email = error_msg['email'][0]
                        }
                        if ('password' in error_msg){
                            $scope.errors.password = error_msg['password'][0]               
                        }
                    }
                    console.log(JSON.stringify(response.data.detail))
                }
                $(".btn_signin").text('Login with Email')
                $(".btn_signin").prop('disabled', false)
            }, function errorCallback(response) {

            });   
        }
        $scope.get_saved_cards = function(){

            $http({
                method: 'GET',
                url: "/user/mysavedcards/",
            }).then(function successCallback(response) {
                $scope.saved_cards = response.data.data.paymentOptions
                if ($scope.saved_cards.length == 0){
                    $scope.flag=1
                    $('.li_saved').hide()
                }
                console.log($scope.saved_cards)
                
            }, function errorCallback(response) {

                console.log(response);

            });   
        }
        

        $scope.get_carts = function(){

            $http({
                method: 'GET',
                url: "/zapcart/",
            }).then(function successCallback(response) {
                console.log(response.data.status,">>>>>")
                if(response.data.status == 'success'){
                    //alert(JSON.stringify(response.data.data))
                    if($localStorage.loggedIn){
                        $('#login-step').removeClass('open')
                        $('#login-step').addClass('done')
                        $('#address').addClass('open')
                    }
                    $scope.CartData = response.data.data
                    $scope.final_price = $scope.CartData.total_price_with_shipping_charge
                    $('#zap_footer').removeClass('is_hidden')
                    $('#zap_footer').addClass('is_visible')
                }
                if(response.data.status == 'error'){

                    var res = response.data.detail
                    if (res.available == 'No such cart'){
                        alert("No Cart selected.")
                    }else if (res.available == 'Size not available'){
                        alert("Selected Size is not available.")
                    }else if (res.available == 0){
                        alert("Sorry Product is Sold Out")
                    }else{
                        alert("Sorry! Only "+res.available+" pieces available. You ordered "+res.ordered_quantity)
                    }
                    $location.url('/feeds')
                    return false
                        
                }
                
            }, function errorCallback(response) {

                console.log(response);

            });   
        }

        if($localStorage.loggedIn == true){
            $scope.get_carts();
        }else{
            // alert(JSON.stringify($localStorage.cartList)+'0000')
            if($localStorage.cartList != null){
                $('#login-step').addClass('open')
            }else{
                $location.url('/feeds')

            }
        }
        $scope.set_continue = function(id){
            if($scope.continue_id1 == id){
            setTimeout(function(){
            $('#address').removeClass('open')
            $('#address').addClass('done')
            $('#review').addClass('open')
            var add_id = $('.address-card.is_selected').attr('select-card')
            $scope.selected_address_id = add_id
            for(var i in $scope.addresses){
                if(''+$scope.addresses[i]['id'] == ''+add_id){

                    $scope.address_name = $scope.addresses[i]['name']
                    $scope.address_selected = ' '+$scope.addresses[i]['address']+' '+$scope.addresses[i]['city']+' '+$scope.addresses[i]['state']+' '+$scope.addresses[i]['pincode']
                    console.log($scope.address_selected)
                    $scope.$apply()
                }
            }
            $scope.$apply()
            }, 10)
            }else{
               $scope.continue_id1= id
            }
            

        }

        $( "div" ).delegate( ".address-card", "mouseover", function() {
          $(this).addClass('current');
        });
        $( "div" ).delegate( ".address-card", "mouseout", function() {
          $(this).removeClass('current');
        });

        // $( "div .content" ).delegate( ".address-card, .current", "click", function() {
        //     alert("kkk")
            
        // });

        // $( ".deliver" ).delegate("click", function() {
        //     alert("")
        //     $('#address').addClass('done')
        //     $('#address').removeClass('open')
        //     $('#review').addClass('open')
        // });
        $( "div" ).delegate( ".review-button", "click", function() {
            $('#review').addClass('done')
            $('#review').removeClass('open')
            $('#payment').addClass('open')
        });
        $('.step').click(function(){
            if($(this).hasClass('done')){
                if($(this).attr('id') == 'login-step'){
                    return false
                }
                // $('.step').removeClass('open')
                // if(!$(this).hasClass('done')){

                // $(this).removeClass('done')
                // }
                $('.step').removeClass('open')
                $(this).addClass('open')
            }
        })



        var AddressList = new Array();
        var DeliveryCharge;
        var DeliveryChargeCheck;
        var TotalPrice;
        var ListingPrice;
        var DiscountStatus;
        var DiscountPrice;
        var CouponId;
        var CouponIdToSend;
        var DiscountPriceToSend;
        var status = $localStorage.loggedIn
        $scope.status = status;
         var buy_status = $localStorage.buy_status;


        //$scope.ProductData = $localStorage.cartList;
        $scope.final_price = $localStorage.zptprce
        console.log($scope.ProductData)


        $scope.get_accesskey_vanity = function(){
            $http({
                        method: 'GET',
                        url: "/payment/get_accesskey_vanity/",
                    }).then(function successCallback(response) {
                        if(response.data.status == 'success'){
                            $scope.accessKey = response.data.data.access_key
                            $scope.vanityUrl = response.data.data.vanity_url
                            $scope.citrus_env = response.data.data.citrus_env
                        CitrusPay.Merchant.Config = {
                            // Merchant details
                            Merchant: {
                                accessKey: $scope.accessKey, //Replace with your access key
                                vanityUrl: $scope.vanityUrl  //Replace with your vanity URL
                            }
                        };
                        if($scope.citrus_env == 'PRODUCTION'){ CitrusPay.Config.setEnv('PRODUCTION') }
                        fetchPaymentOptions();
                        }
                        if(response.data.status == 'error'){
                        }
                        
                    }, function errorCallback(response) {

                        //alert(JSON.stringify(response.data))

                    });             
        }
        
        
        
        $scope.applyZapCash = function(input){
            $scope.apply_zapcash = $('#zapcash_checkbox').prop("checked")
            console.log($scope.apply_zapcash)
            if (!$scope.apply_zapcash){
                $scope.CartData.total_price_with_shipping_charge += $scope.zapcash_applied
                $scope.zapcash_applied = 0
            }
            else{
                if($scope.CartData.total_shipping_charge == 0){
                    if(($scope.CartData.total_price_with_shipping_charge - $scope.zapcash) < 0){
                        $scope.zapcash_applied = $scope.CartData.total_price_with_shipping_charge
                        $scope.CartData.total_price_with_shipping_charge = 0
                    }else{
                        $scope.zapcash_applied = $scope.zapcash
                        $scope.CartData.total_price_with_shipping_charge-=$scope.zapcash
                    }
                }else{
                    if(($scope.CartData.total_listing_price - $scope.zapcash) < 0){
                        $scope.zapcash_applied = $scope.CartData.total_listing_price
                        $scope.CartData.total_price_with_shipping_charge = $scope.CartData.total_shipping_charge
                    }else{
                        $scope.zapcash_applied = $scope.zapcash
                        $scope.CartData.total_price_with_shipping_charge-=$scope.zapcash
                    }                    
                }
            }
        }
        $scope.zapcash_algo = function(zapcash_input, total_amount){
            var zapcash = 0
            if(zapcash_input>=total_amount){
                $scope.zapcash_used = zapcash_input
                zapcash = $scope.zapcash - zapcash_input
                total_amount=0
            }else{
                total_amount-=zapcash_input
                $scope.zapcash_used = zapcash_input
                zapcash = $scope.zapcash - zapcash_input

            }
            return {'zapcash':zapcash,'total_amount':total_amount}
        }
        $scope.get_zapcash = function(){
                $http({
                    method: 'GET',
                    url: "/user/my_zapcash/",
                }).then(function successCallback(response) {
                    $scope.zapcash=response.data.data.amount
                }, function errorCallback(response) {
                    console.log(response)
                    //alert(JSON.stringify(response));
                });        
        }
        
        
        
        $scope.get_addresses = function(){
                $http({
                    method: 'GET',
                    url: "/address/crud/",
                }).then(function successCallback(response) {
                    console.log(response)
                    $scope.addresses=response.data.data
                }, function errorCallback(response) {
                    console.log(response);
                });        
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
        $scope.getStates=function(id){
            $http({
                    method: 'GET',
                    url: "/address/get_states/",
                }).error(function(response) {
                    console.log(response)
                }).then(function successCallback(response) {
                    $scope.states = response.data.data
             });
        }

        
        $scope.open_model = function(address){
            $scope.continue_id1=''
            $scope.modal_pop=true;
            $scope.edit_address_flag = true
            //alert(JSON.stringify(address))
            $scope.address_id = address.id
            $scope.address1 = address
            for(var i in $scope.states){
                if($scope.states[i]['name'] == address.state){
                    $scope.address1.state = $scope.states[i]
                }
            }

            // $scope.address.name = address.name
            // $scope.address.address = address.address
            // $scope.address.address2 = ''
            // $scope.address.city = address.city
            // $scope.address.state = address.state
            // $scope.address.phone = address.phone
            // $scope.address.pincode = address.pincode
            // $scope.address.email = address.email
        }
        $scope.errors = {}
        $scope.save_address=function(){
            $scope.errors ={}
            if($scope.edit_address_flag ==true){
                $('#address_button2').html('Please wait')
                $("#address_button2").prop('disabled', true)   
                $http({
                        method: 'PUT',
                        url: "/address/crud/",
                        data:{
                            'address_id' : $scope.address_id,
                            'name': $scope.address1.name,
                            'address': $scope.address1.address,
                            'address2':$scope.address1.address2,
                            'city': $scope.address1.city,
                            'state': $scope.address1.state.id,
                            'phone': $scope.address1.phone,
                            'pincode': $scope.address1.pincode,
                            // 'email': $scope.address1.email,

                        }
                    }, console.log($scope.address1.pincode)).error(function(response) {
                        console.log(response)
                        $('#address_button2').html('Update')
                        $("#address_button2").prop('disabled', false) 
                    }).then(function successCallback(response) {
                        $('#address_button2').html('Update')
                        $("#address_button2").prop('disabled', false) 
                        console.log(response+' -- '+$scope.address1.state.name)
                        if(response.data.status == 'success'){
                            response.data.data.state=$scope.address1.state.name
                            for(var i in $scope.addresses){
                                if($scope.addresses[i]['id'] == $scope.address_id){
                                    $scope.addresses[i] = response.data.data
                                }
                            }
                            // $scope.addresses.shift($scope.address)
                            // $scope.addresses.push(response.data.data)
                            $scope.modal_pop=0
                            $scope.address = ''
                            
//                            $scope.set_continue($scope.address_id)

                        }else{
                            var error_msg = response.data.detail
                            if('pincode' in error_msg){
                                $scope.errors.pincode = error_msg['pincode'][0]
                                mixpanel.track("User Event", {'Event Name': 'pincode rejected', 'pincode value':$scope.address1.pincode, 'from page': 'checkout'});
                            }
                            if('phone' in error_msg){
                                $scope.errors.phone = error_msg['phone']['phone_number']
                            }
                            //alert(JSON.stringify(response.data.detail))
                        }
                 });
            }else{
                $('#address_button1').html('Please wait')
                $("#address_button1").prop('disabled', true) 
                $http({
                        method: 'POST',
                        url: "/address/crud/",
                        data:{
                            'name': $scope.address1.name,
                            'address': $scope.address1.address,
                            'address2':$scope.address1.address2,
                            'city': $scope.address1.city,
                            'state': $scope.address1.state.id,
                            'phone': $scope.address1.phone,
                            'pincode': $scope.address1.pincode,
                            // 'email': $scope.address1.email,

                        }
                    }, console.log($scope.address1.pincode)).error(function(response) {
                        console.log(response)
                        $('#address_button1').html('Add Address')
                        $("#address_button1").prop('disabled', false) 
                    }).then(function successCallback(response) {
                        $('#address_button1').html('Add Address')
                        $("#address_button1").prop('disabled', false) 
                        if(response.data.data){
                            response.data.data.state=$scope.address1.state.name
                            $scope.addresses.push(response.data.data)
                            $scope.modal_pop=0
                            $scope.address = ''
                            // $scope.new_name = ''
                            // $scope.new_address = ''
                            // $scope.new_city = ''
                            // $scope.new_state = ''
                            // $scope.new_phone = ''
                            // $scope.new_pincode = ''
                            // $scope.new_email = ''
                            mixpanel.track("User Event", {'Event Name': 'Add address', 'city':$scope.address1.city, 'pincode':$scope.address1.pincode});
                        }else{
                            var error_msg = response.data.detail
                            if('pincode' in error_msg){
                                $scope.errors.pincode = error_msg['pincode'][0]
                                mixpanel.track("User Event", {'Event Name': 'pincode rejected', 'pincode value':$scope.address1.pincode, 'from page': 'checkout'});
                            }
                            if('phone' in error_msg){
                                $scope.errors.phone = error_msg['phone'][0]//['phone_number']
                            }
                            //alert(JSON.stringify(response.data.detail))
                        }
                 });
            }
        }
        //  Add new address function
        // ------------------------------------------------

        $scope.addNewAddress = function() {

            var addressId = addressService.getAddress();
             var request = $http({
                method: "POST",
                url: '/useraddress/' + $localStorage.id + '/',
                data: {
                    'address_id': addressId,
                    'name': $scope.username,
                    'address': $scope.addressText1,
                    'city': $scope.city,
                    'state': $scope.state,
                    'country': $scope.country,
                    'phone': $scope.phone,
                    'pincode': $scope.zipcode,
                    'email': $localStorage.email
                },
                headers: {
                    'X-UuidKey': $localStorage.uuid_keyx
                }
            });
            request.success(function(rs) {
                 AddressList.push(rs.new_address);
                $scope.addresses = AddressList;
            })
            request.error(function() {
             })
        }



        // Delete address
        // ------------------------------------------------------

        $scope.deleteAddressss = function(id) {
            var request = $http({
                method: "DELETE",
                url: '/useraddress/' + $localStorage.id + '/' + id + '/',
                headers: {
                    'X-UuidKey': $localStorage.uuid_keyx
                }
            });
            request.success(function(rs) {
                 AddressList = [];
                $http({
                    method: 'GET',
                    url: '/albumaddress/' + $localStorage.id + '/',
                    headers: {
                        'X-UuidKey': $localStorage.uuid_keyx,
                        'X-DeviceID': $localStorage.device_idx 
                    }
                }).then(function successCallback(response) {
                     AddressList = response.data.user_address;
                    $scope.addresses = AddressList;
                }, function errorCallback(response) {
                 });
                var index;
                for (var i = 0; i < AddressList.length; i++) {
                    if (AddressList[i].id = id) {
                        index = AddressList.indexOf(AddressList[i]);
                     }
                }
                AddressList.splice(index, 1);
                $scope.addresses = AddressList;
                addressService.emptyAddress();

            })
            request.error(function() {
             })

        }

        // Add transaction
        // ------------------------------------------------------


        
        $scope.save_phone_num = function(){
            if (!$scope.mymob){
                alert("Please enter phone number")
            }
            $http({
                method: 'POST',
                url: "/user/add_phone/",
                data:{
                    phone_number: $scope.mymob
                }
            }).then(function successCallback(response) {
                if (response.data.status=="error"){
                    alert(response.data.detail.phone_number)
                    return false
                }else{
                    $scope.modal_phone_pop = false
                    $scope.otp_pop_final = true
                    return false
                    // $scope.postData()
                }
            }, function errorCallback(response) {
                
            });
        }
        $scope.otp_cancel = function(){
            $scope.otp_final_pop = false
            $("#paynow_button").text('Pay Now')
            $("#paynow_button").prop('disabled', false)            
        }
        $scope.send_otp_final = function(){
            $http({
                method: 'POST',
                url: "/user/otpverify2/",
                data:{
                    otp: $scope.otp_final
                }
            }).then(function successCallback(response) {
                if (response.data.status=="error"){
                    alert(JSON.stringify(response.data.detail))
                    $("#paynow_button").text('Pay Now')
                    $("#paynow_button").prop('disabled', false)
                    return false
                }else{
                    $scope.otp_final_pop = false
                    $scope.postData()
                    return false
                }
            }, function errorCallback(response) {
                
            });            
        }
        $scope.get_my_email_and_num = function(){
            $http({
                method: 'GET',
                url: "/user/get_my_email_and_num/",
            }).then(function successCallback(response) {
                if (response.data.status=="success"){
                    $scope.user_detail = response.data.data.user_detail
                    setTimeout(function () {
                        $scope.zapMakePayment()
                    }, 10)
                }else{
                    alert(response.data.detail)
                }
            }, function errorCallback(response) {
                alert("Sorry, Payment cannot be proceed now.Please try later.")
            });
        }
        $scope.addTransaction = function() {
            var address = addressService.getAddress();
            if (address !== null) {
                if (CouponId !== null) {
                     CouponIdToSend = CouponId;
                    DiscountPriceToSend = TotalPrice;
                } else {
                     CouponIdToSend = '';
                    DiscountPriceToSend = ListingPrice;
                }
                var request = $http({
                    method: "POST",
                    url: '/transactions/' + $localStorage.id + '/' + $routeParams.CartId + '/',
                    data: {
                        'total_price': ListingPrice,
                        'final_price': DiscountPriceToSend,
                        'delivery_address': address,
                        'coupon': CouponIdToSend
                    },
                    headers: {
                        'X-UuidKey': $localStorage.uuid_keyx
                    }
                });
                request.success(function(rs) {
                     $scope.addOrder(rs.transaction_id);
                })
                request.error(function() {
                 })
            } else {
                 $.gritter.add({
                    title: 'Please select address.',
                });

            }
        }

        $scope.confirmOrder = function() {
            console.log($scope.apply_zapcash)
            if(!$scope.addresses){
                alert("Please add address")
                return false
            }
            // if($('.address-card.is_selected').length==0){
            //     alert("Select Delivery Address")
            //     return false;
            // }
            if(!$scope.selected_address_id){
                alert("Select Delivery Address")
                return false;
            }
            $scope.address_id = $('.address-card.is_selected').attr('select-card')
            if(!$scope.address_id){alert("Select Delivery Address");return false;}
            $("#paynow_button").text('PLEASE WAIT')
            $("#paynow_button").prop('disabled', true)
            if($scope.final_price > 0){
                 if($scope.flag == 4){
                    if(!$(".PayFromWallet").attr("id")){
                        alert("Please select any saved card")
                        $("#paynow_button").text('Pay Now')
                        $("#paynow_button").prop('disabled', false)
                        return false
                    }else{
                    if(!$('#CitrusMembercvv'+$scope.selected_id_for_all).val()){
                        alert("Please enter CVV")
                        $("#paynow_button").text('Pay Now')
                        $("#paynow_button").prop('disabled', false)
                        return false
                    }
                }
                }
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
                            $scope.phone_model= true
                            $scope.error_msg_phone = {}
                            return false
                        }
                        $scope.postData()
                        return false
                    }else{
                        $scope.modal_phone_pop = true
                        $scope.errors_confirm = {}
                        return false
                    }
                    $("#paynow_button").text('Pay Now')
                    $("#paynow_button").prop('disabled', false)

                    return false
                }else{
                    alert("Sorry, please try later.")
                    // $scope.postData()
                }
            }, function errorCallback(response) {
                
            }); 
        }
        $scope.phone_model_cancel = function(){
            $("#paynow_button").text('Pay Now')
            $("#paynow_button").prop('disabled', false)            
        }
        $scope.modal_phone_pop_cancel = function(){
            $("#paynow_button").text('Pay Now')
            $("#paynow_button").prop('disabled', false)            
        }
        $scope.save_email_num = function(){
            if (!($scope.confirm_email && $scope.confirm_zap_username && $scope.confirm_number)){
                alert("Please enter email, username and phone number.")
                return false
            }
            
            $http({
                method: 'POST',
                url: "/user/get_email_and_num/",
                data:{
                    email: $scope.confirm_email,
                    phone_number: $scope.confirm_number,
                    zap_username: $scope.confirm_zap_username,
                }
            }).then(function successCallback(response) {
                $scope.errors_confirm = {}
                if (response.data.status=="error"){
                    var error_msg_confirm = response.data.detail
                    if ('zap_username' in error_msg_confirm){
                        $scope.errors_confirm.zap_username = error_msg_confirm['zap_username'][0]
                    }
                    if ('email' in error_msg_confirm){
                        $scope.errors_confirm.email = error_msg_confirm['email'][0]
                    }
                    if ('phone_number' in error_msg_confirm){
                        $scope.errors_confirm.phone_number = error_msg_confirm['phone_number'][0]
                    }
                    return false
                }else{
                    $scope.modal_phone_pop = false
                    $scope.otp_final_pop = true
                    // $scope.confirm_email_num()
                    return false
                }
            }, function errorCallback(response) {
                
            });
        }
        $scope.save_phone_num = function(){
            $scope.error_msg_phone = {}
            if (!($scope.confirm_number)){
                alert("Please enter phone number.")
                return false
            }
            $http({
                method: 'POST',
                url: "/user/add_phone/",
                data:{
                    // email: $scope.confirm_email,
                    phone_number: $scope.confirm_number,
                    // zap_username: $scope.confirm_zap_username,
                }
            }).then(function successCallback(response) {
                if (response.data.status=="error"){
                    var error_msg_phone = response.data.detail
                    if ('phone_number' in error_msg_phone){
                        $scope.error_msg_phone.phone_number = error_msg_phone['phone_number'][0]
                    }
                    return false
                }else{
                    $scope.phone_model = false
                    $scope.otp_final_pop = true
                }
            }, function errorCallback(response) {
                
            });
        }
        $scope.check_card_fields = function(){
            if (!($scope.card.cardNumber && $scope.card.name && $scope.card.month && $scope.card.year && $scope.card.cvv)){
                
                return false
            }else{
                return true
            }

        }
        $scope.select_flag = function(val){
            $scope.flag = val
            if(val == 5){
                $("#paynow_button").text('Confirm Order')
                $("#paynow_button").prop('disabled', false)
            }else{
                $("#paynow_button").text('Pay Now')
                $("#paynow_button").prop('disabled', false)
            }
        }
        $scope.zapMakePayment = function(){
            // setTimeout(function(){
            if($scope.flag == 3){
                makePayment("netbanking")
            }else if($scope.flag == 4){
                if($(".PayFromWallet").attr("id") == "citrusWalletCardPayButton"){
                    makePayment("card")
                }else{
                    makePayment("netbanking", true)
                }
                
            }else{
                console.log("Payment is working...")
                makePayment("card") 
            }
            // },1000);
        }
        $scope.postData = function(){
            $scope.otp_final_pop = false
            $scope.phone_model = false
            if($scope.flag==1){
                if(!$scope.check_card_fields()){
                    alert("Please enter card number, cvv, expiry.")
                    $("#paynow_button").text('Pay Now')
                    $("#paynow_button").prop('disabled', false)                    
                    return false
                }
                $('#citrusCardType').val("debit");

            }else if($scope.flag==2){
                if(!$scope.check_card_fields()){
                    $("#paynow_button").text('Pay Now')
                    $("#paynow_button").prop('disabled', false)
                    alert("Please fill all the fields in card.")
                    return false
                }
                $('#citrusCardType').val("credit");
            }
            var data = {
                    'address_id': $scope.address_id,
                    'apply_zapcash': $scope.apply_zapcash, 
                }
            if($scope.flag==5){
                if(confirm("Are you sure you want to place the order?")){
                    data['cod'] = true
                }else{
                    $("#paynow_button").text('Pay Now')
                    $("#paynow_button").prop('disabled', false)
                    return false
                }
            }
            $http({
                method: "POST",
                url: '/payment/confirmorder/website/',
                data: data,
                }).success(function(rs) {
                    //alert(JSON.stringify(rs))
                    if(rs.status=='success'){
                        if(rs.data.message=='TXSUCCESS'){
                            window.location.href = "#/summary/?txid=" + rs.data.transaction_id;
                        }else if(rs.data.message=='TXFWD'){
                            $scope.citrus_var = rs.data
                            $scope.get_my_email_and_num()
                            //alert('going to bank'+JSON.stringify(document.getElementById("citrusCardPayButton")))
                            
                        }
                    }else{
                        $("#paynow_button").text('Pay Now')
                        $("#paynow_button").prop('disabled', false)
                        alert(JSON.stringify(rs.detail))
                    }
                    console.log(rs)
                    
                }).error(function() {

            })
        }

        $scope.payNow = function(){
            if($scope.flag==1){
                $('#citrusCardType').val("credit");
            }else if($scope.flag==2){
                $('#citrusCardType').val("debit");
            }
            $("#hashpay").val("Please Wait...").attr('disabled', 'disabled');

            $("#hashnetpay").val("Please Wait...").attr('disabled', 'disabled');
 
            $http({
                    method: 'POST',
                    url: "/order/transaction/",
                    data:{
                        'total_price':$scope.citrus_var.amount.value,
                        'transaction_ref': $scope.citrus_var.merchantTxnId
                    }
                }).error(function(response) {
                    console.log(response)
                    
                }).then(function successCallback(response) {
                    if (response.data.status == 'success'){
                        if($scope.flag == 3){
                            document.getElementById("citrusNetbankingButton").click();
                            $("#hashnetpay").val("Pay Now").prop('disabled', false);
                        }else{
                            document.getElementById("citrusCardPayButton").click();
                            $("#hashpay").val("Pay Now").prop('disabled', false);
                        }
                        
                        
                    }else{
                        $("#hashpay").val("Pay Now").prop('disabled', false);
                        $("#hashnetpay").val("Pay Now").prop('disabled', false);
                        alert(JSON.stringify(response.data.detail))
                    }
                    
             });
            
        }
        // Add Order
        // ------------------------------------------------------

        $scope.addOrder = function(t_id) {
             var address = addressService.getAddress();
            var request = $http({
                method: "POST",
                url: '/orders/' + $localStorage.id + '/',
                data: {
                    'transaction_id': t_id,
                    'success': "True"
                },
                headers: {
                    'X-UuidKey': $localStorage.uuid_keyx
                }
            });
            request.success(function(rs) {
                 var orderId = rs[0].products[0].order_id;
                window.location.href = "#/ordersummary/" + orderId;
            })
            request.error(function() {
             })
        }


        // Address Form Validation
        // -------------------------------------------------------------
        $scope.zapcash_used = 0
        $scope.applyCoupon = function() {
            if(!$scope.coupon_success){
             $http({
                method: 'POST',
                url: '/coupon/apply/',
                data: {
                    coupon_code: $scope.coupon,
                    zapcash_used: $scope.zapcash_used
                }
            }).then(function successCallback(response) {
                 if(response.data.status=="success"){
                    $scope.CartData.item.coupon.has_coupon = true
                    $scope.final_price = parseInt(response.data.data.final_price) - $scope.zapcash_used
                    $scope.CartData.item.coupon.title = response.data.data.title
                    $scope.CartData.item.coupon.coupon_discount = response.data.data.coupon_discount
                    $scope.coupon_flag=0
                    mixpanel.track("User Event", {'Event Name': 'apply coupon', 'coupon code':$scope.coupon, 'discount':$scope.CartData.item.coupon.coupon_discount, 'from page': 'checkout'});
                 }else{
                    alert(JSON.stringify(response.data.detail))
                 }                
            }, function errorCallback(response) {
                alert(JSON.stringify("Sorry, Please try later"))
             });
            }
        }
        $scope.get_datas = function(){
            $scope.getStates()
            $scope.get_addresses()
            $scope.get_zapcash()
            $scope.get_accesskey_vanity()
            // $scope.get_carts()
            $scope.get_saved_cards()

            console.log($localStorage.cartList, "new")
            if($localStorage.cartList){
                $scope.add_cart_to_logged_user()
            }            
        }
        if($localStorage.loggedIn){
            $scope.get_datas()
        }else{
            // show_loader('page', true);
            // show_loader('loading', false);
        }

        $scope.check_cardNumber = function(){
            if ($scope.flag==1){
                var classname = '.debit'
            }else if ($scope.flag==2){
                var classname = '.credit'
            }
            if($scope.card.cardNumber==null){

               $(classname + ' #cardlogo').removeClass('show-current')
            }else 
            if($scope.card.cardNumber[0]==4){
                $(classname + ' #cardmaster').removeClass('current')
                $(classname + ' #cardvisa').addClass('current')
                $(classname + ' #cardlogo').addClass('show-current')
                $('#citrusScheme').val("VISA");

            }else if($scope.card.cardNumber[0]==5){
                $(classname + ' #cardvisa').removeClass('current')
                $(classname + ' #cardmaster').addClass('current')
                $(classname + ' #cardlogo').addClass('show-current')
                $('#citrusScheme').val("mastercard");
            }
        }

        $scope.click_to_save = function(pos){
            $scope.selected_id_for_all = pos
            $(".PayFromWallet").prop("id", "citrusWalletCardPayButton");
            $('.card_radio').prop('checked', false);
            $("#saved_radio_"+pos).prop('checked', true);

        }
        $scope.zapcash_edit = function(){
            $scope.zapcash+=$scope.zapcash_used
            $scope.final_price +=$scope.zapcash_used
            $scope.zapcash_flag=1
            $scope.apply_zapcash = false
        }
        $scope.set_focus = function(s){
            if(s == 'month'){
                if($scope.card.month>0 && $scope.card.month<13 && $scope.card.month.length==2){
                    $('#year_box').focus()
                }
            }else if(s == 'year'){
                if($scope.card.year.length==2 && $scope.card.year>0 && $scope.card.year<99){
                    $('#citrusCvv').focus()
                }
            }else if(s == 'cvv'){
                if($scope.card.cvv.length==3){
                    $('#citrusCardHolder').focus()
                }
            }
        }
        $scope.send_verification_email = function(email){
            if(!email){
                return false
            }
            $(".email_verify_button").html('Please Wait...').prop('disabled', true);;
            $http({
                method: 'POST',
                url: "/account/password/reset/",
                data: {
                    email: email,
                }
            }).then(function successCallback(response) {
                $(".email_verify_button").html("Send Verification Email").prop('disabled', false);
                $scope.frgt_email=''
                if(response.data.status=="success"){
                    $scope.success_msg = response.data.data
                    //setTimeout(function(){alert(frgt_pwd_flag)}, 300);
                    
                }else{
                    if (typeof(response.data.detail)=='object'){
                        $scope.success_msg = response.data.detail['email'][0]
                        //alert(JSON.stringify(response.data.detail['email'][0]))
                    }else{
                        $scope.success_msg = response.data.detail
                        //alert(JSON.stringify(response.data.detail))
                    }
                }
            })
        }
    });
