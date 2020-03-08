var server_host = 'http://localhost:9000';

// var jsdom = require("jsdom");
//
// jsdom.env(
//   "https://iojs.org/dist/",
//   ["http://code.jquery.com/jquery.js"],
//   function (err, window) {
//     console.log("there have been", window.$("a").length - 4, "io.js releases!");
//   }
// );


var process = function(content) {
	content = $('.main-content');
	rows = content.find('.entry-content .sqs-row');
	rows.each(function() {
		$(this).removeClass('sqs-row');
	});

	columns = content.find('.row .col');
	columns.each(function() {
		var get = $.grep(this.className.split(" "), function(v, i){
	       return v.indexOf('sqs-col') === 0;
	    }).join();
		width = get.split("-")[get.split("-").length-1];
		$(this).removeAttr('class');
		$(this).addClass('column');
		width_class='size' + width + 'of12';
		$(this).addClass(width_class);
		$(this).attr('data-width', width);
	});

	blocks = content.find('.column .sqs-block');
	blocks.each(function() {
		var get = $.grep(this.className.split(" "), function(v, i){
	       return v.indexOf('sqs-block-') === 0;
	    }).join();
		type = get.split("-")[get.split("-").length-1];
		$(this).removeAttr('class');
		$(this).addClass('block');
		if (type === 'html') {
			$(this).addClass('text');
			child = $(this).children('.sqs-block-content');
			child.removeAttr('class');
			child.addClass('editable');
		} else if (type === 'image') {
			$(this).addClass('image');
			child = $(this).children('.sqs-block-content');
			child.removeAttr('class');
			child.addClass('content');
			image = $(this).find('img').first();
			new_url = uploadToServer(image);
			var img = $('<img>');
			img.attr('src', new_url);
			child.empty();
			img.appendTo(child);
		}
		$(this).removeAttr('data-block-type');
	});
	body = content.find('.sqs-layout').html();
	changeImageUrls(body);
	cover_pic = $('.block.image').first().find('img').attr('src');
	preview = $('.block.text').first().find('p').first().html();

	var data = {};
	data.body = body;
	data.cover_pic = cover_pic;
	data.preview = preview;

	return data;
	
};

function changeImageUrls(body) {

}

function uploadImageToServer(image) {
	url = image.attr('src');
	return 'https://www.zapyle.com/zapstatic/frontend/landing/images/bg.png';
}

function uploadModifiedBlogs() {
	console.log("Uoloading Modified Logs!");
	// readTextFile("file:///home/sg/Zapcodebase/zapyle_new/data_scrapers/blog_scrapers/scraped_data.json");
	var blogs = [];
	$.getJSON("scraped_data.json", function(json) {
		console.log(json); // this will show the info it in firebug console
		var posts = json.posts;
		for (var post in posts) {
			var blog = {}
			blog.title = post.title;
			blog.status = post.status;
			blog.date = post.date;
			data = process(post.content);
			blog.body = data.body;
			blog.preview = data.preview;
			blog.cover_pic = data.cover_pic;

			$.post(server_host + "/zapblog/crud/", blog, function (data, status) {
				console.log("Data: " + data);
				console.log("Status: " + status);
			});
		}
	});
	
}

uploadModifiedBlogs();