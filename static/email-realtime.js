$(document).ready(function(){
    $('#regis-email').keyup(function(){
        var data = $("#regis-form").serialize()   // capture all the data in the form in the variable data
        $.ajax({
            method: "POST",   // we are using a post request here, but this could also be done with a get
            url: "register/email-realtime",
            data: data
        })
        .done(function(res){
            $('#emailMsg').append(res)  // manipulate the dom when the response comes back
        })
    })
})  