$(document).ready(function(){
    $('.delete-form').submit(function(){
        var data = $(this).serialize()   // capture all the data in the form in the variable data
        $(this).remove()
        $.ajax({
            method: "POST",   // we are using a post request here, but this could also be done with a get
            url: '/delete/message',
            data: data
        })
        .done(function(res){
            console.log($('#msg-count').text())
            var newCount = parseInt($('#msg-count').text()) - 1
            $('#msg-count').html(newCount)
        })
        return false
    })
})  