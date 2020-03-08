$(document).ready(function() {
	
	function getParameterByName(name, url) {
	    if (!url) url = window.location.href;
	    name = name.replace(/[\[\]]/g, "\\$&");
	    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
	        results = regex.exec(url);
	    if (!results) return null;
	    if (!results[2]) return '';
	    return decodeURIComponent(results[2].replace(/\+/g, " "));
	}
	
	$(window).bind("beforeunload", function() { 
		$.post( "/analytics/end_analytics_session/", 
	  		{
	  			'session_id':getCookie("camp_session"),
	  			'end_page' : new Date(),
	  		},function( data ) {});
    });

	function trackEvents(event, event_details){
		$.post( "/analytics/track_analytics_events/", 
	  		{
	  			"events":JSON.stringify({
	  				"data":[{
		  				'session_id' : getCookie("camp_session"),
		  				'name' : event,
		  				'event_details': event_details
		  			}]
		  		})
	  		},function( data ) {}
	  	);
	}

	$( "#btn" ).click(function() {
		if(!$("#email").val()){
			alert('Enter email address.')
			return false;
		}
		if(!validateEmail($("#email").val())){
			alert("Enter valid email address.")
			return false;
		}
	  	$.post( "/marketing/follow_campaign/", 
	  		{
	  			'email':$("#email").val(),
	  			'campaign_id':window.location.pathname.split('/')[2],
	  			'unique_code':getParameterByName('ref')
	  		},function( data ) {
  			var myURL = document.location;
	  		if(data.status == 'success'){
	  			event_details = {"email_id": $("#email").val(), "source": getParameterByName('ref'), "campaign_id": window.location.pathname.split('/')[2]}
	  			trackEvents("pre_launch_cta", event_details)
	  			window.location = window.location.pathname+'thankyou?url='+data.data.url;			
	  		}else{
	  			window.location = window.location.pathname+'thankyou?email='+$("#email").val();
	  		}
		});
	});

	function getCookie(cname) {
	    var name = cname + "=";
	    var ca = document.cookie.split(';');
	    for(var i = 0; i <ca.length; i++) {
	        var c = ca[i];
	        while (c.charAt(0)==' ') {
	            c = c.substring(1);
	        }
	        if (c.indexOf(name) == 0) {
	            return c.substring(name.length,c.length);
	        }
	    }
	    return "";
	}

	function setCookie(cname, cvalue, exdays) {
	    var d = new Date();
	    d.setTime(d.getTime() + (exdays*24*60*60*1000));
	    var expires = "expires="+ d.toUTCString();
	    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
	}

	function checkSession() {
	    var camp_session=getCookie("camp_session");
	    if (camp_session=="") {
	        $.post( "/analytics/initiate_analytics_session/", 
		  		{
		  			'platform':'WEBSITE',
		  			'start_page' : new Date(),
		  			'campaign':window.location.pathname.split('/')[2],
		  			'device_id':navigator.appVersion,
		  			'source':'website'
		  		},function( data ) {
		  		if(data.status == 'success'){	
		  			setCookie("camp_session", data.data[0].session_id, 365);
		  			event_details = {"source": getParameterByName('ref'), "campaign_id": window.location.pathname.split('/')[2]}
					trackEvents("pre_launch_page_visits", event_details)
		  		}
			});
	    }
	}

	function validateEmail(sEmail) {
	    var filter = /^([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;
	    if (filter.test(sEmail)) {
	        return true;
	    }
	    else {
	        return false;
	    }
	}

	$( ".share_link" ).click(function() {
		event_details = {"source": getParameterByName('ref'), "campaign_id": window.location.pathname.split('/')[2], 'medium':$(this).data("name")}
		trackEvents("campaign_social_share_cta", event_details)
	});

	checkSession()
})