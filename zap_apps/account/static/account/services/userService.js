zapyle.factory('admireService', function($http, $log, $q) {
    return {
        postadmire: function(user, action) {
            var deferred = $q.defer();
            $http.post('/user/admire/', {
                    'user' : user,
                    'action': action
                })
                .success(function(data) {
                    if(action=='admire'){
                        clevertap.event.push("admire", {
                            "admired_user_id":USER_ID,
                            "admiring_user_id":user,
                        });
                    }
                    deferred.resolve(data);
                }).error(function(msg, code) {
                    deferred.reject(msg);
                    $log.error(msg, code);
                });
            return deferred.promise;

        }
    }
})
zapyle.factory('loveService', function($http, $log, $q) {
    return {
        postlove: function(id, action) {
            var deferred = $q.defer();
            $http.post('/user/like_product/', {
                    'product_id' : id,
                    'action': action
                })
                .success(function(data) {
                    if(action=='like'){
                        clevertap.event.push("love", {
                            "user_id":USER_ID,
                            "product_id":id,
                        });
                    }
                    deferred.resolve(data);
                }).error(function(msg, code) {
                    deferred.reject(msg);
                    $log.error(msg, code);
                });
            return deferred.promise;

        }
    }
})