mp_id='679eb8981e3a5bfa5bb22ca018ad8114';
if(window.location.host=='www.zapyle.com' || window.location.host=='zapyle.com') {
	mp_id='679eb8981e3a5bfa5bb22ca018ad8114';
}
(function(f,b){if(!b.__SV){var a,e,i,g;window.mixpanel=b;b._i=[];b.init=function(a,e,d){function f(b,h){var a=h.split(".");2==a.length&&(b=b[a[0]],h=a[1]);b[h]=function(){b.push([h].concat(Array.prototype.slice.call(arguments,0)))}}var c=b;"undefined"!==typeof d?c=b[d]=[]:d="mixpanel";c.people=c.people||[];c.toString=function(b){var a="mixpanel";"mixpanel"!==d&&(a+="."+d);b||(a+=" (stub)");return a};c.people.toString=function(){return c.toString(1)+".people (stub)"};i="disable track track_pageview track_links track_forms register register_once alias unregister identify name_tag set_config people.set people.set_once people.increment people.append people.track_charge people.clear_charges people.delete_user".split(" ");
for(g=0;g<i.length;g++)f(c,i[g]);b._i.push([a,e,d])};b.__SV=1.2;a=f.createElement("script");a.type="text/javascript";a.async=!0;a.src="//cdn.mxpnl.com/libs/mixpanel-2-latest.min.js";e=f.getElementsByTagName("script")[0];e.parentNode.insertBefore(a,e)}})(document,window.mixpanel||[]);
mixpanel.init(mp_id);
/******************************************* Google Analytics *****************************************/

ga_id='UA-77120861-1';
if(window.location.host=='www.zapyle.com' || window.location.host=='zapyle.com') {
	ga_id='UA-75163998-1';
}

(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

ga('create', ga_id, 'auto');
  

$(document).ready(function() {
	var flag = 0;
	$(document).click(function() {
		flag=0;
	});

	$('body').on('click', '.product-card > div > a', function() {
		ga('send', {
			'hitType' : 'event',
			'eventCategory' : 'Product Click',
			'eventLabel' : document.getElementsByTagName("title")[0].innerHTML,
			'dimension2' : window.location.hash,
			'dimension5' : $(this).closest('.product-card').find('.product-title').find('a').html(),
        	'metric1' : $(this).closest('.product-card').find('.price').find('.new').html(),
		})
	    flag=1;
	});

	$('body').on('click', '#load-more a', function() {
		ga('send', {
			'hitType' : 'event',
			'eventCategory' : 'Load More',
			'eventAction' : pageNum,
			'dimension2' : window.location.hash,
			'eventLabel' : document.getElementsByTagName("title")[0].innerHTML,
		})
	    flag=1;
	});

//********************************************** ANY EVENT *********************************************************//
	
	// User Click event
	$('body').on('click', 'a, button', function() {
		if(flag!=1) {
			ga('send', {
				'hitType' : 'event',
				'eventCategory' : 'User Click',
				'eventAction' : $(this).html(),
				'dimension2' : window.location.hash,
				'eventLabel' : document.getElementsByTagName("title")[0].innerHTML,
			})
		    flag=0;
		}
	});
});