jQuery.fn.extend({
    afterTime: function (sec, callback) {
        that = $(this);
        setTimeout(function () {
            callback.call(that);
        }, sec);
        return this;
    }
});
var customScroll = [];
function setCustomScroll () {
	scrollObjects = $('.custom_scroll');
	var scrollOptions = {
			scrollbars: 'custom',
			mouseWheel: true,
			preventDefault: false,
			interactiveScrollbars: true,
			shrinkScrollbars: 'scale',
			fadeScrollbars: true
		}
	scrollObjects.each(function( index ) {
		if ($(this).hasClass('brand_wrapper')) {
			scrollOptions.mouseWheel = false;
		}
		customScroll[index] = new IScroll(this, scrollOptions);
		$(this).attr('data-scrollgroup', index);
	});
}
var customHorizontalScroll = [];
function setHorizontalCustomScroll () {
	scrollObjects = $('.horizontal_custom_scroll');
	scrollObjects.each(function( index ) {
		customHorizontalScroll[index] = new IScroll(this, {
			scrollbars: true,
			scrollX: true,
			scrollY: false,
			interactiveScrollbars: true,
			shrinkScrollbars: 'clip',
			fadeScrollbars: false
		});
		$(this).attr('data-horizontalscrollgroup', index);
	});
}
var xScroll, zoomScroll;
var carouselScrolls = [];
function setCarousel(selector) {
	objects = $(selector);
	objects.each(function() {
		scroller = $(this).children('.scroller');
		if (scroller.children().first().find('.slide_width').length > 0) {
			slide_width = scroller.children().first().find('.slide_width').outerWidth(true)
		} else {
			slide_width = scroller.children().first().outerWidth(true)
		}
		var total_width = scroller.children().length * (slide_width + 20) + 50;
		scroller.css({'width': total_width});
		xScroll = new IScroll(this, {
			scrollX: true,
			scrollY: false,
			momentum: false,
			eventPassthrough: true,
			snap: '.slide',
			keyBindings: true,
		});
		carouselScrolls.push(xScroll);
		$(this).attr('data-carouselgroup', carouselScrolls.length - 1);
	});
}
function openAccordion(accordion) {
	accordion.siblings('.accordion_item_inner').css('transition', 'all 0s ease 0s');
	accordion.siblings('.accordion_item_inner').animate({
	    height: accordion.siblings('.accordion_item_inner').get(0).scrollHeight
	  }, 200, function() {
	  		$(this).closest('.accordion_item').addClass('open');
	  		$(this).css('transition', '');
	  });
}
function closeAccordion(accordion) {
	accordion.closest('.accordion_item').removeClass('open');
	accordion.siblings('.accordion_item_inner').animate({
	    height: 0
	  }, 0);
}
function closeSubFilters(filter) {
	subFilters = filter.find('.accordion_item.open');
	subFilters.each(function() {
		$(this).addClass('closed');
		$(this).removeClass('open');
	});
}
function closeOtherFilters(filter) {
	openFilters = filter.closest('.accordion_item').siblings('.accordion_item.open');
	openFilters.each(function() {
		$(this).addClass('closed');
		$(this).removeClass('open');
		closeSubFilters($(this));
	});
}
function openThisFilter(filter) {
	filter.closest('.accordion_item').removeClass('closed');
	filter.closest('.accordion_item').addClass('open');
}
function closeThisFilter(filter) {
	filter.closest('.accordion_item').addClass('closed');
	filter.closest('.accordion_item').removeClass('open');
	closeSubFilters(filter.closest('.accordion_item'));
}
var	threshold1, threshold2;
$(document).ready(function() {
	isMobile = false;
	if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent)
        || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))) isMobile = true;
	/****************** Materialize *****************************/
	$('.slider').slider({full_width: true});
	$('.parallax').parallax();

	$('.datepicker').pickadate({
		selectMonths: true, // Creates a dropdown to control month
		selectYears: 100 // Creates a dropdown of 15 years to control year
	});
	$('select').material_select();
	$('.scrollspy').scrollSpy();
	$('.tooltipped').tooltip({delay: 50});
	/****************** Discover *****************************/
	// $('.product_group.carousel').carousel({
	// 	'dist':0,
	// 	'shift': 20,
	// 	'padding': 20,
	// });

	/****************** Materialize End *****************************/
	$('body').on('click', '.glass, .close_btn', function() {
		if (!$(this).hasClass('cant_close')) {
			$(this).closest('.is_visible').removeClass('is_visible');
			$(this).closest('#bio_ep').css('display', 'none');
		}
	});
	$('body').on('click', '.get_size_quantity .close_btn', function() {
		$('.cart_btn').removeClass('is_hidden');
		$('.confirm_btn').addClass('is_hidden');
		$('.goto_btn').addClass('is_hidden');
	}) 
	$('body').on('click', '.modal-close', function() {
		$(this).closest('.modal').closeModal();
	});
	$('body').on('click', 'header .secondary.menu a.rp_trigger', function() {
		if(window.location.pathname != "/"){
			window.history.pushState('', '', window.location.pathname+'/')
		}
		$(this).addClass('is_active');
		$('.right_panel_inner > div').removeClass('is_visible');
		$($(this).attr('data-activates')).addClass('is_visible');
		$('.right_panel').addClass('is_visible');
	});
//	$('body').on('mouseover', 'header .primary.menu .menu_item', function() {
//		$(this).addClass('current');
//		$(this).siblings().removeClass('current');
//	});
	$('body').on('mouseover', '.sub_menus > div', function() {
		$('#'+$(this).attr('id')+'_parent').addClass('current');
		$('#'+$(this).attr('id')+'_parent').siblings().removeClass('current');
	});
	$('body').on('mouseleave', '.sub_menus > div', function() {
		$('#'+$(this).attr('id')+'_parent').removeClass('current');
	});
	$('body').on('mouseleave', 'header .primary.menu li', function() {
		$(this).removeClass('current');
	});
	$('body').on('click', '.overlay_trigger', function() {
		$($(this).data('overlay')).addClass('is_visible');
	});
	$('body').on('click', '.trigger', function() {
		if ($(this).hasClass('toggle')) {
			$($(this).data('activates')).toggleClass('is_visible');
		} else {
			$($(this).data('activates')).addClass('is_visible');
			if ($($(this).data('activates')).hasClass('show_only_one')) {
				$($(this).data('activates')).siblings().removeClass('is_visible');
			}
		}
	});
	$('body').on('click', '.expand_trigger.contracted', function() {
		$($(this).data('expands')).css('height',$($(this).data('expands')).children('.expandable_inner').outerHeight(true));
		$(this).removeClass('contracted');
		$(this).addClass('expanded');
	});
	$('body').on('click', '.expand_trigger.expanded', function() {
		$($(this).data('expands')).css('height','');
		$(this).removeClass('expanded');
		$(this).addClass('contracted');
	});
	$('body').on('mouseover', '.hover_trigger', function() {
		showClass = 'is_visible';
		if ($(this).hasClass('make_opaque')) {
			showClass = 'is_opaque';
		}
		$($(this).data('activates')).addClass(showClass);
		$($(this).data('activates')).siblings().removeClass(showClass);
	});
	$('body').on('mouseleave', '.hover_trigger.hide_on_leave', function() {
		showClass = 'is_visible';
		if ($(this).hasClass('make_opaque')) {
			showClass = 'is_opaque';
		}
		$($(this).data('activates')).removeClass(showClass);
	});
	$('body').on('mouseover', '#trending_menu .menu_option_item, .shop_tabs a', function() {
		$(this).addClass('current');
		$(this).siblings().removeClass('current');
	});
	$('body').on('click', '.right_panel_inner a', function() {
		if($(this)[0].hasAttribute("data-activates")) {
			$('.right_panel_inner > div').removeClass('is_visible');
			$($(this).attr('data-activates')).addClass('is_visible');
			$('.right_panel').addClass('is_visible');
			if ($(this).attr('data-activates') == '#my_info') {
				Materialize.updateTextFields();
			}
		}
	});

	$('body').on('click', '.options_header > div', function() {
		$($(this).attr('data-activates')).addClass('is_visible');
	});

	$('body').on('click', '.rp_trigger', function() {
		$($(this).attr('data-activates')).siblings().removeClass('is_visible');
		$($(this).attr('data-activates')).addClass('is_visible');
		$('.right_panel').addClass('is_visible');
	});
	$('body').on('click', '.custom_tab', function() {
		$(this).addClass('selected');
		$(this).siblings().removeClass('selected');
		$('#'+$(this).data('tabid')).addClass('is_visible');
		$('#'+$(this).data('tabid')).siblings().removeClass('is_visible');
	});
	$('header .logo .show_menu').click(function() {
		$('.left.menu').addClass('is_visible');
	});
	
	$('.input-field.radio li').click(function() {
		$(this).siblings().removeClass('is_selected');
		$(this).addClass('is_selected');
	});
	$('.show_hide').click(function() {
		if ($(this).hasClass('showing')) {
			$(this).closest('.text_input').find('input[type="text"]').attr('type', 'password');
			$(this).removeClass('showing');
			$(this).text('Show');
		} else {
			$(this).closest('.text_input').find('input[type="password"]').attr('type', 'text');
			$(this).addClass('showing');
			$(this).text('Hide');
		}
	});
	$('body').on('click', '.filters .accordion_item .parent > h6', function() {
		if (!$(this).closest('.accordion_item').hasClass('open')) {
			openThisFilter($(this).closest('.parent'));
		} else {
			closeThisFilter($(this).closest('.parent'));
		}
//		$(this).closest('.parent').afterTime(500, function () {
//	        $(".side_bar").trigger("sticky_kit:recalc");
	        // $('body').scrollToAnimate(this, 500, {offset: {top:-60} });
//	    });
	});
	$('body').on('click', '.accordion_item > h6', function() {
		if (!$(this).closest('.accordion').hasClass('filters')) {
			if (!$(this).closest('.accordion_item').hasClass('open')) {
				openAccordion($(this));
			} else {
				closeAccordion($(this));
			}
		}
	});

	$('body').on('click', '.selectable', function() {
	    if (!$(this).hasClass('disabled')) {
		    $(this).addClass('selected');
		}
	});
	$('body').on('click', '.check_box', function() {
		$(this).addClass('is_selected');
	});
	$('body').on('click', '.check_box.is_selected', function() {
		$(this).removeClass('is_selected');
	});
	$('body').on('click', '.radio.selectable', function() {
	    if (!$(this).hasClass('disabled')) {
		    $(this).siblings().removeClass('selected');
		}
	});
	$('body').on('click', '#payment_options .selectable', function() {
	    if (!$(this).hasClass('disabled')) {
            $(this).closest('#payment_options').find('.selectable').removeClass('selected');
            $(this).addClass('selected');
        }
	});
	$('body').on('click', '.select-wrapper.all_banks .dropdown-content', function() {
		if (!$(this).hasClass('disabled')) {
			$(this).closest('.select-wrapper').find('input').addClass('has_value');
		}
	});
	$('body').on('click', '#payment_options #credit, #payment_options #debit', function() {
		$(this).closest('#checkout').find('.screen_footer').attr('class', 'screen_footer card_cta');
	});
	$('body').on('click', '#payment_options #cod', function() {
		$(this).closest('#checkout').find('.screen_footer').attr('class', 'screen_footer cod_cta');
	});
	$('body').on('click', '#payment_options #saved_cards li.selectable', function() {
		$(this).closest('#checkout').find('.screen_footer').attr('class', 'screen_footer saved_card');
	});
	$('body').on('click', '#payment_options #net_banking li', function() {
		$(this).closest('#checkout').find('.screen_footer').attr('class', 'screen_footer net_banking');
	});
	$('body').on('click', '#order_review h6.title', function() {
		closeAccordion($('.step.open h6.title'));
		openAccordion($('#order_review h6.title'));
		$('#checkout').attr('class', 'is_visible step_1');
		cleverTapCheckout(1)
	});
	$('body').on('click', '#order_review_cta, #delivery_address h6.title', function() {
		$('#checkout').attr('class', 'is_visible step_2');
		$('.price').addClass('is_visible')
		closeAccordion($('.step.open h6.title'));
		openAccordion($('#delivery_address h6.title'));
		cleverTapCheckout(2)
	});
	$('body').on('click', '#payment_options h6.title', function() {
		$('#checkout').attr('class', 'is_visible step_3');
		closeAccordion($('.step.open h6.title'));
		openAccordion($('#payment_options h6.title'));
		cleverTapCheckout(3)
	});
	$('body').on('click', '.search .a_z_navigator li', function() {
	    if ($(this).text() == '#') {
	        var alpha = '*';
	    } else {
	        var alpha = '#scroll_' + $(this).text();
	    }
		first_alpha = $(this).closest('.scroll_parent').find('.scroll_this').find(alpha).first();
        $(this).closest('.scroll_parent').find('.scroll_this').first().scrollToAnimate(first_alpha, 500);
	});
	/******************************************* SELL PAGE **************************************/
	$('body').on('click', '.my_closet .products .previous', function() {
		$('.my_closet .carousel').carousel('prev');
	});
	$('body').on('click', '.my_closet .products .next', function() {
		$('.my_closet .carousel').carousel('next');
	});
	$('body').on('focus', '.top_banner .search input', function() {
		$('body').scrollToAnimate($(this), 500, {offset: {top:-100} });
	});
	$('.buy .page_content').css('min-height', $(window).height());
	$('body').on('click', '.scroll_top', function() {
		$('body').scrollToAnimate(0, 500);
	});
	$('body').on('click', '.slider .previous', function() {
		$(this).closest('.slider').slider('prev');
	});
	$('body').on('click', '.slider .next', function() {
		$(this).closest('.slider').slider('next');
	});
	$('.slider').on({
		mouseover: function () {
	        $(this).slider('pause');
	    },
	    mouseleave: function () {
	        $(this).slider('start');
	    }
	});
	$('body').on('click', '.sell_step a', function() {
		$(this).siblings('.tool_tip').first().addClass('is_visible');
	});
	$('body').on('click', '.side_nav a', function() {
		var address = $(this).attr('href');
		$('body').scrollToAnimate(address, 500, {offset: {top:-60} });
	});
	$('body').on('click', 'video', function() {
		if (this.paused) {
	        this.play();
	        $(this).closest('.video_container').removeClass('paused');
		} else {
	        this.pause();
	        $(this).closest('.video_container').addClass('paused');
	    }
	});
	$('body').on('click', '.video_container .icon-play', function() {
		var video = $(this).siblings('video').first().get(0);
		if (video.paused) {
	        video.play();
	        $(video).closest('.video_container').removeClass('paused');
		} else {
	        video.pause();
	        $(video).closest('.video_container').addClass('paused');
	    }
	});
	$('body').on('click', '.video_container + .modal-close, .video_pause', function() {
		var video = $(this).siblings('.video_container').first().find('video').first().get(0);
		video.pause();
	    $(video).closest('.video_container').addClass('paused');
	});
	$('body').on('click', '.icon-play.modal-trigger', function() {
		var video = $('#'+$(this).data('target')).find('video').first().get(0);
		video.play();
	    $(video).closest('.video_container').removeClass('paused');
	});
	$('body').on('click', '.tap_bar .search', function() {
		$('body').scrollToAnimate(0, 500);
		$('header #search input').focus();
	});
	$('body').on('click', '.show_offers', function() {
	    $(this).closest('.offers').toggleClass('show_all');
	});
});
var lastScrollTop = 0;
$(window).scroll(function() {
	if ($(window).scrollTop() > $('header').offset().top + $('header').height()) {
		$('header').addClass('white');
	} else {
		$('header').removeClass('white');
	}
	if ($(window).scrollTop() > $(window).height()) {
		$('body').addClass('show_scroll_top');
	} else {
		$('body').removeClass('show_scroll_top');
	}
});

function getFirstRange() {
    var sel = rangy.getSelection();
    return sel.rangeCount ? sel.getRangeAt(0) : null;
}

function insertHtmlAtCursor() {
	var sel = rangy.getSelection();
    var range = getFirstRange();
    if (range) {
	    var el = document.createElement("span");
	    $(el).addClass('mention current');
	    el.appendChild(document.createTextNode("@"));
	    range.insertNode(el);
	    rangy.getSelection().setSingleRange(range);
	}
	range.setStart(el,1);
	range.collapse(true);
    sel.removeAllRanges();
    sel.addRange(range);
    el.focus();
    return el;
}

function takeCursorOut(element) {
	var sel = rangy.getSelection();
    var range = getFirstRange();
    var el = $(element).find('.mention.current').get(0);
    $(el).removeClass('current');
    if (range) {
	    var textNode = document.createTextNode('\u00A0');
	    range.setStartAfter(el);
	    range.insertNode(textNode);
	    range.setStartAfter(textNode);
	    range.collapse(true);
	    sel.removeAllRanges();
	    sel.addRange(range);
	}
}

function update(element) {
  	var startPos = $('#compose_comment').offset();
  	var rect = document.getElementById('mention_suggestions');
  	if ($(element).offset().left + $(rect).width() > $(window).width()) {
		rect.style.right = "0px";
	} else {
		rect.style.left = $(element).offset().left - startPos.left + "px";
	}
	rect.style.bottom = startPos.top + $('#compose_comment').height() - $(element).offset().top + "px";
}

function setHorizontalMobScroll() {
	scrollObjects = $('.one_row.viewport');
	scrollObjects.each(function( index ) {
		scroller = $(this).find('.scroller').first();
		scroller.width(scroller.children().length * scroller.children().first().outerWidth(true))
	});
}

$(window).on("load",function() {
//	if(!isMobile) {
//		$(".side_bar").stick_in_parent({offset_top: 90});
//	}
	$('.modal-trigger').leanModal();
    $('body').on('click', '.discover_layout .previous, .step_carousel .previous', function() {
        num = parseInt($(this).siblings('.wrapper').attr('data-carouselgroup'));
        carouselScrolls[num].prev();
    });
    $('body').on('click', '.discover_layout .next,  .step_carousel .next', function() {
        num = parseInt($(this).siblings('.wrapper').attr('data-carouselgroup'));
        carouselScrolls[num].next();
    });
	setHorizontalMobScroll();
    // setCarousel('.product_group .products');
    setCarousel('.user_group .users');
    setCarousel('.step_carousel .wrapper');
    if($(window).width() <= 480){
        setCarousel('.featured_closet .products');
    }
    setCustomScroll();
    setHorizontalCustomScroll();
});