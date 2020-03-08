zapyle.filter('spacetounderscore',function() {
    return function(input) {
        if (input) {
            return input.replace(/\s+/g, '_');    
        }
    }
});

zapyle.filter('totalunselectedsubcats',function($filter){
    return function(input){
        return $filter("filter")(input, {selected:false}).length;
    }
})
zapyle.filter('totalselectedsubcats',function($filter){
    return function(input){
        return $filter("filter")(input, {selected:true}).length;
    }
})
zapyle.filter('totalenabledsubcats',function($filter){
    return function(input){
        return $filter("filter")(input, {disabled:false}).length;
    }
})
zapyle.filter('totalsubcategories',function($filter){
    return function(input){
        total = 0;
        for(i in input){
            total+=input[i]['value'].length;
        }
        return total;
    }
})
zapyle.controller('BuyController', function($scope, $filter, $http, $rootScope, loveService, admireService, $localStorage) {
    $scope.isMobile = false;
    if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent)
        || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))) $scope.isMobile = true;
    function show_loader(id, value) {
        document.getElementById(id).style.display = value ? 'block' : 'none';
    }
    var initial_query='';
    $scope.filter = null;
    $scope.subscriptionPage = false;
    search_query = checkSearch();
    initial_query = getInitialFilters();
    $scope.baseUrl = getBaseUrl();
    $scope.baseFilterUrl = getBaseFilterUrl();
    $scope.selected_filters = {
        'shop':[],
        'category':[],
        'product_category':[],
        'price':[-1,-1],
        'disc':[],
        'brand':[],
        'condition':[],
        'age':[],
        'style':[],
        'color':[],
        'occasion':[],
        'size':[],
    }
    function getBaseFilterUrl() {
        basefilterurl = '/filters/getEFilters/all/?'
        if (initial_query) {
            basefilterurl+=initial_query
        }
        if (getParameterByName('campaign')) {
            basefilterurl = basefilterurl + 'i_campaign=' + getParameterByName('campaign');
        }
        return basefilterurl
    }
    function getBaseUrl() {
        var pathArray = window.location.pathname.split( '?' );
        var baseurl = pathArray[0];
        if (getParameterByName('campaign')) {
            baseurl = baseurl + '?campaign=' + getParameterByName('campaign');
        }
        if (search_query!='') {
            baseurl = baseurl + '?' + search_query;
        }
        return baseurl
    }
    function checkSearch() {
        var filterArray = ['shop', 'brand', 'category', 'collections', 'product_category', 'color', 'occasion', 'style', 'product_collection'];
        var filters = [];
        var values = [];
        for (var i in filterArray) {
            if (getParameterByName(filterArray[i], null, 1)) {
                filters.push(filterArray[i])
                values.push(getParameterByName(filterArray[i], null, 1))
            }
        }
        initial_query = '';
        for(var k in filters) {
            filter = filters[k]
            if (filter == 'sub-category') {
                filter = 'product_category';
            }
            initial_query = initial_query + '&i_'+filter+values[k];
        }
        if (getParameterByName('search')) {
            initial_query = initial_query + '&search='+getParameterByName('search').replace(/ /g, '+');
        }
        return initial_query;
    }
    function getInitialFilters() {
        var pathArray = window.location.pathname.split( '/' );
        var filterArray = ['shop', 'brand', 'category', 'collection', 'product_category', 'color', 'occasion', 'style', 'product_collection'];
        var filters = [];
        var values = [];
        if (pathArray[4]) {
            filters = [pathArray[1], pathArray[3]];
            values = [pathArray[2], pathArray[4]];
        } else if (pathArray[2]) {
            filters = [pathArray[1]];
            values = [pathArray[2]];
            if (values[0].indexOf('subscription-') > -1) {
                $scope.subscriptionPage = true;
            }
        }
        if (search_query!='') {
            initial_query = search_query;
        } else {
            initial_query = '';
        }
        for(var k in filters) {
            filter = filters[k]
            if (filter == 'sub-category')
                filter = 'product_category'
            for (var i = 0; i < filterArray.length; i++) {
                if(filterArray[i] == filter)
                {
                    initial_query = initial_query + '&i_'+filter+'='+values[k];
                    if (filter == "shop"){
                        $scope.shops = values[k]
                    }
                    $scope.filter = filter

                    $scope.filter_value = pathArray[2]
                }
            }
        }
        return initial_query
    }
    var discount_rule = {"1":70,"2":50,"3":30,"4":10}
    function getQuery(){
        var q = ''
        for (var key in $scope.selected_filters) {
            if ($scope.selected_filters[key]!=''){
                if (key!='price') {
                    q+='&'+key+'='+$scope.selected_filters[key];
                    var k = {}
                    k[key] = $scope.selected_filters[key]
                }
                else{
                    if($scope.selected_filters['price'][0]>=0 && $scope.selected_filters['price'][1]>=0){
                        q+='&price='+$scope.selected_filters['price'][0]+','+$scope.selected_filters['price'][1]
                    }else{
                        if($scope.selected_filters['price'][0] >= 0){
                            q+='&price='+$scope.selected_filters['price'][0]+','
                        }else{
                            if($scope.selected_filters['price'][1] >= 0){
                                q+='&price=,'+$scope.selected_filters['price'][1]
                            }
                        }

                    }
                }
            }
        }
        return q
    }

    $scope.products = []
    $scope.getProducts = function(p){
        if($localStorage.backtobuy){
            $http.get('/filters/getProducts/'+p+'/?'+initial_query+'&perpage='+$localStorage.backtobuy*48).
                success(function(data, status, headers, config) {
                page = $localStorage.backtobuy
                $localStorage.backtobuy = 0
                if (data.status == "success"){
                    $scope.products = data.data.data
                    if (data.data.collection_data) {
                        $scope.custom_collection = data.data.collection_data
                        if($scope.custom_collection.show_timer) {
                            $('.flash_sale_timer').removeClass('is_hidden')
                            startTimer();
                        }
                    }
                    $scope.nextPage = data.data.next
                    $rootScope.overlay('filtered')
                }
            })
        }else{
            $http.get('/filters/getProducts/'+p+'/?'+initial_query+'&perpage=48').
                success(function(data, status, headers, config) {
                if (data.status == "success"){
                    $scope.products = data.data.data
                    if (data.data.collection_data) {
                        $scope.custom_collection = data.data.collection_data
                        if($scope.custom_collection.show_timer) {
                            $('.flash_sale_timer').removeClass('is_hidden')
                            startTimer();
                        }
                    }
                    $scope.nextPage = data.data.next
                    page = data.data.page
                    $rootScope.overlay('filtered')
                }
            })
        }
    }
    $scope.category = null
    $scope.size_type = null
    changeFilters = ["shop","category","disc","brand","age","condition","style","color","occasion","price","size_type","brand_alphas"]
    $scope.getFilterItems = function(field){
        // alert(field)
        if (field == 'product_category'){field='category'}
        if (field == 'size'){field='size_type'}
        $('.side_bar_inner > #loading').addClass('is_visible');
        $http.get($scope.baseFilterUrl + getQuery()).
            success(function(data, status, headers, config) {
            if (data.status == "success") {
                // alert(JSON.stringify(data.data))
                $('.side_bar_inner > #loading').removeClass('is_visible');
                $scope.filtersExist = false;
                if(field){
                    var index = changeFilters.indexOf(field)
                    if(index > -1){
                        changeFilters.splice(index, 1)
                    }
                }
                for(var i in changeFilters) {

                    $scope[changeFilters[i]] = data.data[changeFilters[i]]
                    // alert(JSON.stringify(data.data[changeFilters[i]]))
                    // Check if filters exist
                    if (changeFilters[i] == 'size_type') {
                        $scope[changeFilters[i]] = {}
                        for (var j in data.data[changeFilters[i]]) {
                            if (data.data[changeFilters[i]][j].size != null)
                                $scope.filtersExist = true;
                            $scope[changeFilters[i]][data.data[changeFilters[i]][j]['name']] = data.data[changeFilters[i]][j]['size']
                        }
                    } else if (data.data[changeFilters[i]] != null) {
                        $scope.filtersExist = true;
                    }
                }

                if(field){
                    changeFilters.push(field)
                }
                if($scope.category!==null) {
                    for(var i = 0; i < $scope.category.length; i++){
                        category = $scope.category[i];
                        try {
                            Object.defineProperty(category, 'value',
                                Object.getOwnPropertyDescriptor(category, 'sub_cats'));
                            delete category['sub_cats'];
                        } catch (err) {}
                    }
                }

                setTimeout(function(){
                    $('#minprice option[label='+$scope.selected_filters['price'][0]+']').prop('selected', true);
                    $('#maxprice option[label='+$scope.selected_filters['price'][1]+']').prop('selected', true);
                    $('select').material_select();
                    // if($scope.filter != 'shop' && shop){
                    //     shop.split(',').forEach(function (value) {
                    //         $("[data-name="+value+"].with-gap").prop('checked', true);
                    //         $("#"+value+".with-gap").prop('checked', true);
                    //     });
                    // }
                    // $('select').material_select()
                    if(field != "shop"){
                        setPrelovedFilter();
                        setBrandNewFilter();
                    }
                    $('.material-tooltip').remove();
                    $('.tooltipped').tooltip({delay: 50});
                });

            }
        })
    }
    $scope.refine = function(){
       $('.side_bar').addClass('is_visible');
       $('.top_level').removeClass('open').addClass('closed');
       $('#category > h6 .title').click();
    }
    $scope.applyMobileFilter = function(){
       $('.side_bar').removeClass('is_visible')
       $('.filters .accordion_item').removeClass('open');
       $('.filters .accordion_item').addClass('closed');
    }
    $scope.clearMobileFilter = function(){
        $scope.selected_filters = {
            'shop':[],
            'category':[],
            'product_category':[],
            'price':[-1,-1],
            'disc':[],
            'brand':[],
            'condition':[],
            'age':[],
            'style':[],
            'color':[],
            'occasion':[],
            'size':[],
        }
        $scope.getFilteredProducts(0);
    }
    $('body').on('click', '.pre_loved_option', function(){
        if ($(this).is(':checked') > 0) {
            $scope.selected_filters['shop'].push($(this).attr("id"))
        }else{
            var shop = $(this).attr('id')
            var index = $scope.selected_filters["shop"].indexOf(shop);
            if (index > -1) {
                $scope.selected_filters["shop"].splice(index, 1);
            }
        }
        setPrelovedFilter();
        $scope.getFilteredProducts(0,'shop');
    })
    $('body').on('click', '#pre_loved', function() {
        if ($(this).is(':checked') > 0) {
            $(this).parent().removeClass('partly_selected')
            $('.pre_loved_option').prop('checked', true);
            if($scope.selected_filters['shop'].indexOf("curated") == -1){
                $scope.selected_filters['shop'].push("curated")
            }
            if($scope.selected_filters['shop'].indexOf("market") == -1){
                $scope.selected_filters['shop'].push("market")
            }
        }else{
            $(this).parent().removeClass('selected')
            $('.pre_loved_option').prop('checked', false);
            var index = $scope.selected_filters["shop"].indexOf("curated");
            if (index > -1) {
                $scope.selected_filters["shop"].splice(index, 1);
            }
            var index = $scope.selected_filters["shop"].indexOf("market");
            if (index > -1) {
                $scope.selected_filters["shop"].splice(index, 1);
            }
        }
        $scope.getFilteredProducts(0,'shop');
    })

    $('body').on('click', '.brand_new_option', function(){
        if ($(this).is(':checked') > 0) {
            $scope.selected_filters['shop'].push($(this).attr("id"))
        }else{
            var shop = $(this).attr('id')
            var index = $scope.selected_filters["shop"].indexOf(shop);
            if (index > -1) {
                $scope.selected_filters["shop"].splice(index, 1);
            }
        }
        setBrandNewFilter();
        $scope.getFilteredProducts(0,'shop');
    })

    $('body').on('click', '#brand_new', function() {
        if ($(this).is(':checked') > 0) {
            $(this).parent().removeClass('partly_selected')
            $('.brand_new_option').prop('checked', true);
            if($scope.selected_filters['shop'].indexOf("designer") == -1){
                $scope.selected_filters['shop'].push("designer")
            }
            if($scope.selected_filters['shop'].indexOf("brand") == -1){
                $scope.selected_filters['shop'].push("brand")
            }
        }else{
            $(this).parent().removeClass('selected')
            $('.brand_new_option').prop('checked', false);
            var index = $scope.selected_filters["shop"].indexOf("designer");
            if (index > -1) {
                $scope.selected_filters["shop"].splice(index, 1);
            }
            var index = $scope.selected_filters["shop"].indexOf("brand");
            if (index > -1) {
                $scope.selected_filters["shop"].splice(index, 1);
            }
        }
        $scope.getFilteredProducts(0,'shop');
    })

    function setPrelovedFilter(){
        var total_option = $('.pre_loved_option').length
        var len = $('.pre_loved_option:checked').length
        if (len == total_option){
            $('#pre_loved').prop('checked', true).parent().addClass('selected').removeClass('partly_selected')
        }else if(len > 0){
            $('#pre_loved').prop('checked', false).parent().addClass('partly_selected').removeClass('selected')
        }else{
            $('#pre_loved').prop('checked', false).parent().removeClass('partly_selected').removeClass('selected');
        }
    }
    function setBrandNewFilter(){
        var total_option = $('.brand_new_option').length
        var len = $('.brand_new_option:checked').length
        if (len == total_option){
            $('#brand_new').prop('checked', true).parent().addClass('selected').removeClass('partly_selected')
        }else if(len > 0){
            $('#brand_new').prop('checked', false).parent().addClass('partly_selected').removeClass('selected')
        }else{
            $('#brand_new').prop('checked', false).parent().removeClass('partly_selected').removeClass('selected');
        }
    }

    $('body').on('click', '.web .filter_option_item input[type="checkbox"]', function() {
        
        filter_type = $(this).closest('.accordion_item.top_level').data('name')
        if(filter_type == 'product_category'){
            if ($(this).closest('.parent').length > 0) {     // If selected element is parent, select all children
                if ($(this).is(':checked') > 0) {
                    $(this).closest('.parent').siblings('.accordion_item_inner').find('input[type="checkbox"]').prop('checked',true);
                    $(this).parent().addClass('selected').removeClass('partly_selected')
                    $(this).closest('.parent').siblings('.accordion_item_inner').find('.filter_option_item').addClass('selected');
                } else {
                    $(this).closest('.parent').siblings('.accordion_item_inner').find('input[type="checkbox"]').prop('checked',false);
                    $(this).parent().removeClass('selected').removeClass('partly_selected')
                    $(this).closest('.parent').siblings('.accordion_item_inner').find('.filter_option_item').removeClass('selected');
                }
            } else {     // If selected element is not parent give selected or partly_selected to parent accordingly
                if ($(this).closest('.filter_options_list').find('input[type="checkbox"]:not(:checked)').length > 0) {
                    $(this).closest('.accordion_item_inner').siblings('.parent').removeClass('selected');
                    // $(this).closest('.accordion_item_inner').prop('checked', false)
                    if ($(this).closest('.filter_options_list').find('input[type="checkbox"]:checked').length == 0) {
                        $(this).closest('.accordion_item').children('h6').removeClass('show_clear')
                        $(this).closest('#product_category').children('h6').removeClass('show_clear')
                        $(this).closest('.accordion_item_inner').siblings('.parent').removeClass('partly_selected');
                    } else {
                        $(this).closest('.accordion_item').children('h6').addClass('show_clear')
                        $(this).closest('#product_category').children('h6').addClass('show_clear')
                        $(this).closest('.accordion_item_inner').siblings('.parent').addClass('partly_selected');
                        $(this).closest('.accordion_item_inner').siblings('.parent').children().prop('checked',false)
                    }
                } else  {
                    $(this).closest('.accordion_item_inner').siblings('.parent').removeClass('partly_selected');
                    $(this).closest('.accordion_item_inner').siblings('.parent').addClass('selected');
                }
            }
            var subcatList = $(".product_category_option:checked").map(function() {
                return $(this).data("ids");
            }).get();
            $scope.selected_filters['product_category'].splice(0)
            if(subcatList!=''){
                $scope.selected_filters['product_category'] = subcatList
            }
        }else{
            if ($(this).is(':checked') > 0) {
                $(this).closest('.filter_option_item').addClass('selected');
                if ($scope.selected_filters[filter_type].indexOf($(this).data('ids')) == -1)
                    $scope.selected_filters[filter_type].push($(this).data('ids'))
            } else {
                $(this).closest('.filter_option_item').removeClass('selected');
                if ($scope.selected_filters[filter_type].indexOf($(this).data('ids')) > -1){
                    var ids = $(this).data('ids')
                    var index = $scope.selected_filters[filter_type].indexOf(ids);
                    if (index > -1) {
                        $scope.selected_filters[filter_type].splice(index, 1);
                    }
                }
            }
        }
        exclude_filter = $(this).closest('.accordion_item.top_level').data('name')
        $scope.getFilteredProducts(0,exclude_filter)
    });

    $scope.getFilteredProducts = function(page,field){
        $scope.current_page = page;
        // $scope.show_loadMore = false;
        query = getQuery()
        updateURL(query)   
        $('.products_area > #loading').addClass('is_visible');
        $http.get('/filters/getEProducts/'+page+'/?'+initial_query+query+'&perpage=48').
            success(function(res, status, headers, config) {
            if (res.status == "success"){
                // console.log(res.data)
                if(page==0){
                    // $scope.products = rs.hits.hits;
                    $scope.products = res.data.data.map(function(i){
                        return i['_source']; 
                    });
                }else{
                    var data = res.data.data.map(function(i){
                        return i['_source']; 
                    });
                    for (var i=0; i<data.length; i++){
                        $scope.products.push(data[i]);
                    }
                    $('.loading_wrapper').removeClass('is_visible');
                }
                $('.products_area > #loading').removeClass('is_visible').removeClass('is_hidden');
                $scope.loading = false;
                $scope.total = res.data.total;
                // alert($scope.current_page)
                if ((page+1)*48 < $scope.total){
                    $scope.show_loadMore = true;
                }else{
                    $scope.show_loadMore = false;
                }  
                $scope.product_ids = res['data']['data'].map(function(i){
                    return i['_source']['id']; 
                }); 
                $http.post('/filters/get_love_and_offer/',{"ids":$scope.product_ids}).success(function(rs){
                    if (rs.status == 'success'){
                        d = rs.data
                        for(i in d){
                            for(j in $scope.products){
                                if (d[i]['id'] == $scope.products[j]['id']){
                                    $scope.products[j]["liked_by_user"] = d[i]["liked_by_user"]
                                    $scope.products[j]["offer"] = d[i]["offer"]
                                    $scope.products[j]["has_look"] = d[i]["has_look"]
                                }
                            }
                        }
                    }

                })        
            }
        })  
        if(field != 'sort'){
            $scope.getFilterItems(field);
        }
    }         
        
    function updateURL(query) {
        if (query) {
            if (search_query=='') {
                window.history.pushState("", "", window.location.origin + $scope.baseUrl + '?' + query);
            } else {
                window.history.pushState("", "", window.location.origin + $scope.baseUrl + query);
            }
        } else {
            window.history.pushState("", "", window.location.origin + $scope.baseUrl);
        }
    }
    function getParameterByName(name, url, initial) {
        if (!url) url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        if (initial) {
            var regex = new RegExp("[?&](i_)" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        }else {    
            var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        }
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }
    var typingTimer;
    var doneTypingInterval = 800;
    var $input = $('#searchBox');
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
    $scope.searchFilter = function(filter){
        var str = filter.string.replace(' ','+')
        window.history.pushState('', '', '/buy?search='+str.rtrim()+getSuggestedQuery(filter))
        location.reload();
    }
    $('.sort_option_item').click(function(){
        sort_id = $(this).data('ids')
        if(sort_id){
            $scope.selected_filters['sort'] = sort_id
        }else{
            $scope.selected_filters['sort'] = ''  //what's new        
        }
        $('.sort_option_item').removeClass('selected')
        $(this).addClass('selected')
        $scope.getFilteredProducts(0, 'sort');
        if(isMobile) {
            $('.sort').removeClass('is_visible')
        }
    })

    ///*************************Execution starts from here****************************///
    if(window.location.search){
//        if(getParameterByName('search')){
//            searchProducts();
//        }else{
//            // getting parameters from url and assign to obj //
            var product_category = getParameterByName('product_category');
            if(product_category){
                product_category.split(',').forEach(function (value) {
                    $scope.selected_filters['product_category'].push(parseInt(value))
               });
            }
            // if(category){
            //     product_category.split(',').forEach(function (value) {
            //         $scope.selected_filters['category'].push(parseInt(value))
            //    });
            // }
            var style = getParameterByName('style');if(style){style.split(',').forEach(function (value) {
                    $scope.selected_filters['style'].push(parseInt(value))
               });}
            var disc = getParameterByName('disc');if(disc){disc.split(',').forEach(function (value) {
                    $scope.selected_filters['disc'].push(parseInt(value))
               });}
            var shop = getParameterByName('shop');if(shop){shop.split(',').forEach(function (value) {
                    $scope.selected_filters['shop'].push((value))
               });}


            var brand = getParameterByName('brand');if(brand){brand.split(',').forEach(function (value) {
                    $scope.selected_filters['brand'].push(parseInt(value))
               });}
            var condition = getParameterByName('condition');if(condition){condition.split(',').forEach(function (value) {
                    $scope.selected_filters['condition'].push(parseInt(value))
               });}
            var age = getParameterByName('age');if(age){age.split(',').forEach(function (value) {
                    $scope.selected_filters['age'].push(parseInt(value))
               });}
            var color = getParameterByName('color');if(color){color.split(',').forEach(function (value) {
                    $scope.selected_filters['color'].push(parseInt(value))
               });}
            var occasion = getParameterByName('occasion');if(occasion){occasion.split(',').forEach(function (value) {
                    $scope.selected_filters['occasion'].push(parseInt(value))
               });}
            var size = getParameterByName('size');if(size){size.split(',').forEach(function (value) {
                    $scope.selected_filters['size'].push(value)
               });}
            var price = getParameterByName('price');
            if(price){
                var p = price.split(',')
                $scope.selected_filters['price'][0] = p[0];
                $scope.selected_filters['price'][1] = p[1];
            }
            var sort = getParameterByName('sort');
            if(sort){
                $scope.selected_filters['sort']=sort
                $('.sort_option_item.selected').removeClass('selected');
                $("[data-ids="+sort+"].sort_option_item").addClass('selected');
            }
            $scope.getFilteredProducts(0)
//        }
    }else{
        $scope.getFilteredProducts(0)
    }

    $('body').on('click', '.accordion_item > h6 .clear_btn', function() {
        $(this).closest('.accordion_item').find('input[type="checkbox"]').prop('checked', false).parent().removeClass('selected');
        $scope.selected_filters[$(this).closest('.accordion_item').data("name")].splice(0)
        if($(this).hasClass('price_clear')){
            $('#price').find('.filter_option_item').removeClass("selected")
            $scope.startValue = '';
            $scope.endValue = '';
            $scope.$apply();
            $('select').material_select();
            $scope.selected_filters['price'][0] = -1
            $scope.selected_filters['price'][1] = -1
            $scope.getFilteredProducts(0);
        }else{
            $scope.getFilteredProducts(0);
        }
    })

    $scope.minpriceChange = function(){
        if ($scope.startValue) {
            $scope.selected_filters['price'][0] = $scope.startValue
            $('.min_price').addClass('selected')
        }else{
            $scope.selected_filters['price'][0] = -1
        }
        for(i in $scope.price){
            $("#maxprice option:contains("+$scope.price[i].end_value+")").attr("disabled",false)
            if($scope.price[i].end_value <= $('#minprice option:selected').text()){
                $("#maxprice option:contains("+$scope.price[i].end_value+")").attr("disabled","disabled")
            }
        }
        setTimeout(function() { $('select').material_select() });
        $scope.getFilteredProducts(0,'price');
    }
    $scope.maxpriceChange = function(){
        if ($scope.endValue) {
            $scope.selected_filters['price'][1] = $scope.endValue
            $('.max_price').addClass('selected')
        }else{
            $scope.selected_filters['price'][1] = -1
        }
        for(i in $scope.price){
            $("#minprice option:contains("+$scope.price[i].start_value+")").attr("disabled",false)
            if($scope.price[i].start_value >= $('#maxprice option:selected').text()){
                $("#minprice option:contains("+$scope.price[i].start_value+")").attr("disabled","disabled")
            }
        }
        setTimeout(function() { $('select').material_select() });
        $scope.getFilteredProducts(0,'price');
    }
    $('body').on('click', '.filters .accordion_item > h6 .title', function() {
        if (!$(this).closest('.accordion_item').hasClass('open')) {
            var filter_type = $(this).data('name')
            var selectedIds = $("."+filter_type+"_option:checked").map(function() {
                return $(this).data("ids");
            }).get();
            openThisFilter($(this));
            if(isMobile) {
                closeOtherFilters($(this))
            }
        } else {
            closeThisFilter($(this));
        }
        $(this).closest('.parent').afterTime(500, function () {
            $(".side_bar").trigger("sticky_kit:recalc");
        });
    });
    $scope.love = function(p){
        if(ZL == 'True' && USER_NAME){
            p.liked_by_user=!p.liked_by_user
            if(p.liked_by_user){
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
    $scope.loadMore = function(){
        $('.loading_wrapper').addClass('is_visible')
        $('.products_area > #loading').addClass('is_hidden')
        $scope.current_page++;
        $scope.getFilteredProducts($scope.current_page)
    }
    $scope.shopFromDisabledOptions = function(obj, type){
        var flag = true
        if(type == "brandnew"){
            for(i in obj){
                if((obj[i]['id'] == 1 || obj[i]['id'] == 4) && obj[i]["doc_count"] > 0 ){
                    return false;
                }
            }
        }else{
            for(i in obj){
                if((obj[i]['id'] == 2 || obj[i]['id'] == 3) && obj[i]["doc_count"] > 0 ){
                    return false;
                }
            }
        }
        return true;
    }
    $(window).scroll(function() {
        if ($(window).scrollTop() > 0) {
            $('main').addClass('show_filters');
        } else {
            $('main').removeClass('show_filters');
        }
        if (($(window).scrollTop() > $('.products_view .products_area').offset().top + $('.products_view .products_area').height() - $(window).height() - 250) && !$scope.loading) {
            $('.products_view .view_all a').click();
            $scope.loading = true;
        }
    });
    var seconds;
    function startTimer() {
        seconds = $scope.custom_collection.end_time
        timer();
    }
    function timer() {
        var days        = parseInt(seconds/86400);
        var hours       = parseInt((seconds%86400)/3600);
        var minutes     = parseInt((seconds%3600)/60);
        var remainingSeconds = seconds % 60;
        if (remainingSeconds < 10) {
            remainingSeconds = "0" + remainingSeconds;
        }
        if(document.getElementById('countdown')!== null) {
            document.getElementById('countdown').innerHTML = days + ":" + hours + ":" + minutes + ":" + remainingSeconds;
            if (seconds == 0) {
                document.getElementById('countdown').innerHTML = "";
            } else {
                seconds--;
                setTimeout(function() {
                    timer();
                }, 1000);
            }
        }
    }
    $scope.checkShopFilter = function(obj, type){
        if (type == 'brand-new'){
            for (i in obj){
                if ((obj[i]['value'] == 'brand' || obj[i]['value'] == 'designer')){
                    // alert('aaa')
                    return true;
                }
            }
            return false;
        }else{
            for (i in obj){
                if ((obj[i]['value'] == 'curated' || obj[i]['value'] == 'market')){
                    // alert('aaa')
                    return true;
                }
            }
            return false;
        }
    }

    $scope.getSizes = function() {
        $http.get('/catalogue/getsizes/').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
                sizes = data.data;
                $scope.sizes = {};
                for (i in sizes) {
                    size = sizes[i];
                    if (size.category_type=='FW') {
                        $scope.sizes[size.id] = 'EU ' + size.eu_size;
                    } else if (size.category_type=='FS') {
                        $scope.sizes[size.id] = 'FREESIZE';
                    } else {
                        $scope.sizes[size.id] = size.size;
                    }
                }
            }
        })
    }
    $scope.getSizes();

    $scope.get_product = function(product) {
        $('.quick_product').removeClass('show');
        $http.get('/catalogue/singleproduct/'+ product.id +'/an/').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
                $scope.product = data.data;
                setTimeout(function() {
                    $('.quick_product').addClass('show');
                    $('.quick_product').attr('data-id', product.id);
                    $scope.current_image = $('.thumbnail:first-child img').data('image_url');
                    if ($scope.product.size.length == 1) {
                        $('.size_item').click();
                    }
                    $('#current_image').zoom({
                        touch:true,
                        on:'click',
                        onZoomIn: function(){
                          $(this).closest('#current_image').addClass('zooming');
                        },
                        onZoomOut: function(){
                          $(this).closest('#current_image').removeClass('zooming');
                        }
                    });
                    $('.thumbnail').first().click();
                });
            }
        }).error(function(response) {
           Materialize.toast(response.detail, 3000);
        });
    }

    $scope.set_current_image = function(image, event) {
        $scope.current_image = image;
        $('.thumbnails .selected').removeClass('selected');
        $(event.currentTarget).children('img').addClass('selected');
        $('.is_transparent').addClass('is_transparent');
        $('.zoomimage').addClass('is_visible');
        $('.current_image').children("img:first-child").attr("src", $(event.currentTarget).children("img").attr("src").replace('100x100','1000x1000'));
        $('.current_image').children("img:last-child").attr("src", $(event.currentTarget).children("img").attr("src").replace('.100x100',''));
    }

    $('body').on('click', '.mobile_zoom', function() {
        $('div.pinch-zoom').each(function () {
            new RTP.PinchZoom($(this), {});
        });
    });

    $scope.like = function(user){
        if(ZL == 'True' && USER_NAME!='None'){
            if(user.length){
                $scope.product.likes.me = []
                loveService.postlove($('.product_id').data('id'),'unlike');
                $('.love').removeClass('loved')
            }else{
                $scope.product.likes.me = [{'id':USER_ID, 'zap_username':USER_NAME}]
                loveService.postlove($('.product_id').data('id'),'like');
                $('.love').addClass('loved')
            }
        }else{
            $scope.$emit('setLoginPurpose', 'love a product' );
            $('.right_panel_inner > div').removeClass('is_visible');
            $($('.login_label').attr('data-activates')).addClass('is_visible');
            $('.right_panel').addClass('is_visible');
        }
    }

    $scope.set_quantities = function(size, event) {
        if(size.quantity>0){
            $('.size_item').removeClass('selected');
            $(event.currentTarget).addClass('selected');
            $('.max_quantity, .goto_btn').addClass('is_hidden');
            $('.cart_btn').removeClass('is_hidden');
            $scope.availble_qty = size.quantity;
            $scope.qty =  1
//            $scope.$apply()
            if($scope.availble_qty>1){
                $('.get_quantity').removeClass('is_hidden');
            }else{
                $('.get_quantity').addClass('is_hidden');
            }
            $('.size_info').text($(event.currentTarget).data('tooltip'));
        }
    }
    $('.plus').click(function(){
        if($scope.availble_qty>$scope.qty){
            $scope.qty=$scope.qty+1;
            $scope.$apply();
        }else{
            $('.max_quantity').removeClass('is_hidden');
        }
    });
    $('.minus').click(function(){
        if($scope.qty>1){
            $scope.qty=$scope.qty-1;
            $scope.$apply();
        }
    });

    $scope.gotoToCart = function(){
        $scope.cart();
        $('.overlay').removeClass('is_visible');
        $('.goto_btn').addClass('is_hidden');
        $('.cart_btn').removeClass('is_hidden')
        $('.right_panel_inner > div').removeClass('is_visible');
        $($('.goto_btn').attr('data-activates')).addClass('is_visible');
        $('.right_panel').addClass('is_visible');
        window.history.pushState('', '', window.location.href+'/#rp_cart')
    }
    $scope.addToCart = function(product=null, size=null, quantity=null){
        if (product == null) {
            product_id = $('.quick_product').data('id');
        } else {
            $scope.product = product;
            product_id = product.id;
        }
        if (size==null) {
            if(!$('.size_item.selected').length){
                Materialize.toast('Please select a Size.', 3000);
                return false;
            }
            size = $('.size_item.selected').data('id');
        }
        if (quantity==null) {
            quantity = $scope.qty;
            var available_size = $scope.product.size.length
            if(available_size==1){
                $("[data-id="+$scope.product.size[0]['id']+"]").addClass('selected')
                $scope.availble_qty = $scope.product.size[0]['quantity']
                if($scope.availble_qty>1){$('.get_quantity').removeClass('is_hidden')}
            }
        }
        if(ZL == 'True' && USER_NAME!='None') {
            var data = {'cart_data':{'quantity':quantity,'product':product_id,'size':size}}
            if ($scope.appliedOffer) {
                data['cart_data']['offer'] = $scope.appliedOffer;
            }
            $http.post('/zapcart/?web=true',data).
                success(function(rs, status, headers, config) {
                if (rs.status == "success"){
                    // $('.get_size_quantity').removeClass('is_visible')
//                    $('.cart_btn').addClass('is_hidden')
//                    $('.goto_btn').removeClass('is_hidden')
                    // $('.confirm_btn').addClass('is_hidden')
                    Materialize.toast(rs.data.message, 3000);
                    $('#toteBadge').text(rs.data.count)
                    clevertap.event.push("add_to_tote", {
                        "user_id":USER_ID,
                        "product_id":product_id,
                        "size":$('.size_item.selected').text(),
                        "quantity":quantity,
                        "price":$('.z_new').text().replace(',',''),
                    });
                }else{
                    Materialize.toast(rs.detail, 3000);
                }
            })
        } else {
            var count = parseInt($('#toteBadge').text())
            if($localStorage.tote){
                var cart_data = $localStorage.tote['cart_data']
                for(i in cart_data){
                    if(cart_data[i]['product'] == product_id && cart_data[i]['size'] == size){
//                        $('.cart_btn').addClass('is_hidden')
//                        $('.goto_btn').removeClass('is_hidden')
                        Materialize.toast("This item is already added in your tote.", 3000);
                        return false;
                    }
                }
            }else{
                $localStorage.tote = {'cart_data' : []}
            }
            $localStorage.tote['cart_data'].push({
                'product_quantity':quantity,'product':product_id,
                'quantity_available':$scope.availble_qty,
                'size':size,
                'product_image': $scope.product.image,
                'original_price' :$scope.product.original_price,
                'listing_price' : $scope.product.listing_price,
                'product_brand' : $scope.product.listing_price.brand,
                'title' : $scope.product.title,
                'product_size' : $scope.sizes[size],
                'offer': $scope.appliedOffer,
                'offer_benefit': $scope.product.listing_price - $scope.offerPrice,
                'id' : Math.floor((Math.random() * 100) + 1)
            })
            $('.get_size_quantity').removeClass('is_visible')
//            $('.cart_btn').addClass('is_hidden')
//            $('.goto_btn').removeClass('is_hidden')
            Materialize.toast("Item added successfully.", 3000);
            $('#toteBadge').text(++count)
    	}
    }

    $scope.get_looks = function(product) {
        $('.product_looks').removeClass('show');
        $http.get('/catalogue/looks_for_product/'+ product.id).
            success(function(data, status, headers, config) {
            if (data.status == "success"){
                $scope.looks = data.data;
                setTimeout(function() {
                    $('.product_looks').addClass('show');
                    $('select').material_select();
                    $('.looks .look_item:first-child').addClass('selected');
                    $('.looks .highlighter').css({'width': $('.look_item.selected').width()});
                });
            } else {
                Materialize.toast(data.detail, 3000);
            }
        }).error(function(response) {
           Materialize.toast(response.detail, 3000);
        });
    }

    $scope.get_look = function(blog, event) {
        if (!$(event.currentTarget).hasClass('selected')) {
            $('.looks .look_item').removeClass('selected');
            $(event.currentTarget).addClass('selected');
            $('.looks .highlighter').css({'left': $(event.currentTarget).offset().left - $('.looks .look_item:first-child').offset().left, 'width': $(event.currentTarget).width()});
            $http.get('/zapblog/post/'+ blog.id).
                success(function(data, status, headers, config) {
                if (data.status == "success"){
                    $scope.looks.look_data = data.data;
                    setTimeout(function() {
                        $('select').material_select();
                    });
                } else {
                    Materialize.toast(data.detail, 3000);
                }
            }).error(function(response) {
               Materialize.toast(response.detail, 3000);
            });
        }
    }

    $scope.addToCart_bulk = function() {
        items = $('.product_item.selected');
        if (items.length == 0) {
            Materialize.toast('Select products to add to Cart', 3000);
        } else {
            items.each(function() {
                if ($(this).find('.sizes select option:selected').length==0 || $(this).find('.sizes select option:selected').val()=='') {
                    Materialize.toast('Select sizes for the products you add to Tote.', 3000);
                    return false;
                } else {
                    product_id = $(this).data('id');
                    product = $filter('filter')($scope.looks.look_data.products, { id: product_id  }, true)[0];
                    size = $(this).find('.sizes select option:selected').val();
                    $scope.addToCart(product, size, 1);
                }
            });
        }
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

    $('body').on('click', '.look_layout .product_item *', function(event) {
        if (!$(this).is('a')) {
            if(!$(this).closest('.product_item').hasClass('sold_out')) {
                $(this).closest('.product_item').toggleClass('selected');
            }
        } else {
            event.stopPropagation();
        }
    });
});

zapyle.directive('imageonload', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            element.bind('load', function() {
                // alert('image is loaded');
                $('.is_transparent').removeClass('is_transparent')
                $('.zoomimage').removeClass('is_visible')
            });
        }
    };
});