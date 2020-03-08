$(document).ready(function() {
	$('body').attr('id', window.location.href.substr(window.location.href.lastIndexOf('/') + 1));
	$('.nav-bar li').removeClass('selected');
	$('.nav-bar').find('#' + window.location.href.substr(window.location.href.lastIndexOf('/') + 1)).addClass('selected');
	$(window).on('hashchange', function(e){
	    $('body').attr('id', window.location.href.substr(window.location.href.lastIndexOf('/') + 1));
	    $('.nav-bar li').removeClass('selected');
	    $('.nav-bar').find('#' + window.location.href.substr(window.location.href.lastIndexOf('/') + 1)).addClass('selected');
	});
	 $(window).scroll(function(){ 
	     if ($(window).scrollTop() >= $('.main-content').offset().top){
	     	$('header').addClass('is_fixed');
	     }
	     else {
	     	$('header').removeClass('is_fixed');
	     }
	 });
	 $(window).click(function(event) { 
        if(!$(event.target).closest('.logged-in').length) {
            if($('.user-options').hasClass("is_visible")) {
                $('.user-options').removeClass('is_visible');
            }
        }        
	});
	$('body').on('click', '.close, .glass', function() {
		$(this).closest('.pri-overlay').removeClass('is_visible');
	});
	
});

