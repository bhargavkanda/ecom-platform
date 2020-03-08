(function(angular) {
  'use strict';
var editApp = angular.module('EditProductApp', ['ngStorage'])
editApp.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[').endSymbol(']]')})
editApp.directive('stringToNumber', function() {
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

editApp.controller('EditProductCtrl', function($scope, $http, $location, $localStorage) {    
    $scope.setDefaultUser = function(user){
        $(".chosen-select").append($('<option></option>')
            .val(user.id)
            .attr('selected', 'selected')
            .html(user.email)).trigger("chosen:updated");
    $('.chosen-container').css({'margin-top': '-30px', 'margin-left': '100px'})//,    margin-left: 100px)
    }
    $(".chosen-select").on('change', function(event, params) {
        $scope.change_user(params.selected)
    });
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


    jQuery(function($){
        $('ul.sortable').multisortable();
        $('ul#list1').sortable('option', 'connectWith', 'ul#list2');
    });

    $scope.images_selected = []
    $scope.old_images = []
    $scope.cropper = {};
	$scope.cropper.sourceImage = null;
 	$scope.cropper.croppedImage   = null;
    $scope.bounds = {};
    $scope.bounds.left = 50;
    $scope.bounds.right = 50;
    $scope.bounds.top = 50;
    $scope.bounds.bottom = 50;
// $scope.get_users = function(){
//     $http({
//         method: 'GET',
//         url: "/zapadmin/get_users/",
//     }).then(function successCallback(response) {
//         $scope.all_users = response.data.data
//         $scope.change_user($scope.product_data.user)
//     }, function errorCallback(response) {
//         console.log(response);
//     });        
// }
$scope.get_upload_details = function(){
    $http({
        method: 'GET',
        url: "/zapadmin/get_upload_details/",
    }).then(function successCallback(response) {
        $scope.cat=response.data.data['category']
        $scope.sub_cat = response.data.data['sub_category']
        $scope.sub_categories_temp=response.data.data['sub_category']
        $scope.colors = response.data.data['color']
        $scope.occasions = response.data.data['occasion']
        $scope.styles = response.data.data['fashion_types']
        $scope.states = response.data.data['states']
        $scope.brands = response.data.data['brands']
        $scope.categories = response.data.data['category']
        $scope.sub_categories = response.data.data['sub_category']
        $scope.size_list = response.data.data.global_product_list
        $scope.get_product_details();
    }, function errorCallback(response) {
        console.log(response.data.category);
    });        
}
$scope.set_brand = function(){
        console.log($scope.product_data.brand)
        for(var i in $scope.brands){
        	if ($scope.brands[i]['id'] == $scope.product_data.brand){
        		$scope.search_word = $scope.brands[i]['brand']		
        	}
        }
        //$scope.search_word=($scope.product_data.brand && $scope.product_data.brand) || ""
    }
$scope.get_product_details = function(){
	$scope.total_image_count = 0
	$scope.images_selected = []
    $http({
        method: 'GET',
        url: "/zapadmin/edit_product/?p_id="+p_id+"&action="+action,
    }).then(function successCallback(response) {
        $scope.setDefaultUser(response.data.data.user_detail)
        $scope.change_user(response.data.data.user_detail.id)
        console.log(response)
        $scope.product_data = response.data.data
        $scope.old_images = response.data.data.old_images
        ///////$scope.get_users()
        
        for (i in $scope.sub_cat){
            if($scope.sub_cat[i]['id'] == $scope.product_data.product_category){
                for(var j in $scope.cat){
                    if($scope.cat[j]['id'] == $scope.sub_cat[i]['parent']['id']){
                        $scope.product_data.category = $scope.cat[j]
                    }
                }
                console.log($scope.product_data.category)
                //return false
            }
        }
        for(var i in $scope.brands){
            if ($scope.brands[i]['id'] == $scope.product_data.brand){
                $scope.search_word = $scope.brands[i]['brand']      
            }
            $scope.search_word = $scope.brands[i]['brand']      
        $("#slider").attr('max', $scope.product_data.listing_price);
        $("#slider").val($scope.product_data.listing_price);  
        $scope.total_image_count = $scope.product_data.old_images.length
        $scope.set_brand()
        $scope.cat_change()
        //$scope.size_selected[0].size_type = $scope.product_data.size_type
    }}), function errorCallback(response) {
        console.log(response.data.category);
    };        
}
$scope.age = [{'id':'0', 'name':'0-3 months'},
                        {'id':'1','name':'3-6 months'},
                        {'id':'2','name':'6-12 months'},
                        {'id':'3','name':'1-2 years'}];
    $scope.conditions=[{'id':'0','name':'New with tags'},
                        {'id':'1','name':'Mint Condition'},
                        {'id':'2','name':'Gently loved'},
                        {'id':'3','name':'Worn out'}];
$scope.get_upload_details()
$scope.size_selected = [{}]  

$scope.load_zapexc_accounts = function(){
	$http({
        method: 'GET',
        url: "/zapadmin/load_zapexc_accounts/",
    }).then(function successCallback(response) {
    	$scope.selleraccounts = response.data.data
        $http({
            method: 'PUT',
            url: "/zapadmin/load_zapexc_accounts/",
            data:{'id':p_id}
        }).then(function successCallback(response) {
            if(response.data.status == 'success'){
                $scope.product_data.email = response.data.email
            }
        })
    }, function errorCallback(response) {
        console.log(response);
    });
}
$scope.change_user = function(params){
    var param = params.split(',')
    var id = param[0]
    var user_type = param[1]	
    $scope.current_user = {'type': user_type}	
	// for (i in $scope.all_users){
	// 	if($scope.all_users[i]['id']==id)
 //        {
	// 			$scope.current_user = $scope.all_users[i]
	// 			if(user_type == 'zap_exclusive' || user_type == 'zap_dummy'){
	// 				$scope.load_zapexc_accounts()
	// 			}
	// 	}
	// }
    if(user_type == 'zap_exclusive' || user_type == 'zap_dummy'){
        $scope.load_zapexc_accounts()
    }
    $http({
        method: 'GET',
        url: "/zapadmin/address/"+id+"/",
    }).then(function successCallback(response) {
        $scope.addresses = response.data.data
       	setTimeout(function(){
        	$('.address-card[select-card='+$scope.product_data.pickup_address+']').addClass('is_selected');
       	})

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
            $scope.account_holder = response.data.account_holder
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

    $scope.remove_image = function(id){
        console.log(id,'imgid')
        $('.sortable').children('li').each(function () {
        console.log(id+'---->'+$(this).find('div').find('img').attr('imgid'))
            if($(this).find('div').find('img').attr('imgid') == id){
                $(this).remove()
            }
        });
        $scope.total_image_count = $(".sortable li").length;
    }
    $scope.post_account_num = function(){
        if($scope.account_num && $scope.ifsc_code  && $scope.account_num == $scope.confirm_account_num)
        {
            $http({
                method: 'POST',
                url: "/zapadmin/accountnumber/"+$scope.product_data.user+"/",
                data: {
                    'account_number': $scope.account_num,
                    'ifsc_code': $scope.ifsc_code,
                    'account_holder': $scope.account_holder
                }
            }).then(function successCallback(response) {
                if(response.data.status == 'success'){
                    $scope.account_num_edit = 0
                }else{
                    alert(JSON.stringify(response.data.detail))                    
                }
            }, function errorCallback(response) {
                console.log(response.data.category);
            }); 
        }
    }
    $scope.fasioncalculator = function(){
        if($scope.product_data.age && $scope.product_data.condition && $scope.product_data.original_price){
            $http({
                    method: 'POST',

                    url: "/catalogue/zapfashioncalculator/",
                    data:{
                        'age':$scope.product_data.age,
                        'condition':$scope.product_data.condition,
                        'original_price':$scope.product_data.original_price,
                    }
                }).error(function(response) {
                    console.log(response)
                }).then(function successCallback(response) {
                    console.log(response)
                    $scope.product_data.listing_price = response.data.data.max_listing_price
                    $("#slider").attr('max', response.data.data.max_listing_price);
                    $("#slider").val(response.data.data.max_listing_price);  
                    //$("#slider").slider('refresh');
            });
        }
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
    //$scope.img_id = 0
    $scope.cancel_crop = function(){
        $('.crop-image').removeClass('is_visible');
    }

    $('li#remove_click').click(function(){
        alert()
    })
    $scope.changeSize = function(size){
        $scope.product_data.size_type = $scope.product_data.size_selected[0].size_type
        var count = 0
        for (i in $scope.product_data.size_selected){
            if(size.size == $scope.product_data.size_selected[i].size){
                if(++count == 2){
                    alert("This size already selected")
                    size.size = ''
                    return false
                } 
            }
        }
    }
    var image_ids = []
    $scope.submit = function(){
        image_ids = []
        $scope.images = []
        $('.sortable').children('li').each(function () {
            console.log($(this).find('div').find('img').attr('data')) // "this" is the current element in the loop
            $scope.images.push({'id':$(this).find('div').find('img').attr('data'), 'img_url' : $(this).find('div').find('img').attr('src')})
        });
    	if ($scope.product_data.size_selected.length == 0){
            alert("Choose a Size")
            return false
        }
    	if($scope.images.length){
    		if($scope.product_data.sale=='2' && $('.address-card.is_selected').length==0){
    			alert('Select a Pickup Address')
    			return false
    		}
            var user_type = $(".chosen-select").val().split(',')[1]
            if((user_type == 'zap_exclusive' || user_type == 'zap_dummy') && !$scope.product_data.email && $scope.product_data.sale == '2'){
                alert('Select a Seller Account')
                return false;
            }
            if($scope.product_data.sale=='2' && $scope.product_data.listing_price>$scope.product_data.original_price){
                alert("Listing price must be less than Original price")
                return false;
            }
			$scope.product_data['action'] = action
			$scope.product_data['pickup_address'] = $('.address-card.is_selected').attr('select-card')
			$("#updateProduct").val("Please Wait...").attr('disabled', 'disabled');
			
            for(i in $scope.images){
                $scope.images[i]['pos'] = i
                if($scope.images[i]['id'] == '0'){
                    $http({
                        method: 'POST',
                        url: "/zapadmin/upload/image",
                        data:$scope.images[i]
                    }).then(function successCallback(response) {
                        console.log(response)  
                        if(response.data.status == 'success'){   
                            image_ids.push(response.data.img_id)
                            if(image_ids.length == $scope.images.length){
                                $scope.product_data['images'] = image_ids 
                                save_product_with_image() 	

                        	}
                        }
                    })
                }else{
                    image_ids.push({'pos':i,'id':parseInt($scope.images[i]['id'])})
                    if(image_ids.length == $scope.images.length){
                        $scope.product_data['images'] = image_ids 
                        save_product_with_image()   

                    }

                }
            }
        }else{
            alert('Select atleast one Image')
            return false
        }
    }
    function save_product_with_image(){
        $scope.product_data.user = $(".chosen-select").val().split(',')[0]
        console.log($scope.product_data)
        $http({
            method: 'POST',
            url: "/zapadmin/edit_product/",
            data:$scope.product_data
        }).error(function(error){console.log(error)
            $("#updateProduct").val("Upload").prop('disabled', false);
        }).then(function successCallback(response) {
            console.log('updated success')
            console.log(response)  
            if(response.data.status == 'success'){    
                swal({   
                    title: "",   
                    text: "Product Updated Successfully!",   
                    type: "success",   
                    showCancelButton: true,   
                    confirmButtonColor: "#69DF55",   
                    confirmButtonText: "Goto Zapadmin",
                    cancelButtonText: 'Update Again',   
                    closeOnConfirm: false 
                    }, 
                    function(isConfirm)
                    {   
                        if(isConfirm){parent.history.back(); }
                        else{
                           $("#updateProduct").val("Update").prop('disabled', false);
                           $scope.get_product_details()
                        }
                    }   
                );
            }else{
                alert(JSON.stringify(response.data.detail))
                $("#updateProduct").val("Update").prop('disabled', false);
            }
            },
            function errorCallback(response) {
        });  
    }
    $scope.cat_change=function(){
        $scope.free_size = false
        console.log($scope.product_data.product_category)
        if($scope.product_data.size_selected == ''){
        	$scope.product_data.size_selected = [{}]
        }
        if($scope.product_data.category==undefined){
            $scope.free_size=true
            return true
        }
        for(i in $scope.sub_cat){
            if($scope.sub_cat[i].id == $scope.product_data.product_category){
                if($scope.sub_cat[i].parent.category_type == "FS"){
                    $scope.free_size=true
                    $scope.product_data.size_selected[0]['size_type'] = 'FREESIZE'
                    $scope.product_data.size_selected[0]['size'] = ''
                    $scope.product_data.size_type = 'FREESIZE'
                }
            }
        }

        // else if($scope.product_data.category.category_type == "FS"){

        // }else{
        // 	if ($scope.product_data.size_selected[0]['size_type'] == 'FREESIZE'){
        // 		$scope.product_data.size_selected[0]['size_type'] = ''
        // 	}
        //     $scope.free_size=false
        // }
        document.getElementById('loading').style.display = 'none';
    }
    $scope.addChoice = function(){
        $scope.product_data.size_selected.push({})
    }  
    $scope.removeChoice = function(item){
        $scope.product_data.size_selected.shift(item)
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


  // Tooltip
  $('[data-toggle="tooltip"]').tooltip();


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
            var d = new Date();
            $('.crop-image').removeClass('is_visible');
            var current_time = d.getTime()
            if($(".sortable li").length){
                $( "ul li:last-child" ).after("<li class='picture'><label class='myLabel'><a class='remove_click' onclick='remove_b64("+current_time+")'>remove</a></label><div class='imagePreview'><img imgid="+current_time+" data='0' src="+result.toDataURL('image/jpeg')+" style='height:151px;width:150px' /></div></li>")
            }else{
                $(".sortable").append("<li class='picture'><label class='myLabel'><a class='remove_click' onclick='remove_b64("+current_time+")'>remove</a></label><div class='imagePreview'><img imgid="+current_time+" data='0' src="+result.toDataURL('image/jpeg')+" style='height:151px;width:150px' /></div></li>")
            }
                // {'id':'0','image': result.toDataURL('image/jpeg')})
            //$scope.img_id=$scope.img_id+1;
            $scope.total_image_count = $(".sortable li").length;
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

});


});
})(window.angular);


    function remove_b64(imgid){
        $('.sortable').children('li').each(function () {
        console.log(imgid+'---->'+$(this).find('div').find('img').attr('imgid'))
            if($(this).find('div').find('img').attr('imgid') == imgid){
                $(this).remove()
            }
        })
    }