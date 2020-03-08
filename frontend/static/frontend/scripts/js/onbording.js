function changeImage(current) {
    if (current.closest('.current').length) {
        current.removeClass('is_current');
        if (current.next().length) {
            current = current.next();
        } else {
            current = current.siblings().eq(0);
        }
        current.addClass('is_current')
        setTimeout(function() {
            changeImage(current);
        }, 2000);
    }
}
$( "div" ).delegate( ".style-card", "click", function() {
    $(this).toggleClass('is_selected');
    if ($('.style-card.is_selected').length) {
        $('#onboarding-style .footer .button').removeClass('is_disabled');
    } else {
        $('#onboarding-style .footer .button').addClass('is_disabled');
    }
});
$( "div" ).delegate( ".style-card", "mouseover", function() {
  // code here
  $(this).addClass('current');
  console.log('addClass');
  current = $(this).find('.is_current');
    setTimeout(function() {
        changeImage(current);
    }, 1000);
});
$( "div" ).delegate( ".style-card", "mouseout", function() {
  // code here
  $(this).removeClass('current');
  console.log('removeClass');
});

$('#onboarding-style .footer .button').addClass('is_disabled');

// $('.style-card').click(function() {
//     $(this).toggleClass('is_selected');
//     if ($('.style-card.is_selected').length) {
//         $('#onboarding-style .footer .button').removeClass('is_disabled');
//     } else {
//         $('#onboarding-style .footer .button').addClass('is_disabled');
//     }
// });
// $('#onboarding-size .button a').click(function() {
//     $('#onboarding-brands').addClass('is_visible');
//     $('#onboarding-size').removeClass('is_visible');
// });
// $('#onboarding-brands .button button').click(function() {
//     $('#onboarding-brands').removeClass('is_visible');
// });
// $('.style-card').on("mouseover", function(evt) {
// // $('.style-card').mouseover(function() {
//     console.log('addClass');
//     $(this).addClass('current');
//     current = $(this).find('.is_current');
//     setTimeout(function() {
//         changeImage(current);
//     }, 1000);
// });
// $(".style-card").mouseout(function() {
//     $(this).removeClass('current');
// });


// moved to controller
// $('#onboarding-name .button .submit').click(function() {
//  alert("asdsad")
//  $('#onboarding-style').css({'display':'block'});
//  $('#onboarding-name').css({'display':'none'});
// });





// $('#onboarding-style .button a').click(function() {
//     $('#onboarding-size').addClass('is_visible');
//     $('#onboarding-style').removeClass('is_visible');
// });


// $('.brand').click(function() {
//     $(this).toggleClass('is_selected');
//     if ($('.brand.is_selected').length) {
//         $('#onboarding-brands .footer .button').removeClass('is_disabled');
//     } else {
//         $('#onboarding-brands .footer .button').addClass('is_disabled');
//     }
// });

// $(window).bind("load", function() {
// $('.body .size').click(function() {
 //                 if ($(this).hasClass('is_selected')) {
 //                     $(this).removeClass('is_selected');
//                 } else {
//                     $(this).addClass('is_selected');
 //                 }
//             });

// });