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
zapyle.controller('BlogController', function($scope, $http) {

    $('#blog-posts').masonry({
      // options
      itemSelector: '.post-card.show',
      columnWidth: 238,
      gutter: 24
    });

    $scope.page=1;
    $scope.blogs = [];
    $scope.loading = false;
    $scope.filter = '';
    $scope.getBlogs = function(page) {
        $http.get('/zapblog/posts?page='+page)
        .success(function(response) {
            $scope.blogs.push.apply($scope.blogs, response.data.data);
        }).error(function() {
            Materialize.toast('Error', 3000);
        });
    }
    $scope.getBlogs($scope.page);
    $http.get('/zapblog/meta_data/')
    .success(function(response) {
        if (response.status == "success"){
            $scope.MetaData = response.data;
            setTimeout(function() {
                $('.filter .highlighter').css({'left': $('.filter a.selected').offset().left});
                $('.filter .highlighter').css({'width': $('.filter a.selected').width()});
                $('.filter .highlighter').css({'top': $('.filter a.selected').offset().top + $('.filter a.selected').height() + 20 - $('.filter').offset().top});
                $('.filter .highlighter').removeClass('is_hidden');
            });
        } else {
            Materialize.toast(response.detail.error, 3000);
        }
     }).error(function() {
        Materialize.toast('Error', 3000);
     });
    $scope.$on('setShuffle', function(ngRepeatFinishedEvent) {
        items = $('#blog-posts .post-card').not('.show');
        $('#blog-posts').masonry( 'addItems', items );
        if ($scope.filter != '' && $scope.filter != 'all') {
            items = items.filter('[data-category="'+ $scope.filter +'"]');
        }
        $('#blog-posts').imagesLoaded(function () {
            items.addClass('show');
            $('#blog-posts').masonry( 'appended', items );
            $scope.loading = false;
        });
    });
    $scope.filterPosts = function($event) {
        $scope.filter = $(event.currentTarget).data('filter')
        $('.filter a').removeClass('selected');
        $(event.currentTarget).addClass('selected');
        $('.filter .highlighter').css({'left': $('.filter a.selected').offset().left});
        $('.filter .highlighter').css({'width': $('.filter a.selected').width()});
        $('.filter .highlighter').css({'top': $('.filter a.selected').offset().top + $('.filter a.selected').height() + 20 - $('.filter').offset().top});
        if ($scope.filter == 'all') {
            $('.post-card').addClass('show');
        } else {
            $('.post-card').not('[data-category="'+ $scope.filter +'"]').removeClass('show');
            $('.post-card[data-category="'+ $scope.filter +'"]').addClass('show');
        }
        $('#blog-posts').masonry('reloadItems');
        $('#blog-posts').masonry('layout');
    }
    $scope.loadMore = function(){
        $scope.page++;
        $scope.getBlogs($scope.page);
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
    $(window).scroll(function() {
        if (($(window).scrollTop() > $('footer').offset().top - $(window).height() - 250) && !$scope.loading) {
            $scope.loadMore();
            $scope.loading = true;
        }
    });
});