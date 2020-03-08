function previewSocialPost(embed_code) {
	$('.pri-overlay.social_embed .preview').html(embed_code);
}

function previewZapCTA(button) {
	url = $(button).siblings('.url').val();
	text = $(button).siblings('.cta_text').val();
	cta = '<a class="zapyle_cta" href="' + url + '">' + text + '</a>';
	preview = $('.pri-overlay.zap_cta .preview').html(cta);
	if ($(button).siblings('.new_tab:checked').length>0) {
		preview.find('a').attr('target','_blank');
	};
}
// var result;
function previewZapPost(response) {
	product_card = '<div class="product-card"><div class="product-display"><a target="_blank" href=""><img class="product-image" src=""></a></div><div class="brand"><a target="_blank" href=""></a></div><span class="price"><span class="discount"></span></span></div>';
	x = $('.pri-overlay.zap_embed .preview').html(product_card);
	card = x.children('.product-card');
	card.find('a').attr('href','http://staging.zapyle.com/#/product/'+response.data.id);
	card.find('.product-image').attr('src', 'http://staging.zapyle.com'+response.data.image1);
	card.find('.brand a').html(response.data.brand.brand);
	card.find('.price .discount').html(parseInt(response.data.discount*100)+'% off');
	if ($('input[name="user-preview"]:checked').length > 0) {
		user_card = '<div class="seller-info"><a target="_blank" href=""><img src=""><span class="name"></span></a></div>';
		card.prepend(user_card);
		card.find('.seller-info a').attr('href','http://staging.zapyle.com/#/profile/'+response.data.user.id);
		card.find('.seller-info img').attr('src', response.data.user.profile_pic);
		card.find('.seller-info .name').html('@'+response.data.user.zap_username);
	}
	if ($('input[name="use-cta"]:checked').length > 0) {
		engagement_block = '<span class="engagement"><span class="love icon-heart-empty"></span><span class="share icon-share"><ul><li class="icon-facebook">fb</li><li class="icon-twitter">tw</li><li class="icon-pinterest">pt</li><li class="icon-instagram">ins</li></ul></span></span>';
		card.find('.price').append(engagement_block);
	}
}

function previewImage(result) {
	var html= "<img src="+result.toDataURL('image/jpeg')+">";
	$('.pri-overlay.image').addClass('preview-mode');
	$('.image.pri-overlay .preview').html(html);
}


function sendRrequest(url_input) {
	$.ajax({
		method: "GET",
	  	url: url_input,
	  	context: document.body
	}).done(function(response) {
	  	previewZapPost(response);
	});
}