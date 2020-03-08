$(document).ready(function() {
    function checkPreferences(data) {
        form = $('form#preferences');
        inputs = form.find('input');
        inputs.each(function() {
            data[$(this).attr('name')] = $(this).val();
        });
        return data;
    }
    $('body').on('click', 'form a.btn.post_data', function() {
        data = {};
        form = $(this).closest('form');
        inputs = form.find('input');
        valuemissing = false;
        inputs.each(function() {
            if ($(this).val() == '') {
                $('#message .success').addClass('is_hidden');
                $('#message .error').removeClass('is_hidden');
                $('#message .error .message1').removeClass('is_hidden');
                valuemissing=true;
            } else {
                data[$(this).attr('name')] = $(this).val();
            }
        });
        if (!valuemissing) {
            $('#message .error').addClass('is_hidden');
            if ($(this).closest('#talk_to_us_form').length > 0) {
                data = checkPreferences(data);
            }
            $.post('/user/subscribe/', data, function(response) {
                if(response.status == 'success'){
                    $('#message .success').removeClass('is_hidden');
                } else {
                    $('#message .success').addClass('is_hidden');
                    $('#message .error').removeClass('is_hidden');
                    $('#message .error .message2').removeClass('is_hidden');
                }
            });
        }
    });
});