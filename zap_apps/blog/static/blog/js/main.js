$(document).ready(function() {
	var rightEnd, originalWidthData, newWidth1, newWidth2;
	var flag = false;


	function savePost() {
		cleanPost();
	}
	function publishPost() {
		cleanPost();
	}
	function cleanPost() {
		postText = $('#container').html();
		postText.find('.row-helper, .col-helper, .new-block, .edit-block, .dropper, ui-droppable').remove();
		alert(postText);
	}


	$('body').on('click', '.pri-overlay.image .done', function() {
		insertImage($('#'+$(this).closest('.pri-overlay').attr('data-targetid')));
	});
	$('body').on('click', '.pri-overlay.zap_cta .done', function() {
		insertZapCTA($('#'+$(this).closest('.pri-overlay').attr('data-targetid')));
	});

	$('body').on('click', '.pri-overlay.zap_embed .show-preview', function() {
		sendRrequest($(this).siblings('.url').val());
	});


	$('body').on('click', '.block .edit', function() {
		blockType = $(this).closest('.block').attr('data-type');
		if (blockType == 'image') {
			alert($(this).closest('.block').attr('data-blobURL'));
			blobURL = $(this).closest('.block').attr('data-blobURL');
			// $('#crop-image').attr('src', blobURL);
			$('#crop-image').one('built.cropper', function () {
	        }).cropper('reset').cropper('replace', blobURL);
		}
		$('.pri-overlay.'+blockType).attr('data-targetid', $(this).closest('.block').attr('id'));
		$('.pri-overlay.'+blockType).addClass('is_visible edit');
	});
	
	$('body').on('click', '.pri-overlay.create .cancel', function() {
		block = $('#'+$(this).closest('.pri-overlay').attr('data-targetid'));
		column = block.closest('.column');
		block.remove();
		if (column.find('.block').length == 0) {
			removeColumn(column);
		}
		$(this).closest('.pri-overlay').removeClass('create');
		$(this).closest('.pri-overlay').removeClass('is_visible');
	});
	$('body').on('click', '.pri-overlay.edit .cancel', function() {
		$(this).closest('.pri-overlay').removeClass('edit');
		$(this).closest('.pri-overlay').removeClass('is_visible');
	});
	$('body').click(function() {
		$('.new-block').removeClass('show-options');
	});
	$('body').on('click', '.edit-block .delete', function() {
		column=$(this).closest('.column');
		$(this).closest('.block').remove();
		if (column.find('.block').length==0) {
			removeColumn(column);
		}
	});

	$('body').on('click', '.pri-overlay .close', function(event) {
		$(this).closest('.pri-overlay').removeClass('is_visible');
	});
	$('body').on('click', '.trigger', function(event) {
		$($(this).data('activates')).addClass('is_visible');
	});
	$('body').on('click', '.close_trigger', function(event) {
		$(this).closest('.is_visible').removeClass('is_visible');
	});
	$('body').on('click', '.post-data .save', function(event) {
		savePost();
	});
	$('body').on('click', '.post-data .publish', function(event) {
		publishPost();
	});
	$('select').material_select();
//	$('.modal').modal();
});