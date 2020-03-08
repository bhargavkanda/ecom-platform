$(document).ready(function() {
	$('body').on('click', '.show', function() {
		type = $(this).attr('id');
		$('.pri-overlay.'+type).addClass('is_visible');
	});
	$('body').on('click', '.close, .glass', function() {
		$(this).closest('.pri-overlay').removeClass('is_visible');
	});
	 $('body').on('click', 'a', function() {
               ga('send', 'event', {
                   eventCategory: 'Link',
                   eventAction: 'Click',
                   eventLabel: $(this).html()
               });
       });
	//$( "#txtphone_number" ).focus();
	$( "#btn" ).click(function() {
	  $.post( "/", {'name':$("#txtNAME").val(),'phone':$("#txtphone").val(),'email':$("#txtEMAIL").val()},function( data ) {
	  		$("#errorname").text('');$("#errorphone").text('');$("#erroremail").text('')
	  		if(data.status == 'success'){
	  			$('.forms').addClass('is_hidden');
	  			 $('.success-msg').addClass('is_visible');
	  			$("#txtNAME").val('')
	  			$("#txtphone").val('')
	  			$("#txtEMAIL").val('')	  			
	  		}else{
		  		var err = data.errors
		  		if ('name' in err){
		  			$("#errorname").text(err.name);
		  		}
		  		if('phone' in err){
		  			$("#errorphone").text(err.phone);
		  		}
		  		if('email' in err){
		  			$("#erroremail").text(err.email);
		  		}
	  		}
		});
	});
	jQuery('a').click(function (event) {
		if(event.target.id == 'btn_send'){
	    	send_sms()
		}
	});
	$('#txtphone_number').keypress(function(e){
		if(e.which == 13){
			send_sms()
			
		}
	})
	function send_sms(){
		$.post( "/", {'phone_number':$("#txtphone_number").val()},function( data ) {
	  		$('.sucess_msg').removeClass('is_visible')
	  		$('.error-msg').removeClass('is_visible')
	  		if(data.status == 'success'){
	  			$('.sucess_msg').addClass('is_visible')
		  		$('.sucess_msg').text(data['data'])
		  		$("#txtphone_number").val('')
	  			fbq('track', "LeadConversion");
	  		}else{
		  		var err = data.errors
		  		$('.error-msg').addClass('is_visible')
		  		$('.error-msg').text(err['error'])
	  		}
		});
	}
});