zapyle.controller('SellController', function($scope, $http, loveService) {
		
	$scope.getUserDetails = function(){
		$http.get('/user/profile/'+USER_ID).
	        success(function(data, status, headers, config) {
	        if (data.status == "success"){
	            $scope.profile = data.data.products
	            $scope.user_type = data.data.user_type
	            if(!$scope.profile.length){
	            	$scope.getCategories()
	            }
	        }
	    })
	}
	$scope.getCategories = function(){
		$http.get('/catalogue/webfilteritems/?catalogue=true&brand=true').
		success(function(rs){
			if(rs.status == 'success'){
				$scope.brands = rs.data.brands
				$scope.catalogues = rs.data.catalogues
				setTimeout(function() { $('select').material_select() });
			}
		})
	}
	if(ZL == 'True'){
		$scope.getUserDetails()
	}else{
		$scope.getCategories()
	}
	$scope.fashion = {}
	$scope.calculateFashion = function(data){
		if(!data['product_category']){
			Materialize.toast('Select Category.', 3000);
			return false;
		}
		if(!data['original_price']){
			$('#original_price').focus()
			Materialize.toast('Enter Original Price.', 3000);
			return false;
		}
		if(data['age'] == undefined){
			Materialize.toast('Select Age.', 3000);
			return false;
		}
		if(data['condition'] == undefined){
			Materialize.toast('Select Condition.', 3000);
			return false;
		}
		$http.post('/catalogue/zapfashioncalculator',data)
		.success(function(data){
			if(data.status == 'success'){
				$scope.fashionPrice = data.data.max_listing_price
				// $scope.earnings = data.data.earning
				$scope.fashionCheck = true
				$http.get('/catalogue/sim/1?plt=10&pht=0&cat='+$scope.fashion.product_category+'&pr='+$scope.fashionPrice*75/100).
				success(function(rs){
					$scope.cSimilar = rs.data.data.splice(0, 2)
					if($scope.cSimilar.length<2){
						$http.get('/catalogue/sim/1?plt=10&pht=0&pr='+$scope.fashionPrice*75/100).
						success(function(rs){$scope.cSimilar = rs.data.data.splice(0, 2)})
					}
				})
				$http.get('/catalogue/sim/1?plt=10&pht=0&cat='+$scope.fashion.product_category+'&pr='+$scope.fashionPrice*85/100).
				success(function(rs){
					$scope.mSimilar = rs.data.data.splice(0, 2)
					if($scope.mSimilar.length<2){
						$http.get('/catalogue/sim/1?plt=10&pht=0&pr='+$scope.fashionPrice*85/100).
						success(function(rs){$scope.mSimilar = rs.data.data.splice(0, 2)})
					}
				})
			}
		})
	}
	$scope.pickup = {}
	$scope.setschedulePickup = function(){
		setTimeout(function() { $('select').material_select() });
	}
	$scope.uploadPickup = function(){
        var formData = new FormData();
        $('.image_files').each(function(i, obj) {
			formData.append("image"+i, obj.files[0]);
		});
		formData.append("data", JSON.stringify($scope.fashion))
		$http({
             method: 'POST',
             url: '/catalogue/schedulepickup/',
             'data' : formData,
             transformRequest: angular.identity,
             headers: {'Content-Type': undefined}
         }).then(function successCallback(rs) {
         	if(rs.data.status == 'success'){
				$scope.doneUpload = true
			}else{
         		Materialize.toast(JSON.stringify(rs.data.detail), 3000);
			}
         })
	}
	$scope.addImg = function(){
		str = makerandomstr()
		$('.pictures').prepend("<input type='file' id='"+str+"' class='image_files' hidden onchange='fileChange(this)'>")
		$('#'+str).click()
	}
	$('body').on('click', '.delete', function() {
		var el = $(this).parent()
		$('#'+el.data('string')).remove()
		el.remove()
		if($('.pickup_imgs').length < 4){
        	$('.add_img').removeClass('is_hidden')
        }
	})	
	var req1 = true
	$scope.callMe = function(){
		if(req1){
			req1 = false
			if($scope.phone){
				$.post( "/account/call/", {'phone_number':$scope.phone},function( data ) {
			  		if(data.status == 'success'){
			  			$scope.callRequested = true	
			  			if(!$scope.$$phase) {
			                $scope.$apply()
			            }
			  		}else{
				  		Materialize.toast('Enter valid phone number.', 3000);
			  		}
			  		req1 = true
				});
			}else{
				$('#phone_input').focus();
				req1 = true
			}
		}
	}
	$scope.love = function(p){
        if(ZL == 'True' && USER_NAME){
            p.liked=!p.liked
            if(p.liked){
                loveService.postlove(p.id,'like');
            }else{
                loveService.postlove(p.id,'unlike');
            } 
        }else{
            $scope.$emit('setLoginPurpose', 'love a product' );
            $('.right_panel_inner > div').removeClass('is_visible');
            $($('.login_label').attr('data-activates')).addClass('is_visible');
            $('.right_panel').addClass('is_visible');
        }
    }
    $scope.sendLink = function(phone){
    	if(req1){
			req1 = false
			if(phone){
				$.post( "/account/call/?sendLink=true", {'phone_number':phone},function( data ) {
			  		if(data.status == 'success'){
			  			Materialize.toast('A link to download the Zapyle app has been sent to your mobile.', 3000);
			  			$scope.phone_number = ''
			  			$('.tool_tip').removeClass('is_visible')
			  		}else{
				  		Materialize.toast('Enter valid phone number.', 3000);
			  		}
			  		req1 = true
				});
			}else{
				$('#linkInput').focus();
				req1 = true
			}
		}
    }
})
function makerandomstr()
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 5; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}
var str = ''
function fileChange(input){
	if (input.files && input.files[0]) {
		$('.pictures').prepend("<div class='picture pickup_imgs' data-string='"+str+"'><span class='delete'>&times;</span><label class='myLabel'><img id='blah'></label></div>");
        var reader = new FileReader();
        reader.onload = function (e) {
            var d = document.getElementById("blah");
            d.className = "";
            $('#blah')
                .attr('src', e.target.result)
                .width(150)
                .height(150);
        };
        reader.readAsDataURL(input.files[0]);
        if($('.pickup_imgs').length == 4){
        	$('.add_img').addClass('is_hidden')
        }
    }
}