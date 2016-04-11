function submit_form(url, formData){
    return $.ajax({
        method: 'POST',
        url: url,
        data: formData
    });
}