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
    $("#journal-filter").on("keyup", function() {
        var value = $(this).val().toLowerCase();
        $("#dt-journals tr").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
    $("[id^='sort-a']").on('click', function(e) {
        e.preventDefault();
        $(this).blur();
        sortT2($(this).closest('th').get(0),true);
    });
    $("[id^='sort-d']").on('click', function(e) {
        e.preventDefault();
        $(this).blur();
        sortT2($(this).closest('th').get(0),false);
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
            }
        }
    });
}
const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;
const comparer = (idx, asc) => (a, b) => ((v1, v2) => 
    v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

function sortT2(th, n){
        const table = th.closest('table');
        Array.from(table.children[1].querySelectorAll('tr:nth-child(n+1)'))
        .sort(comparer(Array.from(th.parentNode.children).indexOf(th), n))
        .forEach(tr => table.children[1].appendChild(tr) );
}
