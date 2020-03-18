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
            data = {
                'id': $(currentEle).siblings().first().attr("id").slice(2),
                'main_id': $(currentEle).text()
            }
            $.ajax({
                url: "/authors",
                type: "POST",
                data: JSON.stringify(data),
                contentType: "application/json",
                success: function(result){
                    $(currentEle).attr("id", "main_id"+result["main_id"]);
                    $("#main"+result['id']).text(result["main_repr"]);
                }
            });
        }
    });
		$(".thVal").focusout(function(event){
        $(currentEle).html(value);
    });
}
