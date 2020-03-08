zapyle.controller('HomeController', function($scope, $http, admireService) {
    $scope.isMobile = false;
    if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent) 
        || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))) $scope.isMobile = true;
  	var typingTimer; 
    var doneTypingInterval = 800;
    var $input = $('#searchBoxhome');
    $input.on('keyup', function () {
      clearTimeout(typingTimer);
      typingTimer = setTimeout(doneTyping, doneTypingInterval);
    });
    $input.on('keydown', function () {
      clearTimeout(typingTimer);
    });
    function doneTyping() {
        $scope.doSearch()
    }
    $scope.doSearch = function(){
        $scope.url_search_key = false
        $scope.getSuggestions()    
    }
    $scope.tab = 'product'
    function getPage() {
        var pathArray = window.location.pathname.split( '/' );
        page = pathArray[1];
        if (page == 'events') {
            return '&page=events';
        } else {
            return '';
        }
    }
    var pagerequest = getPage();
    $scope.get_discover_datas = function(){
        $http.get('https://search-zapylesearch-oh745tarex4gbmbmndo7ek6inq.us-west-1.es.amazonaws.com/discover/data/_search?sort=importance:desc&q=active:true').success(function (data) {
        // $http.get('http://localhost:9200/discovers/data/_search?sort=importance:desc&q=active:true').success(function (data) {
            // console.log(data)
            // alert(JSON.stringify(data.hits.hits));
            $scope.discover_data = data.hits.hits
        });
    }
    $scope.get_discover_datas()

	$scope.getSuggestions = function(tab){
        if(!tab){
            if($('#clst_tab').hasClass('active')){tab = 'closet'}else{tab = 'product';}
        }
        if(!$scope.search_key){
            if(tab=='product'){$scope.pInit = true}else{$scope.uInit = true;}
            return false
        }
        $scope.tab = tab
        if($scope.use_suggestion_flag){
            var str1 = $scope.search_key.substring(0, $scope.use_suggestion_string.length)
            var str2 = $scope.use_suggestion_string
            if (str1 === str2)
            {
                var key = $scope.search_key.substring($scope.use_suggestion_string.length)
                if(!key){
                    $scope.suggestions = []
                    $scope.$apply()
                    return false;
                }
                $scope.search_use_suggestion(key)
            }else
            {
                $scope.search_key = ''
                $scope.use_suggestion_flag = false
                $scope.$apply()
            }   
            return false;
        }
        $http({
            method: 'POST',
            url: "/search/suggestions/"+tab,
            data: {
                query_string: $scope.search_key,
                filter : {
                  "Category": [],
                  "Style": [],
                  "Color": [],
                  "Occasion": [],
                  "Brand": [],
                  "SubCategory": [],
                  "string": ""
                },
            }
        }).then(function successCallback(response) {
            $scope.suggestions = response.data.data
            if(tab=='product'){$scope.pInit = false}else{$scope.uInit = false;}
        })
    }
    $scope.pInit = true
    $scope.uInit = true
    $scope.useSuggestion = function(obj){
        $scope.search_key = obj.string
        setTimeout(function() { $("#searchBox").focus(); });
        $scope.use_suggestion_flag = true
        $scope.use_suggestion_obj = obj
        $scope.use_suggestion_string = obj.string.substring(0,obj.string.length-1)
    }
    $scope.search_use_suggestion = function(query_string){
        if(query_string){
            $http({
                method: 'POST',
                url: "/search/suggestions/product",
                data: {
                    query_string: query_string,
                    filter : $scope.use_suggestion_obj,
                }
            }).then(function successCallback(response) {
                $scope.suggestions = response.data.data
            })
        }
    }
    $scope.searchSuggestion = function(key){     
        if(!key){
            $('#searchBoxhome').focus()
            return false;
        }  
        if($scope.use_suggestion_flag){
            window.history.pushState('', '', '/buy?search='+$scope.use_suggestion_string.replace(' ','+')+getSuggestedQuery($scope.use_suggestion_obj))
        }else{
            window.history.pushState('', '', '/buy?search='+key.replace(' ','+'))
        }
        location.reload();
    }
    $scope.searchFilter = function(filter){
        var str = filter.string.replace(' ','+')
        window.history.pushState('', '', '/buy?search='+str.rtrim()+getSuggestedQuery(filter))
        location.reload();
    }
    // $scope.admire = function(data){
    //     if(ZL == 'True'){
    //         data.admired=!data.admired
    //         if (data.admired){
    //             admireService.postadmire(data.id,'admire');
    //         }
    //         else{
    //             admireService.postadmire(data.id,'unadmire');
    //         }
    //     }else{
    //         $scope.$emit('setLoginPurpose', 'admire a user' );
    //         $('.right_panel_inner > div').removeClass('is_visible');
    //         $($('.login_label').attr('data-activates')).addClass('is_visible');
    //         $('.right_panel').addClass('is_visible');
    //     }
    // }//discover admire
    $scope.admire = function(data){
        if(ZL == 'True'){
            if (data.admired){
                admireService.postadmire(data.user_id,'unadmire');
            }
            else{
                admireService.postadmire(data.user_id,'admire');
            }
            data.admired = ! data.admired
        }else{
            $scope.$emit('setLoginPurpose', 'admire a user' );
            $('.right_panel_inner > div').removeClass('is_visible');
            $($('.login_label').attr('data-activates')).addClass('is_visible');
            $('.right_panel').addClass('is_visible');
        }
    }
    $('#searchBoxhome').keypress(function (e) {
        var key = e.which;
        if(key == 13)
        {
            $scope.searchSuggestion($scope.search_key)
        }
    })
    $scope.$on('onRepeatLast', function(scope, element, attrs){
        carousel=$(element).closest('.products.wrapper')
        setCarousel(carousel);
    });
})

zapyle.directive('onLastRepeat', function() {
    return function(scope, element, attrs) {
        if (scope.$last) setTimeout(function(){
            scope.$emit('onRepeatLast', element, attrs);
        }, 1);
    };
})
