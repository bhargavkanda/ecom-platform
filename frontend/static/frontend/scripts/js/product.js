$(document).ready(function() {
   
    $('#minus').click(function() {
        if ($('#quantity').html() > 1) {
            $('#quantity').html($('#quantity').html() - 1);
        }
    });
    $('#plus').click(function() {
        if ($('#quantity').html() < $('#quantity').attr('data-max-quantity')) {
            $('#quantity').html(+($('#quantity').html()) + 1);
        }
    });
});
