$(document).ready(function(){
    $(".editable-cell").dblclick(function (e) {
        e.stopPropagation();
        var currentEle = $(this);
        var value = $(this).html();
        if ($(this).has("input").length > 0){return}
        updateVal(currentEle, value);
    });
    $("#author-filter").on("keyup", function() {
        var value = $(this).val().toLowerCase();
        $("#dt-authors tr").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });{
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
}
});

function updateVal(currentEle, value) {
    $(currentEle).html('<input class="thVal form-control" size="1" type="text" value="' + value + '" />');
    $(".thVal").focus();
    $(".thVal").keyup(function (event) {
        if (event.keyCode == 13) {
            $(currentEle).html($(".thVal").val().trim());
            data = {
                'id': $(currentEle).siblings().first().attr("id").split(':')[1],
                'main_id': $(currentEle).text()
            }
            if (data['main_id'] != ''){
                $(currentEle).parent().addClass("table-info");
            }
            else{
                $(currentEle).parent().removeClass("table-info");
            }

            $.ajax({
                url: "/authors",
                type: "POST",
                data: JSON.stringify(data),
                contentType: "application/json",
                success: function(result){
                    $(currentEle).attr("id", "main_id:"+result["main_id"]);
                    $("#main:"+result['id']).text(result["main_repr"]);
                }
            });
        }
    });
		$(".thVal").focusout(function(event){
        $(currentEle).html(value);
    });
}
const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;
const comparer = (idx, asc) => (a, b) => ((v1, v2) => 
    v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

function sortT2(th, n){
        const table = th.closest('table');
        Array.from(table.children[1].querySelectorAll('tr:nth-child(n+2)'))
        .sort(comparer(Array.from(th.parentNode.children).indexOf(th), n))
        .forEach(tr => table.children[1].appendChild(tr) );
}
//document.querySelectorAll('th').forEach(
    //th => th.addEventListener('click', (() => {
        //console.log(th);
        //const table = th.closest('table');
        //Array.from(table.querySelectorAll('tr:nth-child(n+2)'))
        //.sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
        //.forEach(tr => table.appendChild(tr) );
    //}))
//)
