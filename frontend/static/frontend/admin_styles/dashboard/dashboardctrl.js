(function(angular) {
  'use strict';
angular.module('dashboardApp', [])
    .config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('[[').endSymbol(']]')})

    .controller('DashboardCtrl', function($scope,$http){//, AuthUser, $state, $http) {
    
    $scope.total = {
        't_users' : 0,
        'users' : 0,
        't_products' : 0,
        'products' : 0,
        't_orders' : 0,
        'orders' : 0,
        't_returns':0,
        'returns':0
    };
    $scope.device = {
        'android_today' : 0,
        'android_total' : 0,
        'ios_today' : 0,
        'ios_total' : 0,
        'website_today' : 0,
        'website_total' : 0,
        'fb_today':0,
        'fb_total':0
    };
    function load_user_details(date){
        $http({
            method: 'POST',
            url: "/dashboard/?action=users&date="+date,
        }).then(function successCallback(response) {
            $scope.users = response.data.users
            }, function errorCallback(response) {
            console.log(response);
        });
    }
    function load_user_details_by_device(){
        $http({
            method: 'POST',
            url: "/dashboard/?action=device",
        }).then(function successCallback(response) {
            $scope.device = response.data.total
            load_user_details()
            }, function errorCallback(response) {
            console.log(response);
        });
    }

    $scope.load_dashboard = function(retry){    
        $http({
            method: 'POST',
            url: "/dashboard/?action=graph",
        }).then(function successCallback(response) {
            if ($scope.joined_last >= 0 || $scope.logged_last >= 0){
                if($scope.joined_last != response.data.joined.slice(-1)[0] || $scope.logged_last != response.data.logged.slice(-1)[0]){                    
                    $scope.load_graph(response.data.dates,response.data.joined,response.data.logged);                
                    $scope.joined_last = response.data.joined.slice(-1)[0]
                    $scope.logged_last = response.data.logged.slice(-1)[0]
                }
            }
            else{
                $scope.load_graph(response.data.dates,response.data.joined,response.data.logged);
                $scope.joined_last = response.data.joined.slice(-1)[0];
                $scope.logged_last = response.data.logged.slice(-1)[0];

            }
            $scope.total = response.data.total;
            if (!retry){
                $scope.load_listing_graph()
            }
             
        }, function errorCallback(response) {
            console.log(response);
        }); 
    };
    $scope.load_dashboard();
    setInterval(function() {
        $scope.load_dashboard("retry");
        $scope.load_listing_graph("retry");
    }, 20000);


    $scope.load_graph = function(dates,joined,logged){
            
    $('#container').highcharts({
        chart: {
            type: 'spline'
        },
        title: {
            text: 'Last 10 days Users Joined and Logged'
        },
        // subtitle: {
        //     text: 'Source: WorldClimate.com'
        // },
        xAxis: {
            categories : dates,
            crosshair: true
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Users (count)'
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y}</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true
        },
        plotOptions: {
            spline: {
                dataLabels: {
                    enabled: true
                },
                enableMouseTracking: true
            },
            // column: {
            //     // pointPadding: 0.2,
            //     borderWidth: 0
            // },
            series: {
                cursor: 'pointer',
                point: {
                    events: {
                        click: function (uuuu) {
                            load_user_details(this.category);
                        }
                    }
                }
            }
        },
        series: [{
            color: '#0066FF',
            name: 'Logged',
            data: logged
        }, {
            color: '#FF0000',
            name: 'Joined',
            data: joined
        }]
    })}

    $scope.load_listing_graph = function(retry){
        $http({
            method: 'POST',
            url: "/dashboard/?action=listing_graph"
        }).then(function successCallback(response) {
            if ($scope.listing_last >= 0){
                if($scope.listing_last != response.data.listing.slice(-1)[0]){                    
                    $scope.show_listing_graph(response);                
                    $scope.listing_last = response.data.listing.slice(-1)[0]
                }
            }
            else{
                $scope.show_listing_graph(response);
                $scope.listing_last = response.data.listing.slice(-1)[0]

            }
            if (!retry){
                $scope.load_order_graph()
            }
            
             
        })}
        $scope.load_order_graph = function(){
        $http({
            method: 'POST',
            url: "/dashboard/?action=order_graph",
        }).then(function successCallback(response) {
            $('#order_graph').highcharts({
                chart: {
                    type: 'spline'
                },
                title: {
                    text: 'Last 10 days Orders'
                },
                // subtitle: {
                //     text: 'Source: WorldClimate.com'
                // },
                xAxis: {
                    categories : response.data.dates,
                    crosshair: true
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'Orders (count)'
                    }
                },
                tooltip: {
                    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                        '<td style="padding:0"><b>{point.y}</b></td></tr>',
                    footerFormat: '</table>',
                    shared: true,
                    useHTML: true
                },
                plotOptions: {
                    spline: {
                        dataLabels: {
                            enabled: true
                        },
                        enableMouseTracking: true
                    },
                    // column: {
                    //     // pointPadding: 0.2,
                    //     borderWidth: 0
                    // },
                    series: {
                        cursor: 'pointer',
                        point: {
                            events: {
                                click: function (uuuu) {
                                    load_user_details(this.category);
                                }
                            }
                        }
                    }
                },
                series: [{
                    color: '#20ed90',
                    name: 'Orders',
                    data: response.data.order
                }]
            })
            load_user_details_by_device()
             
        })}



        $scope.show_listing_graph = function(response){
            $('#listing_graph').highcharts({
                chart: {
                    type: 'spline'
                },
                title: {
                    text: 'Last 10 days Listing'
                },
                // subtitle: {
                //     text: 'Source: WorldClimate.com'
                // },
                xAxis: {
                    categories : response.data.dates,
                    crosshair: true
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'Listings (count)'
                    }
                },
                tooltip: {
                    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                        '<td style="padding:0"><b>{point.y}</b></td></tr>',
                    footerFormat: '</table>',
                    shared: true,
                    useHTML: true
                },
                plotOptions: {
                    spline: {
                        dataLabels: {
                            enabled: true
                        },
                        enableMouseTracking: true
                    },
                    // column: {
                    //     // pointPadding: 0.2,
                    //     borderWidth: 0
                    // },
                    series: {
                        cursor: 'pointer',
                        point: {
                            events: {
                                click: function (uuuu) {
                                    load_user_details(this.category);
                                }
                            }
                        }
                    }
                },
                series: [{
                    color: '#dc2479',
                    name: 'Listings',
                    data: response.data.listing
                }]
            })
        };
    // $('.grid-stack').gridstack({
    //     width: 12,
    //     draggable: {
    //         handle: '.drag-heading',
    //     }

    // });
    // var grid = $('.grid-stack').data('gridstack');
    // var positions = {}
    // $('.grid-stack').on('change', function(e, items) {
    //     for (i = 0; i < items.length; i++) {
    //         positions[items[i].el.context.id] = {
    //             'x': items[i].x,
    //             'y': items[i].y
    //         }
    //     }
    //     $http.get('/ng/dash_home/?position=' + JSON.stringify(positions))
    //     positions_global = positions
    // })
    // $.each((positions_global), function(id, pos) {
    //     grid.update($("#" + id)[0], pos['x'], pos['y'])
    // })

    // $http({
    //     url: '/ng/dash_home/',
    //     method: "GET"
    // }).success(function(response) {
    //     $scope.dateresponse = response[0]
    //     $scope.top_badge = response[1]
    //     $scope.top_users = response[2]
    //     $scope.new_mem = response[3]
    //     $http({
    //         url: '/ng/dash_home/',
    //         method: "GET",
    //         params: {
    //             'limit_exceeded': true
    //         }
    //     }).success(function(response) {
    //         $scope.org_status = response
    //     })
    // })
})
})(window.angular);