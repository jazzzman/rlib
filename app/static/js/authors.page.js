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
            //$.ajax({
                //url: "/index",
                //type: "POST",
                //data: JSON.stringify({"auth":}),
                //contentType: "application/json",
                //success: function(result){
                    //$("#table-container").html(result);
                //}
            //});
        }
    });
		$(".thVal").focusout(function(event){
        $(currentEle).html(value);
    });
}
