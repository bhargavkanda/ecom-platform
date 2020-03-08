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
zapyle.controller('editorController', function($scope, $http) {
    $scope.image_data = [];
    $scope.previewimage = '';
    $scope.previewimage_id = '';
    $scope.get_previewimages = function() {
        $scope.image_data = [];
        $('#post-body').find('img').each(function() {
            if ($(this).attr('src').indexOf('data:') == -1) {
                $scope.image_data.push.apply($scope.image_data, [{'id': $(this).attr('id'), 'url': $(this).attr('src')}]);
            }
        });
        setTimeout(function() {
            if (!$scope.previewimage || !$('#preview_'+$scope.previewimage_id).length) {
                $('#preview-image-select span:first-of-type').addClass('selected');
                $scope.previewimage = $('#preview-image-select .selected').data('url');
                $scope.previewimage_id = $('#preview-image-select .selected').data('img_id');
            } else {
                $('#preview_'+$scope.previewimage_id).addClass('selected');
                $scope.previewimage = $('#preview-image-select .selected').data('url');
            }
        });
    }
    $scope.set_previewimage = function($event) {
        $('#preview-image-select span').removeClass('selected');
        $(event.currentTarget).addClass('selected');
        $scope.previewimage = $('#preview-image-select .selected').data('url');
        $scope.previewimage_id = $('#preview-image-select .selected').data('img_id');
        $('#post-body img').removeClass('cover_image');
        $('#'+$scope.previewimage_id).addClass('cover_image');
    }
    if (window.location.pathname.split('/')[3]) {
        $http.get("/zapblog/post/"+window.location.pathname.split('/')[3]).
        success(function(response) {
            if (response.status == "success") {
                $scope.post = response.data;
                $('#post-body').html($scope.post.body);
                if ($scope.post.cover_pic) {
                    $scope.previewimage = $scope.post.cover_pic;
                    $('#post-body').find('img').each(function() {
                        if ($(this).attr('src') == $scope.previewimage) {
                            $scope.previewimage_id = $(this).attr('id');
                            $(this).addClass('cover_image');
                        }
                    });
                }
                $('.medium-insert-images-slideshow').cycle({slides: 'figure'});
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
    $scope.initiateEditor = function() {
        var editor = new MediumEditor('.editable', {
            toolbar: {
                buttons: ['bold', 'italic', 'underline', 'quote', 'anchor', 'h2', 'h3'],
            },
            buttonLabels: 'fontawesome',
            anchor: {
                targetCheckbox: true
            },
            placeholder: {
                text: 'Type your text',
                hideOnClick: true
            }
        });
        $(function () {
            $('.editable').mediumInsert({
                editor: editor,
                addons: {
                    images: {
                        uploadScript: null,
                        deleteScript: null,
                        captionPlaceholder: 'Type caption for image',
                        styles: {
                            slideshow: {
                                label: '<span class="fa fa-play"></span>',
                                added: function ($el) {
                                    $el
                                        .data('cycle-center-vert', true)
                                        .cycle({
                                            slides: 'figure'
                                        });
                                },
                                removed: function ($el) {
                                    $el.cycle('destroy');
                                }
                            }
                        },
                        actions: {
                          remove: {
                            label: '<span class="delete_btn icon-cross"></span>',
                            clicked: function ($el) {
                                if($el.hasClass('cover_image')) {
                                    $('#cover_image_delete').modal('open');
                                    return false;
                                } else {
                                    var $event = $.Event('keydown');
                                    $event.which = 8;
                                    $(document).trigger($event);
                                }
                            }
                          },
                          zoomin: {
                            label: '<span class="zoomin_btn">+</span>',
                            clicked: function ($el) {
                                if($el[0].style.width == "") {
                                    $el.css({'width': '100%'});
                                }
                                width = parseInt($el[0].style.width);
                                if (width<100) {
                                    width+=10;
                                    $el.css({'width': String(width)+'%'});
                                }
                            }
                          },
                          zoomout: {
                            label: '<span class="zoomout_btn">-</span>',
                            clicked: function ($el) {
                                if($el[0].style.width == "") {
                                    $el.css({'width': '100%'});
                                }
                                width = parseInt($el[0].style.width);
                                if (width>10) {
                                    width-=10;
                                    $el.css({'width': String(width)+'%'});
                                }
                            }
                          }
                        }
                    }
                }
            });
        });
    }
    $scope.initiateEditor();
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
    $scope.$on('materializeSelect', function(ngRepeatFinishedEvent) {
        $('select').material_select();
    });
    $scope.save_images = function(publish=null) {
        $scope.saved = 0
        $scope.images = $('#post-body').find('img');
        $scope.images.each(function(index) {
            if ($(this).attr('src').indexOf('data:') !== -1) {
                data = {}
                data['id'] = 'img_' + index + Date.now();
                $(this).attr('id', data['id']);
                data['b64_list'] = [$(this).attr('src')];
                data['blog_id'] = $scope.post.id;
                $http.post('/zapblog/image/', data)
                .success(function(response) {
                    if (response.status == "success") {
                        $('#'+response.id).attr('src', response.url);
                        $scope.image_data.push.apply($scope.image_data, [{'id': $(this).attr('id'), 'url': response.url}]);
                        $scope.saved += 1;
                        if ($scope.saved == $scope.images.length) {
                            $scope.save_post_without_images(publish);
                        }
                    } else {
                        Materialize.toast(response.detail.error, 3000);
                        return 0;
                    }
                 }).error(function(){
                    Materialize.toast('Error', 3000);
                    return 0;
                 });
            } else {
                $scope.saved += 1;
                if ($scope.saved == $scope.images.length) {
                    $scope.save_post_without_images(publish);
                }
            }
        });
    }
    $scope.save_post = function(publish=null){
        if ($scope.post) {
            if ($('#post-body').find('img').length > 0) {
                $scope.save_images(publish);
            } else {
                $scope.save_post_without_images(publish);
            }
        } else {
            var blog_data = {};
            blog_data['title'] = $('#post-title input').val();
            $http.post('/zapblog/post/', blog_data)
            .success(function(response) {
                if (response.status == "success") {
                    $scope.post = response.data;
                    if ($('#post-body').find('img').length > 0) {
                        $scope.save_images(publish);
                    } else {
                        $scope.save_post_without_images(publish);
                    }
                } else {
                    Materialize.toast(response.detail.error, 3000);
                }
             }).error(function() {
                Materialize.toast("Title cannot be blank", 3000);
                return 0;
             });
        }
    }
    $scope.save_post_without_images = function(publish=null) {
        $('#post-body').find('.medium-insert-images-slideshow').cycle('destroy');
        var data = {};
        data['title'] = $('#post-title input').val();
        content = $('#post-body').find('.medium-insert-buttons').remove().end();
        content.find('.medium-insert-active').removeClass('medium-insert-active');
        data['body'] = content.html();
        data['category'] = $('#post-category select option:selected').val();
        data['author'] = $('#post-author select option:selected').val();
        product_ids = []
        $('#products .product-item').each(function() {
            product_ids.push.apply(product_ids, [parseInt($(this).data('id'))]);
        });
        data['products'] = product_ids;
        if ($scope.previewimage) {
            data['cover_pic'] = $scope.previewimage;
        } else {
            data['cover_pic'] = null;
        }
        if ($scope.post) {
            $http.put('/zapblog/post/'+$scope.post.id+'/', data)
            .success(function(response) {
                if (response.status == "success") {
                    $scope.post = response.data;
                    $('.medium-insert-images-slideshow').cycle({slides: 'figure'});
                    if (publish) {
                        $('#confirm-publish').modal('open');
                    } else if (!window.location.pathname.split('/')[3]) {
                        window.location = window.location.origin + "/blog/post/" + response.data.id + "/edit";
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
                    window.location = window.location.origin + "/blog/post/" + response.data.id + "/edit";
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
                        window.location = window.location.origin + "/blog/post/" + response.data.id + "/edit";
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

    $('body').on('click', '.pri-overlay.image .show-preview', function() {
        result = $image.cropper('getCroppedCanvas', null, null);
        // var html= "<img src="+result.toDataURL('image/jpeg')+">"
        // console.log(html)
        previewImage(result);
      });
      $('body').on('click', '.pri-overlay.image .back', function() {
        $('.pri-overlay.image').removeClass('preview-mode');
      });
      $('.modal').modal();
      $( "#post-category select" ).change(function() {
        $('.post-preview .post-category').html($( "#post-category select option:selected" ).html());
      });
      $( "#post-title input" ).change(function() {
        $('.post-preview .post-title').html($(this).val());
      });
    $('body').on('click', '.side-bar-inner > .close_trigger', function() {
        $('.side-bar-inner > div').removeClass('is_visible');
    });
    $( "#post-title input" ).change(function() {
        if (!$scope.post) {
            $('body').addClass('saving');
        }
        $scope.save_post();
    });
    $('body').on( "keydown", function( event ) {
        if (event.which == 8 && $('.medium-insert-images img.medium-insert-image-active').length > 0) {
            if ($('.medium-insert-images img.medium-insert-image-active').hasClass('cover_image')) {
                $('.medium-insert-images').removeClass('medium-insert-active');
                $('.medium-editor-toolbar.medium-editor-toolbar-active').removeClass('medium-editor-toolbar-active');
                $('#cover_image_delete').modal('open');
                event.stopPropagation();
                return false;
            }
        }
    });
});
