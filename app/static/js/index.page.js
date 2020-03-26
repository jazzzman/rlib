var filter = {};
$(function (){
    $("[id^='drop-']").click(function(){
        var inputId = this.id.replace("drop","input");
        var key = this.id.replace("drop-","");
        //deselect selects
        if ($("#"+inputId).length > 0){
            $("#"+inputId)[0].selectedIndex = 0;
        }
        $("#"+inputId).val("");
        if (key in filter){
            delete filter[key];
        }
        deactivateBtnClass(this.id);
        sendFilters();
    });
    // Filters
    $(".custom-select").change(function(){
        var selectedValues = $("option:selected", this).map(function(){
            return this.value;
        })
        .toArray();
        var id = this.id.replace("input","drop");
        activateBtnClass(id);
        var key = this.id.replace("input-","");
        filter[key] = selectedValues;
        sendFilters();
    });
    $("#input-title").change(function(){
        var id = this.id.replace("input","drop");
        activateBtnClass(id);
        filter["title"] = this.value;
        sendFilters();
    });
    $(".custom-control-input").change(function(){
        var key = ""
        if (this.name == "db-indexing"){
            key = "db";
            var dbs = $("[name='db-indexing']:checked").map(function(){
                return this.value;
            })
            .toArray()
            filter[key] = dbs;
        }
        else {
            key = "quartile";
            var qs = $("[name='quartile']:checked").map(function(){
                return this.value;
            })
            .toArray()
            filter[key] = qs;
        }
        if (key in filter && filter[key].length==0){
            delete filter[key];
        }
        sendFilters();
    });
    // <a> - ajax
    bindNavBtns();
    // Sorting
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
    // exporting
    $("#to-clipboard").click(function (){
        $.ajax({
            url: "/output",
            type: "POST",
            data: JSON.stringify({'type':'clipboard','filters':filter}),
            contentType: "application/json",
        });
    });
    $("#to-csv").click(function (){
        //$("#file").trigger("click");
        $.redirect('/output', 
            {'json':JSON.stringify({'type':'csv','filters':filter})},
            "POST");
        //$.ajax({
            //url: "/output",
            //type: "POST",
            //data: JSON.stringify({'type':'clipboard','filters':filter}),
            //contentType: "application/json",
        //});
    });
    $("#file").change(function() {
        var filename = $(this).val();
        console.log(filename);
    });
});
function activateBtnClass(id){
        $("#"+id).removeClass("btn-outline-light");
        $("#"+id).addClass("btn-outline-secondary");
}
function deactivateBtnClass(id) {
        $("#"+id).removeClass("btn-outline-secondary");
        $("#"+id).addClass("btn-outline-light");
}
function sendFilters(){
    delete filter['page'];
    navigate();
}
function navigate(){
    $.ajax({
        url: "/index",
        type: "POST",
        data: JSON.stringify(filter),
        contentType: "application/json",
        success: function(result){
            $("#table-container").html(result);
            bindNavBtns();
        }
    });
}
function bindNavBtns(){
    $('a.page-link').on('click', function(e) {
        e.preventDefault();
        filter['page'] = $(this).attr('href').split('=')[1]
        navigate();
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
