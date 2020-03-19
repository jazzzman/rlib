$(function () {
    $(".editable-cell").dblclick(function (e) {
        e.stopPropagation();
        var currentEle = $(this);
        var value = $(this).html();
        if ($(this).has("input").length > 0){return}
        updateVal(currentEle, value);
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
            }
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
    });
		$(".thVal").focusout(function(event){
        $(currentEle).html(value);
    });
}
