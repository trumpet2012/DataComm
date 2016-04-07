function submit_form(url, formData){
    console.log(formData);
    return $.ajax({
        method: 'POST',
        url: url,
        data: formData
    });
}