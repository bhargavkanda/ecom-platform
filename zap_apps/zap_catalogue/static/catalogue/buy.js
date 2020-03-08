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
zapyle.controller('BuyController', function($scope, $http, $rootScope, loveService, admireService, $localStorage) {
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
        basefilterurl = '/filters/getFilters/all/?'
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
        var filterArray = ['shop', 'brand', 'category', 'collection', 'product_category', 'color', 'occasion', 'style', 'product_collection'];
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
                    $scope.filter = filter
                    $scope.filter_value = pathArray[2]
                }
            }
        }
        return initial_query
    }
    function getQuery(){
        var q = ''
        for (var key in $scope.selected_filters) {
            if ($scope.selected_filters[key]!=''){
                if (key!='price') {
                    q+='&'+key+'='+$scope.selected_filters[key];
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
        return q;
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
    changeFilters = ["shops","category","disc","brands","age","condition","styles","colors","occasions","price","size_type"]
    $scope.getFilterItems = function(field){
        // alert(field)
        $http.get($scope.baseFilterUrl + getQuery()).
            success(function(data, status, headers, config) {
            if (data.status == "success") {
                $scope.filtersExist = false;
                if(field){
                    var index = changeFilters.indexOf(field)
                    if(index > -1){
                        changeFilters.splice(index, 1)
                    }
                }
                for(var i in changeFilters) {
                    $scope[changeFilters[i]] = data.data[changeFilters[i]]
                    // Check if filters exist
                    if (changeFilters[i] == 'size_type') {
                        for (var j in data.data[changeFilters[i]]) {
                            if (data.data[changeFilters[i]][j].size != null)
                                $scope.filtersExist = true;
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
                    if(field != "shops"){
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
        $scope.getFilteredProducts(1);
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
        $scope.getFilteredProducts(1,'shops');
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
        $scope.getFilteredProducts(1,'shops');
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
        $scope.getFilteredProducts(1,'shops');
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
        $scope.getFilteredProducts(1,'shops');
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
        exclude_filter = $(this).closest('.accordion_item.top_level').attr('id')
        $scope.getFilteredProducts(1,exclude_filter)
    });

    $scope.page = 1
    $scope.getFilteredProducts = function(page,field){
        if(page==undefined){page=1}
        $('.products_view > #loading').addClass('is_visible');
        query = getQuery()
        updateURL(query)
        $http.get('/filters/getProducts/'+page+'/?'+initial_query+query+'&perpage=48').
            success(function(data, status, headers, config) {
            if (data.status == "success"){
                $('.loading_wrapper').removeClass('is_visible');
                $('.sort').removeClass('is_hidden');
                $scope.page = page
                $('.products_view > #loading').removeClass('is_visible');
                $scope.nextPage = data.data.next
                if (data.data.collection_data) {
                    $scope.custom_collection = data.data.collection_data
                    if($scope.custom_collection.show_timer) {
                        $('.flash_sale_timer').removeClass('is_hidden')
                        startTimer();
                    }
                }
                if(page==1){
                    $scope.products = data.data.data
                }else{
                    var data = data.data.data
                    for (var i=0; i<data.length; i++){
                        $scope.products.push(data[i]);
                    }
                    $localStorage.backtobuy = page
                }
                setTimeout(function(){
                    if ($(window).scrollTop() > $('.products_area .product_card:last-child').offset().top) {
                        $('body').scrollToAnimate($('.products_area .product_card:last-child'), 500, {offset: {top:-120} });
                    } else {
                        $('body').scrollToAnimate('+=1px', 0);
                    }
                    $('.products').css('min-height', 'unset');
                })
            }
        })
        $scope.getFilterItems(field); //update filter items after select/deselect an item.
        $scope.searchFlag = false;
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
        $scope.getFilteredProducts();
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
            $scope.getFilteredProducts(1)
//        }
    }else{
        $scope.getFilteredProducts(1)
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
            $scope.getFilteredProducts();
        }else{
            $scope.getFilteredProducts();
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
        $scope.getFilteredProducts(1,'price');
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
        $scope.getFilteredProducts(1,'price');
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
        $scope.getFilteredProducts(++$scope.page)
    }
    $scope.shopFromDisabledOptions = function(obj, type){
        var flag = true
        if(type == "brandnew"){
            for(i in obj){
                if((obj[i]['id'] == 1 || obj[i]['id'] == 4) && obj[i]["disabled"] == false ){
                    return false;
                }
            }
        }else{
            for(i in obj){
                if((obj[i]['id'] == 2 || obj[i]['id'] == 3) && obj[i]["disabled"] == false ){
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
})