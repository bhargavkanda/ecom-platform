'use strict';

angular.module('zapyle')
    .service('productService', function() {
        var productList = [];

        var addProduct = function(p_id, title, size, qty, image, fashion, brand, listing_price) {
            productList.push({
                "id": p_id,
                "title": title,
                "size": size,
                "quantity": qty,
                "image": image,
                "fashion": fashion,
                "brand": brand,
                "listing_price": listing_price
            });
        };

        var getProducts = function() {
            return productList;
        };

        return {
            addProduct: addProduct,
            getProducts: getProducts
        };

    })
    .service('addressService', function() {
        var SelectedAddressId = null;

        var selectAddress = function(id) {
            SelectedAddressId = id;
        };

        var emptyAddress = function() {
            SelectedAddressId = null;
        };

        var getAddress = function() {
            return SelectedAddressId;
        };

        return {
            selectAddress: selectAddress,
            getAddress: getAddress,
            emptyAddress: emptyAddress
        };

    })
    .service('mouseHoverService', function() {
 
        function changeImage(current) {
            if (current.closest('.current').length && current.siblings().length) {
                current.removeClass('is_current');
                if (current.next().length) {
                    current = current.next();
                } else {
                    current = current.siblings().eq(0);
                }
                current.addClass('is_current')
                setTimeout(function() {
                    changeImage(current);
                }, 1500);
            }
        }
        return {
            changeImage: changeImage
        };

    })
    // .service('mouseHoverService', function() {
 
//     function changeImage(current) {
//         if (current.closest('.current').length) {
//             current.removeClass('is_current');
//             if (current.next().length) {
//                 current = current.next();
//             } else {
//                 current = current.siblings().eq(0);
//             }
//             current.addClass('is_current')
//             setTimeout(function() {
//                 changeImage(current);
//             }, 1000);
//         }
//     }
//     return {
//         changeImage: changeImage
//     };

// })
.factory('likeService', function($http, $log, $q, $localStorage) {
        return {
            postLikes: function(album_id) {
                var deferred = $q.defer();
                $http.post('/like/', {
                        'album_id': album_id
                    })
                    .success(function(data) {
                        deferred.resolve(data);
                    }).error(function(msg, code) {
                        deferred.reject(msg);
                        $log.error(msg, code);
                    });
                return deferred.promise;

            }
        }
    })
    .factory('UnlikeService', function($http, $log, $q, $localStorage) {
        return {
            postunLikes: function(album_id) {
                var deferred = $q.defer();
                $http.post('/unlike/', {
                        'album_id': album_id
                    })
                    .success(function(data) {
                        deferred.resolve(data);
                    }).error(function(msg, code) {
                        deferred.reject(msg);
                        $log.error(msg, code);
                    });
                return deferred.promise;

            }
        }
    })
    .factory('admireService', function($http, $log, $q, $localStorage) {
        return {
            postadmire: function(album_user_id) {
                var deferred = $q.defer();
                $http.post('/admire/', {
                        'user_id': $localStorage.id,
                        'album_user_id': album_user_id
                    }, {
                        headers: {
                            'X-UuidKey': $localStorage.uuid_keyx
                        }
                    })
                    .success(function(data) {
                        deferred.resolve(data);
                    }).error(function(msg, code) {
                        deferred.reject(msg);
                        $log.error(msg, code);
                    });
                return deferred.promise;

            }
        }
    })
    .factory('UnadmireService', function($http, $log, $q, $localStorage) {
        return {
            postunadmire: function(album_user_id) {
                var deferred = $q.defer();
                $http.post('/undoadmire/', {
                        'user_id': $localStorage.id,
                        'album_user_id': album_user_id
                    }, {
                        headers: {
                            'X-UuidKey': $localStorage.uuid_keyx
                        }
                    })
                    .success(function(data) {
                        deferred.resolve(data);
                    }).error(function(msg, code) {
                        deferred.reject(msg);
                        $log.error(msg, code);
                    });
                return deferred.promise;

            }
        }
    }).service('SellerData', function() {
        var SellerFeedView = new Array();

        var addData = function(data) {
            SellerFeedView.push(data);
        };

        var emptyData = function() {
            SellerFeedView = [];
        };

        var getData = function() {
            return SellerFeedView;
        };

        return {
            addData: addData,
            emptyData: emptyData,
            getData: getData
        };

    }).service('ProductData', function() {
        var ProductFeedarray = new Array();

        var addData = function(data) {
            ProductFeedarray.push(data);
        };

        var emptyData = function() {
            ProductFeedarray = [];
        };

        var getData = function() {
            return ProductFeedarray;
        };

        return {
            addData: addData,
            emptyData: emptyData,
            getData: getData
        };

    })
    .filter('reverse', function() {
        return function(items) {
            return items.slice().reverse();
        };
    });
