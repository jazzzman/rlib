var timeoutHandle = new Object();
$(function () {
    $("#add").click(add);
    $("#parse").click(function(){
        //popUpAlert('alert-warning');
    });
    $("#close-alert").click(closeAlert);
    $("#alert-warning").hover(function(){
        clearTimeout(timeoutHandle);
    });
    $("#input-title").focusout(function(){
        var title = $(this).val().trim();
        if (title !== ''){
            var data ={'title':title} 
            $.ajax({
                url: '/checktitle',
                type: 'POST',
                data: JSON.stringify(data),
                contentType: "application/json",
                success: function(result){
                    $("#input-title").removeClass("is-invalid");
                    if (!$("#alert-warning").hasClass('invisible')){
                        closeAlert();
                    }
                },
                error: function(result){
                    errs = JSON.parse(result['responseText']);
                    if ($("#input-title").hasClass('is-invalid')){
                        $("#input-title").removeClass('is-invalid');
                    }
                    $("#input-title").addClass("is-invalid");
                    if (errs['title'] != ''){
                        $("#input-title").next('.invalid-feedback').text(errs['title']);
                    }
                    if ('warnings' in errs){
                        $("#warnings-message").html("There are similar publications in the database:<br/>"+errs['warnings'].join('<br/>'));
                        popUpAlert('alert-warning', 10000);
                    }
                }
            });
        }
        else{
            $("#input-title").removeClass('is-invalid');
        }
    });
});

function add(){
    validateinputs = {
        'authors_raw': $('#input-authors-raw'),
        'title': $('#input-title'),
        'journal': $('#input-journal'),
        'year': $('#input-year'),
        'pub_type': $('#input-pub-type'),
    }
    data = {
        'authors_raw': validateinputs['authors_raw'].val().trim(),
        'title': validateinputs['title'].val().trim(),
        'journal': validateinputs['journal'].val().trim(),
        'volume': parseInt($('#input-volume').val().trim()),
        'issue': $('#input-issue').val().trim(),
        'pages': $('#input-pages').val().trim(),
        'year': parseInt(validateinputs['year'].val().trim()),
        'doi': $('#input-doi').val().trim(),
        'pub_type': parseInt(validateinputs['pub_type'].val()),
    }
    if (!$("#alert-warning").hasClass('invisible')){
        closeAlert();
    }
    Object.values(validateinputs).forEach(function(val){
        if (val.hasClass('is-invalid')){
            val.removeClass('is-invalid');
        }
    });
    $.ajax({
        url: '/add',
        type: 'POST',
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function(result){
            if (result === '200'){
                $("#warning-message").html("Publication added!");
                popUpAlert('alert-success');
            }
            else if ('reject' in result){
                $("#warnings-message").html("Publication rejected!<br/>"+result['reject']);
                popUpAlert('alert-danger', 10000);
            }
            else if ('warnings' in result){
                $("#warnings-message").html("Publication added! But there were warnings.<br/>"+result['warnings'].join('<br/>'));
                popUpAlert('alert-warning', 10000);
            }
        },
        error: function(result){
            errs = JSON.parse(result['responseText']);
            Object.keys(errs).forEach(function(key){
                validateinputs[key].addClass("is-invalid");
                if (errs[key] != ''){
                    validateinputs[key].next('.invalid-feedback').text(errs[key]);
                }
            });
        },
    });
}

function parse(){
    raw = $("#input-area").text().trim();

}
function popUpAlert(type, delay=2000){
    toggleAlert(type);
    timeoutHandle = setTimeout(function(){
                    toggleAlert(type)
                },
                delay);
}
function toggleAlert(type=''){
    if (type != '') {
        $("#alert-warning").attr('class',
            $("#alert-warning").attr('class').replace(/\balert-\w+\b/,type)
        );
    }
    $("#alert-warning").toggleClass('invisible');
}
function closeAlert(){
    clearTimeout(timeoutHandle);
    toggleAlert();
}

