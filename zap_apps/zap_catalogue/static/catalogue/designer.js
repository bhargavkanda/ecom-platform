zapyle.controller('DesignerController', function($scope, $http, admireService) {
	$http.get('/catalogue/seller_closet/1/?closet=designer').
	success(function(rs){
		if(rs.status == 'success'){
			$scope.designers = rs.data.data
		}
		// alert(JSON.stringify(rs))
	})
	$scope.admire = function(designer){
        if(ZL == 'True' && USER_NAME!='None'){
            designer.admiring=!designer.admiring
            if (designer.admiring){
                admireService.postadmire(designer.id,'admire');
            }
            else{
                admireService.postadmire(designer.id,'unadmire');
            }
        }else{
            $scope.$emit('setLoginPurpose', 'admire a user' );
            $('.right_panel_inner > div').removeClass('is_visible');
            $($('.login_label').attr('data-activates')).addClass('is_visible');
            $('.right_panel').addClass('is_visible');
        }
    }
    // $('li.tab').click(function(){
    // 	window.location = '/buy/'+$(this).data('tab');
    // })
   
})