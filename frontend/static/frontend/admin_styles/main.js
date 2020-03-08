$(document).ready(function() {
	$('.glass').click(function() {
		$('.pri-overlay').removeClass('is_visible');
	});
/********************* HEADER **********************************/
	$('#show-menu').click(function() {
		if ($('#show-menu.icon-menu').length) {
			$('.nav-bar').css({'top':0});
			$('.signup-login').css({'top':'-60px'});
			$(this).removeClass('icon-menu');
			$(this).addClass('icon-cancel-1');
		} else {
			$('.nav-bar').css({'top':'-60px'});
			$('.signup-login').css({'top':'0px'});
			$(this).addClass('icon-menu');
			$(this).removeClass('icon-cancel-1');
		}	
	});
	$('.logged-in').click(function() {
		$('.user-options').toggleClass('is_visible');
	});
	$('.signup-login-links a').click(function() {
		$('#signup-login').addClass('is_visible');
	});
	$('#signup-login .close').click(function() {
		$('#signup-login').removeClass('is_visible');
	});
/********************* HOME PAGE *******************************/
	$('#show-login').click(function() {
		$('.signup-module').hide(500);
		$('.signin-module').show(500);
	});
	$('#show-signup').click(function() {
		$('.signup-module').show(500);
		$('.signin-module').hide(500);
	});
	$('.home .copy').css({'height':$('.copy > div:first-child').height()});
	if ($('body.home').length) {
		showRightContent(1);
	};
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

/********************* ONBOARDING PAGE *******************************/
	$('.style-card').mouseover(function() {
		$(this).addClass('current');
		current = $(this).find('.is_current');
		setTimeout(function() { changeImage(current);},200);
	});
	$( ".style-card" ).mouseout(function() {
		$(this).removeClass('current');
	});
	$('#onboarding-name .button a').click(function() {
		$('#onboarding-style').css({'display':'block'});
		$('#onboarding-name').css({'display':'none'});
	});

	$('.style-card').click(function() {
		$(this).toggleClass('is_selected');
		if ($('.style-card.is_selected').length) {
			$('#onboarding-style .footer .button').removeClass('is_disabled');
		} else {
			$('#onboarding-style .footer .button').addClass('is_disabled');
		}
	});
	
	
	$('#onboarding-style .button a').click(function() {
		$('#onboarding-size').css({'display':'block'});
		$('#onboarding-style').css({'display':'none'});
	});
	$('.size').click(function() {
		$(this).toggleClass('is_selected');
		if ($('.size.is_selected').length) {
			$('#onboarding-size .footer .button').removeClass('is_disabled');
		} else {
			$('#onboarding-size .footer .button').addClass('is_disabled');
		}
	});
	$('#onboarding-size .button a').click(function() {
		$('#onboarding-brands').css({'display':'block'});
		$('#onboarding-size').css({'display':'none'});
	});
	$('.brand').click(function() {
		$(this).toggleClass('is_selected');
		if ($('.brand.is_selected').length) {
			$('#onboarding-brands .footer .button').removeClass('is_disabled');
		} else {
			$('#onboarding-brands .footer .button').addClass('is_disabled');
		}
	});
	$('#onboarding-brands .button a').click(function() {
		$('#onboarding-brands').css({'display':'none'});
	});
/********************* BUY PAGE *******************************/
	
	$('.view-switch > span > span').click(function() {
		$('.view-switch .is_selected').removeClass('is_selected');
		$(this).addClass('is_selected');
		$('[class*="-view"].content').addClass('is_hidden');
		$('.'+$(this).attr('id')).removeClass('is_hidden');
	});
	$( ".product-card" ).mouseover(function() {
		$(this).addClass('current');
		current = $(this).find('.is_current');
		setTimeout(function() { changeImage(current);},500);
	});
	$( ".product-card" ).mouseout(function() {
		$(this).removeClass('current');
	});
	function changeImage(current) {
		if (current.closest('.current').length && current.siblings().length) {
			current.removeClass('is_current');
			if (current.next().length) {
				current=current.next();
			} else {
				current=current.siblings().eq(0);
			}
			current.addClass('is_current')
			setTimeout(function() { changeImage(current);},2000);	
		}	
	}

/********************* PRODUCT PAGE *******************************/
	$('.thumbnails li').click(function() {
		$('.thumbnails li').removeClass('is_current');
		$(this).addClass('is_current');
		$('.product-images .large img').attr('src', $('.thumbnails .is_current img').attr('src'))
	});
	$('.normal-sizes .size').click(function() {
		$('.normal-sizes .size').removeClass('is_selected');
		$(this).addClass('is_selected');
	});
	$('#minus').click(function() {
		if ($('#quantity').html()>1) {
			$('#quantity').html($('#quantity').html()-1);
		}
	});
	$('#plus').click(function() {
		if ($('#quantity').html()<$('#quantity').attr('data-max-quantity')) {
			$('#quantity').html(+($('#quantity').html())+1);
		}
	});
/********************* CHECKOUT PAGE ********************************/
	$('#show-coupon').click(function() {
		$('.apply-coupon').addClass('show');
	});
	$('.address-card').click(function() {
		$('.address-card').removeClass('is_selected');
		$(this).addClass('is_selected');
	});
	$('.new-address-card').click(function() {
		$('#add-address').fadeIn(500);
	});
	$('#add-address .cancel').click(function() {
		$('#add-address').fadeOut(500);
	})
/********************* DISCOVER PAGE *******************************/
	$('.video').click(function() {
		$('#zap-video').addClass('is_visible');
		$('#zap-video .video-frame').html('<iframe width="100%" height="100%" src="https://www.youtube.com/embed/Bbd3Zi-6V-o?autoplay=1" frameborder="0" allowfullscreen></iframe>');
	});
	$('#zap-video .close, #zap-video .glass').click(function() {
		$('#zap-video').removeClass('is_visible');
		$('#zap-video .video-frame').html('');
	});
});
