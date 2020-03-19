$(function () {
    $(".editable-cell").dblclick(function (e) {
        e.stopPropagation();
        var currentEle = $(this);
        var value = $(this).html();
        if ($(this).has("input").length > 0){return}
        updateVal(currentEle, value);
    });
    $("input[type='checkbox']").change(function (){
        id = $(this).attr("id").trim().split(':')[1];
        field = $(this).attr("id").trim().split(':')[0];
        data = {
            'id': id,
            'field': field,
            'value': $(this).is(":checked")
        };
        send_ajax(data);
    });
});

function updateVal(currentEle, value) {
    $(currentEle).html('<input class="thVal form-control" size="1" type="text" value="' + value + '" />');
    $(".thVal").focus();
    $(".thVal").keyup(function (event) {
        if (event.keyCode == 13) {
            $(currentEle).html($(".thVal").val().trim());
            id = $(currentEle).attr("id").trim().split(':')[1];
            field = $(currentEle).attr("id").trim().split(':')[0];
            data = {
                'id': id,
                'field': field,
                'value': $(currentEle).text().trim()
            };
            send_ajax(data);
        }
    });
		$(".thVal").focusout(function(event){
        $(currentEle).html(value);
    });
}
function send_ajax(data){
    $.ajax({
        url: "/journals",
        type: "POST",
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function(result){
            if (result != "True"){
                $(currentEle).html(value);
                console.log(result);
            }
        }
    });
}
