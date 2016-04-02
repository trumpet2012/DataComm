function fetch_devices(url, session_key){
    return $.ajax({
        url: url,
        data: {
            session: session_key
        }
    }).done(function(data, textStatus, jqXHR){
        $("#devices").html(data);
    });
}

function perform_trace(url, formData){
    console.log(url);
    return $.ajax({
        method: 'POST',
        url: url,
        data: formData
    });
}