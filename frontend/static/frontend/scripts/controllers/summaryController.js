'use strict';

/**
 * @ngdoc function
 * @name appApp.controller:AboutCtrl
 * @description
 * # AboutCtrl
 * Controller of the appApp
 */
angular.module('zapyle')
    .controller('summaryController', function($localStorage, $scope,$route, $http, $routeParams, $location) {
        
        $scope.zap_username = $localStorage.zap_username
        mixPanelVar.CurrentPage = 'summary'
        mixPanelVar.pageStartTime = Date.now()
        console.log($location.search()['txid'])
        $scope.txid = $location.search()['txid']
        $http({
                method: 'GET',
                url: $location.search()['txid'] ? '/payment/summary/?txid=' + $location.search()['txid'] : '/payment/summary/',
            }).then(function successCallback(response) {
                if(response.data.status == 'success'){
                    show_loader('page', true);
                    show_loader('loading', false);

                    $scope.card = ''
                    $scope.flag = 4
                    //alert(JSON.stringify(response))
                    $scope.summarydetail = response.data.data
                    $scope.final_price = $scope.summarydetail.listing_price + $scope.summarydetail.shipping_charge - $scope.summarydetail.zapwallet_used
                    if($location.search()['txid'] && $localStorage.buyStartTime){
                        var delta = Math.abs(Date.now() - $localStorage.buyStartTime) / 1000;
                        var minutes = Math.floor(delta / 60) % 60;
                        delta -= minutes * 60;
                        var seconds = delta % 60;
                        for (var i in $scope.summarydetail.ordered_products){
                            mixpanel.track("User Event", {'Event Name': 'Purchase made', 'total time for checkout':minutes+'minutes '+seconds+'seconds', 'product title':$scope.summarydetail.ordered_products[i].title,'product price':$scope.summarydetail.ordered_products[i].listing_price, 'from page': 'summary'});
                        }
                        $localStorage.buyStartTime = ''
                    }

                }else{
                    show_loader('page', true);
                    show_loader('loading', false);

                    window.location = '#/feeds'                    
                }
            }).then(function errorCallback(response){
                    show_loader('page', true);
                    show_loader('loading', false);
            });
        $scope.goto_feeds = function(){
            window.location = '#/feeds'
        }
        $scope.change_flag = function(num){
            $scope.flag = num
        }

        $scope.get_saved_cards = function(){

            $http({
                method: 'GET',
                url: "/user/mysavedcards/",
            }).then(function successCallback(response) {
                $scope.saved_cards = response.data.data.paymentOptions
                if ($scope.saved_cards.length == 0){
                    $scope.flag = 1
                    $('.li_saved').hide()
                }
                console.log($scope.saved_cards)
                
            }, function errorCallback(response) {

                console.log(response);

            });   
        }
        
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

                        alert(JSON.stringify(response.data))

                    });             
        }
        $scope.confirmOrder = function() {
            console.log($scope.flag)
            // alert($scope.flag+'--'+$(".PayFromWallet").attr("id"))
            // return false
            $("#paynow_button").text('PLEASE WAIT')
            $("#paynow_button").prop('disabled', true)
            if($scope.final_price > 0){
                 if($scope.flag == 4){
                    if(!$(".PayFromWallet").attr("id")){
                        alert("Please select any saved card")
                        $("#paynow_button").text('RETRY PAYMENT')
                        $("#paynow_button").prop('disabled', false)
                        return false
                    }else{
                    if(!$('#CitrusMembercvv'+$scope.selected_id_for_all).val()){
                        alert("Please enter CVV")
                        $("#paynow_button").text('RETRY PAYMENT')
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
                    if($scope.confirm_email && $scope.confirm_number && $scope.confirm_zap_username){
                        $scope.postData()
                        return false
                    }
                    $scope.modal_phone_pop = true
                    $("#paynow_button").text('RETRY PAYMENT')
                    $("#paynow_button").prop('disabled', false)
                    return false
                }else{
                    alert("Sorry, please try later.")
                    // $scope.postData()
                }
            }, function errorCallback(response) {
                
            }); 
        }
        $scope.save_email_num = function(){
            if (!($scope.confirm_email && $scope.confirm_number && $scope.confirm_zap_username)){
                alert("Please enter phone number, email and username")
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
                if (response.data.status=="error"){
                    alert(JSON.stringify(response.data.detail))
                    return false
                }else{
                    $scope.modal_phone_pop = false
                    $scope.postData()
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
        $scope.get_my_email_and_num = function(){
            $http({
                method: 'GET',
                url: "/user/get_my_email_and_num/",
            }).then(function successCallback(response) {
                //alert(JSON.stringify(response))
                if (response.data.status=="success"){
                    $scope.user_detail = response.data.data.user_detail
                }else{
                    alert(response.data.detail)
                }
            }, function errorCallback(response) {
                
            });
        }
        $scope.postData = function(){
            if($scope.flag==1){
                if(!$scope.check_card_fields()){
                    alert("Please enter card number, cvv, expiry.")
                    $("#paynow_button").text('RETRY PAYMENT')
                    $("#paynow_button").prop('disabled', false)                    
                    return false
                }
                $('#citrusCardType').val("debit");

            }else if($scope.flag==2){
                if(!$scope.check_card_fields()){
                    $("#paynow_button").text('RETRY PAYMENT')
                    $("#paynow_button").prop('disabled', false)
                    alert("Please fill all the fields in card.")
                    return false
                }
                $('#citrusCardType').val("credit");
            }

            var data = {}
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
                url: '/payment/confirmorder/website/retry/'+$scope.txid+'/',
                data:data
                }).success(function(rs) {
                    //alert(JSON.stringify(rs))
                    if(rs.status=='success'){
                        if(rs.data.message=='TXSUCCESS'){
                            window.location.href = "#/summary/?txid=" + rs.data.transaction_id;
                            //$route.reload();
                            return false
                        }else if(rs.data.message=='TXFWD'){
                            $scope.get_my_email_and_num()
                            $scope.citrus_var = rs.data
                            setTimeout(function(){
                                if($scope.flag == 3){
                                    makePayment("netbanking")
                                }else if($scope.flag == 4){
                                    if($(".PayFromWallet").attr("id") == "citrusWalletCardPayButton"){
                                        makePayment("card", true)
                                    }else{
                                        makePayment("netbanking", true)
                                    }
                                    
                                }else{
                                    makePayment("card") 
                                }
                            },1000);
                            //alert('going to bank'+JSON.stringify(document.getElementById("citrusCardPayButton")))
                            
                        }
                    }else{
                        $("#paynow_button").text('RETRY NOW')
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
                            $("#hashnetpay").val("RETRY PAYMENT").prop('disabled', false);
                        }else{
                            document.getElementById("citrusCardPayButton").click();
                            $("#hashpay").val("RETRY PAYMENT").prop('disabled', false);
                        }
                        
                        
                    }else{
                        $("#hashpay").val("RETRY PAYMENT").prop('disabled', false);
                        $("#hashnetpay").val("RETRY PAYMENT").prop('disabled', false);
                        alert(JSON.stringify(response.data.detail))
                    }
                    
             });
            
        }
        $scope.get_accesskey_vanity()
        $scope.get_saved_cards()
        $scope.click_to_save = function(pos){
            $scope.selected_id_for_all = pos
            $(".PayFromWallet").prop("id", "citrusWalletCardPayButton");
            $('.card_radio').prop('checked', false);
            $("#saved_radio_"+pos).prop('checked', true);

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
        //     if($scope.card.cardNumber==null){

        //        $('#cardlogo').removeClass('show-current')
        //     }else 
        //     if($scope.card.cardNumber[0]==4){
        //         $('#cardmaster').removeClass('current')
        //         $('#cardvisa').addClass('current')
        //         $('#cardlogo').addClass('show-current')
        //         $('#citrusScheme').val("VISA");

        //     }else if($scope.card.cardNumber[0]==5){
        //         $('#cardvisa').removeClass('current')
        //         $('#cardmaster').addClass('current')
        //         $('#cardlogo').addClass('show-current')
        //         $('#citrusScheme').val("mastercard");
        //     }
        // }

    });