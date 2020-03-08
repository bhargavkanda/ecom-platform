$(document).ready(function() {
	var rightEnd, originalWidthData, newWidth1, newWidth2;
	var flag = false;
	$( ".dropper div" ).droppable({
		over: function(e, ui) {  },
		drop: function(e, ui) { moveBlock(e, ui, $(this).closest('.block'), $(this).attr('data-location')); },
		tolerance: "pointer",
		hoverClass: "drop-hover"
	});
	$( ".dropper .left, .dropper .right" ).droppable( "option", "greedy", true );
	$( ".column .add-left, .column .add-right" ).droppable({
		over: function(e, ui) { showPreview(e, ui, this); },
		drop: function(e, ui) { moveBlocktoNewColumn(e, ui, $(this).closest('.column'), $(this).attr('data-location')); },
		tolerance: "pointer",
		greedy: true,
		hoverClass: "drop-hover"
	});
	$( ".row-helper .add-bottom" ).droppable({
		over: function(e, ui) { showPreview(e, ui, this); },
		drop: function(e, ui) { moveBlocktoNewRow(e, ui, $(this).closest('.row'), $(this).attr('data-location')); },
		tolerance: "pointer",
		hoverClass: "drop-hover"
	});
	$(".column").resizable({
		handles: "e",
    	containment: "parent",
    	start: function(e, ui) { rightEnd = ui.originalPosition.left + ui.originalSize.width; grid_x = ui.originalSize.width/parseInt(ui.helper.attr('data-width'), 10);},
    	resize: function(e, ui) { ui.helper.removeAttr('style'); resizeColumn(e, ui); },
    	stop: function(e, ui) { ui.helper.attr('data-width', newWidth1);ui.helper.next().attr('data-width', newWidth2); },
	});
	$('.block').draggable({
		  	handle: ".move",
		  	revert: "invalid",
		  	addClasses: false,
		  	cursor: "crosshair",
		  	opacity: 0.3,
		  	start: function(e, ui) { flag=true; },
		  	stop: function(e, ui) { ui.helper.removeAttr('style'); },
		});
	$('body').on('click', '.new-block', function(event) {
		$(this).toggleClass('show-options');
		event.stopPropagation();
	});
	var json = '{"text":"<div class=\'block text\' data-type=\'text\'><div class=\'dropper\'><div class=\'above\' data-location=\'above\'><div class=\'left\' data-location=\'left\'></div><div class=\'right\' data-location=\'right\'></div></div><div class=\'below\' data-location=\'below\'><div class=\'left\' data-location=\'left\'></div><div class=\'right\' data-location=\'right\'></div></div></div><div class=\'editable\'><p>Type here..</p></div><div class=\'new-block\'><ul><li class=\'text\'>Text</li><li class=\'image\'>Image</li><li class=\'social_embed\'>Social Embed</li><li class=\'zap_embed\'>Zapyle Product Embed</li><li class=\'zap_cta\'>Button</li></ul></div><div class=\'edit-block\'><ul><li class=\'move\'>Move</li><li class=\'delete\'>Delete</li></ul></div></div>",' +
	'"image":"<div class=\'block image\' data-type=\'image\'><div class=\'dropper\'><div class=\'above\' data-location=\'above\'><div class=\'left\' data-location=\'left\'></div><div class=\'right\' data-location=\'right\'></div></div><div class=\'below\' data-location=\'below\'><div class=\'left\' data-location=\'left\'></div><div class=\'right\' data-location=\'right\'></div></div></div><div class=\'content\'><img src=\'\'></div><div class=\'new-block\'><ul><li class=\'text\'>Text</li><li class=\'image\'>Image</li><li class=\'social_embed\'>Social Embed</li><li class=\'zap_embed\'>Zapyle Product Embed</li><li class=\'zap_cta\'>Button</li></ul></div><div class=\'edit-block\'><ul><li class=\'edit\'>Edit</li><li class=\'delete\'>Delete</li></ul></div></div>",' +
	'"social_embed":"<div class=\'block social_embed\' data-type=\'social_embed\'><div class=\'dropper\'><div class=\'above\' data-location=\'above\'><div class=\'left\' data-location=\'left\'></div><div class=\'right\' data-location=\'right\'></div></div><div class=\'below\' data-location=\'below\'><div class=\'left\' data-location=\'left\'></div><div class=\'right\' data-location=\'right\'></div></div></div><div class=\'content\'><embed></embed></div><div class=\'new-block\'><ul><li class=\'text\'>Text</li><li class=\'image\'>Image</li><li class=\'social_embed\'>Social Embed</li><li class=\'zap_embed\'>Zapyle Product Embed</li><li class=\'zap_cta\'>Button</li></ul></div><div class=\'edit-block\'><ul><li class=\'edit\'>Edit</li><li class=\'delete\'>Delete</li></ul></div></div>",' +
	'"zap_embed":"<div class=\'block zap_embed\' data-type=\'zap_embed\'><div class=\'dropper\'><div class=\'above\' data-location=\'above\'><div class=\'left\' data-location=\'left\'></div><div class=\'right\' data-location=\'right\'></div></div><div class=\'below\' data-location=\'below\'><div class=\'left\' data-location=\'left\'></div><div class=\'right\' data-location=\'right\'></div></div></div><div class=\'content\'><iframe></iframe></div><div class=\'new-block\'><ul><li class=\'text\'>Text</li><li class=\'image\'>Image</li><li class=\'social_embed\'>Social Embed</li><li class=\'zap_embed\'>Zapyle Product Embed</li><li class=\'zap_cta\'>Button</li></ul></div><div class=\'edit-block\'><ul><li class=\'edit\'>Edit</li><li class=\'delete\'>Delete</li></ul></div></div>",' +
	'"zap_cta":"<div class=\'block zap_cta\' data-type=\'zap_cta\'><div class=\'dropper\'><div class=\'above\' data-location=\'above\'><div class=\'left\' data-location=\'left\'></div><div class=\'right\' data-location=\'right\'></div></div><div class=\'below\' data-location=\'below\'><div class=\'left\' data-location=\'left\'></div><div class=\'right\' data-location=\'right\'></div></div></div><div class=\'content\'><a href=\'\'><button val=\'\'></a></div><div class=\'new-block\'><ul><li class=\'text\'>Text</li><li class=\'image\'>Image</li><li class=\'social_embed\'>Social Embed</li><li class=\'zap_embed\'>Zapyle Product Embed</li><li class=\'zap_cta\'>Button</li></ul></div><div class=\'edit-block\'><ul><li class=\'edit\'>Edit</li><li class=\'delete\'>Delete</li></ul></div></div>"' +
	'}';
	var obj = JSON.parse(json);
	rowWrap = "<div class='row'></div>";
	rowAdd = "<div class='row-helper'><div class='new-block'><ul><li id='text' class='text'>Text</li><li id='image' class='image'>Image</li><li id='social_embed' class='social_embed'>Social Embed</li><li id='zap_embed' class='zap_embed'>Zapyle Product Embed</li><li id='zap_cta' class='zap_cta'>Button</li></ul></div><div class='add-bottom' data-location='after'></div></div>";
	colAdd = "<div class='col-helper'><div class='new-block'><ul><li id='text' class='text'>Text</li><li id='image' class='image'>Image</li><li id='social_embed' class='social_embed'>Social Embed</li><li id='zap_embed' class='zap_embed'>Zapyle Product Embed</li><li id='zap_cta' class='zap_cta'>Button</li></ul></div></div><div class='add-left' data-location='before'></div><div class='add-right' data-location='after'><div class='resizer'><div class='resize-line'></div></div></div>";
	halfcolWrap = '<div class="column size6of12" data-width="6"></div>';
	fullcolWrap = '<div class="column size12of12" data-width="12"></div>';
	function showPreview(event, ui, column) {
		// $(column).css({'background':'#000'});
	}
	function moveBlocktoNewColumn(e, ui, column, location) {
		if (flag) {
			flag=false;
			ui.draggable.removeAttr('style');
			currentColumn = ui.draggable.closest('.column');
			addColumn(e, ui, column, location);
			if ($(currentColumn).find('.block').length==0) {
				removeColumn(currentColumn);
			};
		};
	}
	function moveBlocktoNewRow(e, ui, row, location) {
		if (flag) {
			flag=false;
			ui.draggable.removeAttr('style');
			currentColumn = ui.draggable.closest('.column');
			addBlocktoNewRow(e, ui, row, location);
			if ($(currentColumn).find('.block').length==0) {
				removeColumn(currentColumn);
			};
		};
	}
	function moveBlock(e, ui, block, location) {
		if (flag) {
			flag=false;
			ui.draggable.removeAttr('style');
			currentColumn = ui.draggable.closest('.column');
			if (location == 'above' || location == 'below') {
				addBlock(e, ui, block, location);
			} else {
				addBlocktoRow(e, ui, block, location);
			}
			if ($(currentColumn).find('.block').length==0) {
				removeColumn(currentColumn);
			};
		}
	}
	function addBlock(e, ui, block, location) {
		if (location == 'above') {
			ui.draggable.detach().insertBefore(block);
		} else {
			ui.draggable.detach().insertAfter(block);
		}
	}
	function addBlocktoNewRow(e, ui, row, location) {
		copy = ui.draggable.clone();
		ui.draggable.remove();
		if (location == 'after') {
			$(copy).insertAfter($(row));
		} else {
			$(copy).insertBefore($(row));
		}
		copy.wrap(rowWrap).before(rowAdd).wrap(fullcolWrap).after(colAdd);
		setUpNewColumn(copy);
		setUpNewRow(copy);
	}
	function addBlocktoRow(e, ui, block, location) {
		copy = ui.draggable.clone();
		ui.draggable.remove();
		$(block).wrap(rowWrap).before(rowAdd).wrap(halfcolWrap).after(colAdd);
		if (location == 'left') {
			$(copy).insertBefore($(block).closest('.column'));
		} else {
			$(copy).insertAfter($(block).closest('.column'));
		}
		copy.wrap(halfcolWrap).after(colAdd);
		setUpNewBlock(copy);
		setUpNewColumn(copy);
		setUpNewColumn(block);
		setUpNewRow(copy);
	}

	function addColumn(event, ui, column, location) {
		row = $(column).closest('.row');
		cols = $(row).children('.column');
		usedWidth = 0;
		cols.each(function( index ) {
			width = parseInt($(this).attr('data-width'), 10);
			$(this).removeClass('size'+width+'of12');
			newWidth = (12 - (12/(cols.length+1)))*width/12;
			$(this).addClass('size'+newWidth.toFixed()+'of12');
			$(this).attr('data-width', newWidth.toFixed());
			usedWidth = usedWidth + parseInt(newWidth.toFixed());
		});
		newColClass = 'size'+(12 - usedWidth)+'of12';
		colWrap = "<div class='column "+newColClass+"' data-width='"+(12 - usedWidth)+"'></div>"
		copy = ui.draggable.clone();
		ui.draggable.remove();
		if (location == 'before') {
			copy.insertBefore(column);
		} else {
			copy.insertAfter(column);
		}

		copy.wrap(colWrap);
		copy.after(colAdd);
		setUpNewColumn(copy);
		setUpNewBlock(copy);
	}
	function removeColumn(column) {
		currentRow = column.closest('.row');
		parentColumn = currentRow.closest('.column');
		$(column).remove();
		if (parentColumn.length>0 && parentColumn.find('.block').length == 0) {
			removeColumn(parentColumn);
		} else {
			cols = currentRow.children('.column');
			existingColsWidth = 0;
			cols.each(function( index ) {
				existingColsWidth = existingColsWidth + parseInt($(this).attr('data-width'), 10);
			});
			usedWidth = 0;
			cols.each(function(index) {
				width = parseInt($(this).attr('data-width'), 10);
				$(this).removeClass('size'+width+'of12');
				newWidth = 12*width/existingColsWidth;
				if (index == cols.length-1) {
					newWidth = 12 - usedWidth;
				};
				$(this).addClass('size'+newWidth.toFixed()+'of12');
				$(this).attr('data-width', newWidth.toFixed());
				usedWidth = usedWidth + parseInt(newWidth.toFixed());
			});
		}
		if (currentRow.find('.block').length==0) {
			currentRow.remove();
		};
	}
	function resizeColumn(e, ui) {
		difference = (rightEnd - (ui.position.left + ui.size.width))/grid_x;
		newWidth1 = parseInt(ui.helper.attr('data-width'), 10) -  parseInt(difference.toFixed());
		newWidth2 = parseInt(ui.helper.next().attr('data-width'), 10) + parseInt(difference.toFixed());
		if (newWidth1>0 && newWidth1 < 13 && newWidth2>0 && newWidth2 < 13) {
			ui.helper.removeClass (function (index, css) {return (css.match (/(^|\s)size\S+/g) || []).join(' ');});
			ui.helper.addClass('size'+newWidth1+'of12');
			ui.helper.next().removeClass (function (index, css) {return (css.match (/(^|\s)size\S+/g) || []).join(' ');});
			ui.helper.next().addClass('size'+newWidth2+'of12');
		}
	}

	function createNewBlock(trigger) {
		if ($(trigger).closest('.col-helper').length > 0) {
			column = $(trigger).closest('.column');
			colHelper = $(column).children('.col-helper').after((obj[$(trigger).attr('class')]));
			newBlock = $(colHelper).next();
		} else if ($(trigger).closest('.row-helper').length > 0) {
			row = $(trigger).closest('.row').after((obj[$(trigger).attr('class')]));
			newBlock = row.next();
			newBlock.wrap(rowWrap).before(rowAdd).wrap(fullcolWrap).after(colAdd);
			setUpNewColumn(newBlock);
			setUpNewRow(newBlock);
		} else {
			block = $(trigger).closest('.block').after((obj[$(trigger).attr('class')]));
			newBlock = block.next();
		}
		newBlock.attr('id', $.now());
		if (!newBlock.hasClass('text')) {
			blockType = newBlock.attr('data-type');
			$('.pri-overlay.'+blockType).attr('data-targetid', newBlock.attr('id'));
			$('.pri-overlay.'+blockType).addClass('is_visible create');
		}
		return newBlock;
	}
	function setUpNewRow(newBlock) {
		newBlock.closest( ".row" ).find('.add-bottom').droppable({
			over: function(e, ui) { showPreview(e, ui, this); },
			drop: function(e, ui) { moveBlocktoNewRow(e, ui, $(this).closest('.row'), $(this).attr('data-location')); },
			tolerance: "pointer",
			hoverClass: "drop-hover"
		});
	}
	function setUpNewColumn(newBlock) {
		newBlock.closest( ".column" ).find('.add-left, .add-right').droppable({
			over: function(e, ui) { showPreview(e, ui, this); },
			drop: function(e, ui) { moveBlocktoNewColumn(e, ui, $(this).closest('.column'), $(this).attr('data-location')); },
			tolerance: "pointer",
			hoverClass: "drop-hover"
		});
		newBlock.closest( ".column" ).resizable({
			handles: "e",
	    	containment: "parent",
	    	start: function(e, ui) { rightEnd = ui.originalPosition.left + ui.originalSize.width; grid_x = ui.originalSize.width/parseInt(ui.helper.attr('data-width'), 10);},
	    	resize: function(e, ui) { ui.helper.removeAttr('style'); resizeColumn(e, ui); },
	    	stop: function(e, ui) { ui.helper.attr('data-width', newWidth1);ui.helper.next().attr('data-width', newWidth2); },
		});
	}
	function setUpNewBlock(newBlock) {
		newBlock.draggable({
		  	revert: "invalid",
		  	addClasses: false,
		  	cursor: "crosshair",
		  	opacity: 0.3,
		  	start: function(e, ui) { flag=true; },
		  	stop: function(e, ui) { ui.helper.removeAttr('style'); },
		});
		if (newBlock.hasClass('text')) {
			newBlock.draggable( "option", "handle", ".move" );
			initiateEditor();
		}
		newBlock.find('.dropper div').droppable({
			over: function(e, ui) {  },
			drop: function(e, ui) { moveBlock(e, ui, $(this).closest('.block'), $(this).attr('data-location')); },
			tolerance: "pointer",
			hoverClass: "drop-hover"
		});
		newBlock.find( ".dropper .left, .dropper .right" ).droppable( "option", "greedy", true );
	}

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

	$('body').on('click', '.new-block li', function() {
		newBlock = createNewBlock(this);
		setUpNewBlock(newBlock);
	});

	$('body').on('click', '.pri-overlay.zap_embed .done', function() {
		insertZapPost($('#'+$(this).closest('.pri-overlay').attr('data-targetid')), $(this).closest('.pri-overlay').find('input.url').val());
	});
	$('body').on('click', '.pri-overlay.social_embed .done', function() {
		insertSocialPost($('#'+$(this).closest('.pri-overlay').attr('data-targetid')));
	});
	$('body').on('click', '.pri-overlay.image .done', function() {
		insertImage($('#'+$(this).closest('.pri-overlay').attr('data-targetid')));
	});
	$('body').on('click', '.pri-overlay.zap_cta .done', function() {
		insertZapCTA($('#'+$(this).closest('.pri-overlay').attr('data-targetid')));
	});

	$('body').on('click', '.pri-overlay.zap_embed .show-preview', function() {
		sendRrequest($(this).siblings('.url').val());
	});
	$('body').on('click', '.pri-overlay.social_embed .show-preview', function() {
		previewSocialPost($(this).siblings('.embed-code').val());
	});
	// $('body').on('click', '.pri-overlay.image .show-preview', function() {
	// 	previewImage();
	// });
	$('body').on('click', '.pri-overlay.zap_cta .show-preview', function() {
		previewZapCTA(this);
	});

	$('body').on('click', '.block .edit', function() {
		blockType = $(this).closest('.block').attr('data-type');
		if (blockType == 'image') {
			alert($(this).closest('.block').attr('data-blobURL'));
			blobURL = $(this).closest('.block').attr('data-blobURL');
			// $('#crop-image').attr('src', blobURL);
			$('#crop-image').one('built.cropper', function () {
	            // Revoke when load complete
	            // URL.revokeObjectURL(blobURL);
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
	$('body').on('click', '.next', function(event) {
		$('.post-data').addClass('slide_in');
	});
	$('body').on('click', '.post-data .back', function(event) {
		$('.post-data').removeClass('slide_in');
	});

	$('body').on('click', '.post-data .save', function(event) {
		savePost();
	});
	$('body').on('click', '.post-data .publish', function(event) {
		publishPost();
	});
});