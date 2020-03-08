$(document).ready(function() {
	$('#show-login').click(function() {
		$('.signup-module').hide(500);
		$('.signin-module').show(500);
	});
	$('#show-signup').click(function() {
		$('.signup-module').show(500);
		$('.signin-module').hide(500);
	});
	showRightContent(1);
	function showRightContent(k) {
		var copy = '.copy #' + String(k);
		var bg = '.bg #bg-' + String(k);
		var screenshot = '.phone #sc-' + String(k);
		
		$('.copy > div').removeClass('is_current');
		$('.bg > [id^="bg"]').removeClass('is_current');
		$('.phone [id^="sc"]').removeClass('is_current');
		
		$(copy).addClass('is_current');
		$(bg).addClass('is_current');
		$(screenshot).addClass('is_current');

		//alert('hi')
		k++;
		if (k>3) {
			k=1;
		};
		setTimeout(function(){ showRightContent(k); }, 5000);
	}
});

