function initiateEditor() {
    var editor = new MediumEditor('.editable', {
        toolbar: {
            buttons: ['bold', 'italic', 'underline', 'quote', 'anchor', 'justifyLeft', 'justifyCenter', 'justifyRight', 'justifyFull', 'orderedlist', 'unorderedlist', 'removeFormat', 'h2', 'h3'],
        },
        buttonLabels: 'fontawesome',
        anchor: {
            targetCheckbox: true
        }
    });
}

function insertImage(block) {
	$(block).find('.content').html($('.pri-overlay.image .preview').html());
	URL = window.URL || window.webkitURL;
	file = document.getElementById('inputImage').files[0];
	blobURL = URL.createObjectURL(file);
	$(block).attr('data-blobURL', blobURL);
	$('.pri-overlay').removeClass('is_visible');
	$('.pri-overlay').removeClass('create');
	$('.pri-overlay').removeClass('edit');
}

function insertZapCTA(block) {
	$(block).find('.content').html($('.pri-overlay.zap_cta .preview').html());
	$('.pri-overlay').removeClass('is_visible');
	$('.pri-overlay').removeClass('create');
	$('.pri-overlay').removeClass('edit');
}

function insertZapPost(block, url) {
	$(block).attr('data-href', url)
	$(block).find('.content').html($('.pri-overlay.zap_embed .preview').html());
	$('.pri-overlay').removeClass('is_visible');
	$('.pri-overlay').removeClass('create');
	$('.pri-overlay').removeClass('edit');
}

function insertSocialPost(block) {
	$(block).find('.content').html($('.pri-overlay.social_embed .preview').html());
	$('.pri-overlay').removeClass('is_visible');
	$('.pri-overlay').removeClass('create');
	$('.pri-overlay').removeClass('edit');
}