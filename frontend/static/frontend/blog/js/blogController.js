
(function(angular) {
  'use strict';
angular.module('zapyleBlog', ['angular-img-cropper']).controller('BlogCtrl', function($scope, $http) {
    //alert()
    $scope.new_img=1;
    $scope.cropper = {};
    $scope.cropper.sourceImage = null;
        $scope.cropper.croppedImage   = null;
        $scope.bounds = {};
        $scope.bounds.left = 50;
        $scope.bounds.right = 50;
        $scope.bounds.top = 50;
        $scope.bounds.bottom = 50;
    $scope.upload_to_server=function() {
                alert("ll")
        if (!$scope.cropper.croppedImage){
            $scope.cancel_crop()
            return false
        }
        // $http({
        //         method: 'POST',
        //         url: "/zapblog/image/",
        //         data:{
        //             'imageb64':$scope.cropper.croppedImage
        //         }
        //     }).error(function(error){console.log(error)
        //         alert('Somthing went wrong while image uploading. Retry...')
        //     }).then(function successCallback(response) {
                $('.crop-image').removeClass('is_visible');
                var html= "<div class='block' data-width='12'><div class='editable'><img id="" src="+$scope.cropper.croppedImage+"></div><div class='new-block'><ul><li class='text'>Text</li><li class='image'>Image</li><li class='embed'>Social Embed</li><li class='zap_embed'>Zapyle Product Embed</li><li class='button'>Button</li></ul></div><div class='edit-block'><ul><li class='move'>Move</li><li class='delete'>Delete</li></ul></div></div>"
                $scope.new_place.after(html)
                $('.crop-image').removeClass('is_visible');
            // })
        // $('.crop-image').removeClass('is_visible');
            // $scope.images_selected.push({'id':$scope.img_id,'img_url':$scope.cropper.croppedImage})
            // $scope.img_id=$scope.img_id+1;
            // if ($scope.images_selected.length==6){
            //     $scope.new_img=0;
            // }
            // $scope.img1=$scope.cropper.croppedImage;
            $scope.cropper.croppedImage=null
    }
    $scope.add_visible_crop=function (id) {
        $('.crop-image').addClass('is_visible');
    }
    $scope.cancel_crop = function(){
        $('.crop-image').removeClass('is_visible');
    }
    $('body').on('click', '.new-block li', function() {
            console.log(">>>>>>>>>>")
        if($(this).attr('class') == 'image'){
            $('.pri-overlay').removeClass('is_visible');
            $scope.new_place = $(this).closest('.block')
            document.getElementById('inputImage').click()
            return false
        }
        $(this).closest('.block').after((obj[$(this).attr('class')]));
        initiateEditor();
        $( ".block" ).draggable({
             handle: ".move",
             revert: "invalid",
             addClasses: false
        });
    });
    var json = '{"text":"<div class=\'block\'><div class=\'editable\'><p>Type here..</p></div><div class=\'new-block\'><ul><li class=\'text\'>Text</li><li class=\'image\'>Image</li><li class=\'embed\'>Social Embed</li><li class=\'zap_embed\'>Zapyle Product Embed</li><li class=\'button\'>Button</li></ul></div><div class=\'edit-block\'><ul><li class=\'move\'>Move</li><li class=\'delete\'>Delete</li></ul></div></div>",' +   
    '"image":"<div class=\'block\' data-width=\'12\'><div class=\'editable\'><img src=https://www.zapyle.com/zapmedia/uploads/product_images/original/HAMMAM_f5cebd1b-237.jpg\></div><div class=\'new-block\'><ul><li class=\'text\'>Text</li><li class=\'image\'>Image</li><li class=\'embed\'>Social Embed</li><li class=\'zap_embed\'>Zapyle Product Embed</li><li class=\'button\'>Button</li></ul></div><div class=\'edit-block\'><ul><li class=\'move\'>Move</li><li class=\'delete\'>Delete</li></ul></div></div>",' +
    '"embed":"<div class=\'block\'><div class=\'editable\'><embed></embed></div><div class=\'new-block\'><ul><li class=\'text\'>Text</li><li class=\'image\'>Image</li><li class=\'embed\'>Social Embed</li><li class=\'zap_embed\'>Zapyle Product Embed</li><li class=\'button\'>Button</li></ul></div><div class=\'edit-block\'><ul><li class=\'move\'>Move</li><li class=\'delete\'>Delete</li></ul></div></div>",' +
    '"zap_embed":"<div class=\'block\'><div class=\'editable\'><iframe></iframe></div><div class=\'new-block\'><ul><li class=\'text\'>Text</li><li class=\'image\'>Image</li><li class=\'embed\'>Social Embed</li><li class=\'zap_embed\'>Zapyle Product Embed</li><li class=\'button\'>Button</li></ul></div><div class=\'edit-block\'><ul><li class=\'move\'>Move</li><li class=\'delete\'>Delete</li></ul></div></div>",' +
    '"button":"<div class=\'block\'><div class=\'editable\'><a href=\'\'><button val=\'\'></a></div><div class=\'new-block\'><ul><li class=\'text\'>Text</li><li class=\'image\'>Image</li><li class=\'embed\'>Social Embed</li><li class=\'zap_embed\'>Zapyle Product Embed</li><li class=\'button\'>Button</li></ul></div><div class=\'edit-block\'><ul><li class=\'move\'>Move</li><li class=\'delete\'>Delete</li></ul></div></div>",' +
    '"row":"<div class=\'row\'><div class=\'column size12of12\' data-width=\'12\'><div class=\'block\'><div class=\'new-block\'><ul><li id=\'text\' class=\'text\'>Text</li><li id=\'image\' class=\'image\'>Image</li><li id=\'embed\' class=\'embed\'>Social Embed</li><li id=\'zap_embed\' class=\'zap_embed\'>Zapyle Product Embed</li><li id=\'button\' class=\'button\'>Button</li></ul></div></div></div></div>"' +
    '}';
    var obj = JSON.parse(json);



});
})(window.angular);