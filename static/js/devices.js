function fetch_devices(url, session_key){
    return $.ajax({
        url: url,
        data: {
            session: session_key
        }

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