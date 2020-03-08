var zapyle = angular.module('BlogEditor',['ngStorage','ngSanitize']);
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
zapyle.config(['$httpProvider', '$interpolateProvider',function($httpProvider, $interpolateProvider) {
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
    $httpProvider.defaults.headers.common["X-Requested-With"] = 'XMLHttpRequest';
}]);
zapyle.controller('lookEditorController', function($scope, $http) {
    $('.modal').modal();
    $scope.$on('materializeSelect', function(ngRepeatFinishedEvent) {
        $('select').material_select();
    });
    if (window.location.pathname.split('/')[3]) {
        $http.get("/zapblog/post/"+window.location.pathname.split('/')[3]).
        success(function(response) {
            if (response.status == "success") {
                $scope.post = response.data;
                $('#post-body').html($scope.post.body);
                setTimeout(function() {
                    $('select').material_select();
                });
            } else {
                Materialize.toast(response.detail.error, 3000);
            }
        }).error(function() {
            Materialize.toast('Error', 3000);
        });
    }
    $scope.get_meta_data = function() {
        $http.get('/zapblog/meta_data/')
        .success(function(response) {
            if (response.status == "success"){
                $scope.MetaData = response.data;
            } else {
                Materialize.toast(response.detail.error, 3000);
            }
         }).error(function() {
            Materialize.toast('Error', 3000);
         });
    }
    $scope.get_meta_data();
    $(function () {
        $('#fileupload').fileupload({
            url: '/zapblog/image',
            dataType: 'json',
            done: function (e, data) {
                if (data.result.status == 'success') {
                    $('.post-pic .preview img').attr('src', data.result.url);
                } else {
                    Materialize.toast(data.result.error, 3000);
                }
            }
        });
    });
    $scope.fetch_products = function() {
        if (!$scope.post) {
            Materialize.toast('Please save the post before adding products.', 3000);
        } else {
            id_string=$('#product-ids input').val().replace(/ /g,'');
            $http.get("/catalogue/look_items/?ids="+id_string).
            success(function(response) {
                if (response.status == "success") {
                    products = response.data;
                    if (!$scope.post.products) {
                        $scope.post.products = [];
                    }
                    $scope.post.products.push.apply($scope.post.products, response.data);
                } else {
                    Materialize.toast(response.detail.error, 3000);
                }
            }).error(function() {
                Materialize.toast('Error', 3000);
            });
        }
    }
    $scope.remove_item = function(event, product) {
        var index = $scope.post.products.indexOf(product);
        $scope.post.products.splice(index, 1);
        $(event.currentTarget).closest('.product-item').remove();
    }
    $scope.save_post = function(publish=null) {
        var data = {};
        data['title'] = $('#post-title input').val();
        data['body'] = $('#post-body').val();
        data['category'] = 'look-book';
        data['author'] = $('#post-author select option:selected').val();
        data['cover_pic'] = $('.post-pic .preview img').attr('src');
        product_ids = []
        $('#products .product-item').each(function() {
            product_ids.push.apply(product_ids, [parseInt($(this).data('id'))]);
        });
        data['products'] = product_ids;
//        alert(data);
        if ($scope.post) {
            $http.put('/zapblog/post/'+$scope.post.id+'/', data)
            .success(function(response) {
                if (response.status == "success") {
                    $scope.post = response.data;
                    if (publish) {
                        $('#confirm-publish').modal('open');
                    } else if (!window.location.pathname.split('/')[3]) {
                        window.location = window.location.origin + "/look/post/" + response.data.id + "/edit";
                    }
                } else {
                    Materialize.toast(response.detail.error, 3000);
                }
             }).error(function(){
                Materialize.toast('Error', 3000);
             });
        } else {
            $http.post('/zapblog/post/', data)
            .success(function(response) {
                if (response.status == "success") {
                    Materialize.toast('Post Saved.', 3000);
                    $scope.post = response.data;
                    window.location = window.location.origin + "/look/post/" + response.data.id + "/edit";
                } else {
                    Materialize.toast(response.detail.error, 3000);
                }
             }).error(function(){
                Materialize.toast('Error', 3000);
             });
        }
    }
    $scope.publish_post = function() {
        var data = {};
        data['status'] = 'PB';
        if ($scope.post) {
            $http.put('/zapblog/post/'+$scope.post.id+'/', data)
            .success(function(response) {
                if (response.status == "success") {
                    if (!$scope.post) {
                        window.location = window.location.origin + "/look/post/" + response.data.id + "/edit";
                    }
                    $scope.post = response.data;
                } else {
                    Materialize.toast(response.detail.error, 3000);
                }
             }).error(function(){
                Materialize.toast('Error', 3000);
             });
        } else {
            Materialize.toast('Error! Save the Post first.', 3000);
        }
    }
    $scope.unpublish_post = function() {
        var data = {};
        data['status'] = 'DR';
        if ($scope.post) {
            $http.put('/zapblog/post/'+$scope.post.id+'/', data)
            .success(function(response) {
                if (response.status == "success") {
                    $scope.post = response.data;
                } else {
                    Materialize.toast(response.detail.error, 3000);
                }
             }).error(function(){
                Materialize.toast('Error', 3000);
             });
        } else {
            Materialize.toast('Error! Save the Post first.', 3000);
        }
    }
    $( "#post-title input" ).change(function() {
        if (!$scope.post) {
            $('body').addClass('saving');
        }
        $scope.save_post();
    });
});