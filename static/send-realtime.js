$(document).ready(function(){
    $('.send-form').submit(function(){
        var data = $(this).serialize()   // capture all the data in the form in the variable data
        var id = $("#profile-id").attr('value')
        var url_string = '/'+ id + '/messages/send-message'
        $(this).contents('.col-8').children('textarea').val('')
        $.ajax({
            method: "POST",   // we are using a post request here, but this could also be done with a get
            url: url_string,
            data: data
        })
        .done(function(res){
        })
        return false
    })
})  