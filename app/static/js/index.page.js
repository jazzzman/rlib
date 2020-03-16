var filter = {};
// Setting dataTable
$('#dt-basic-checkbox').dataTable({
    searching: false,
    paging: false,
    columnDefs: [{
        orderable: false,
        className: 'select-checkbox',
        targets: 0
    }],
    select: {
        style: 'os',
        selector: 'td:first-child'
    }
});
$('#dt-basic-checkbox_length').insertBefore('#dt-basic-checkbox_paginate');
$('#dt-basic-checkbox_length').addClass('dataTables_paginate float-left');
$(function (){
    paintCurrentPage();
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
});
function paintCurrentPage(){
    return
    //TODO implement ajax paging & updating paint
    var page = 1;
    if (/page=(\d*)/.test($(location).attr('href'))){
        page = /page=(\d*)/.exec($(location).attr('href'));
    }
    $("li.page-item:contains("+page+")").addClass('active');
}
function activateBtnClass(id){
        $("#"+id).removeClass("btn-outline-light");
        $("#"+id).addClass("btn-outline-secondary");
}
function deactivateBtnClass(id) {
        $("#"+id).removeClass("btn-outline-secondary");
        $("#"+id).addClass("btn-outline-light");
}
function sendFilters(){
        $.ajax({
            url: "/index",
            type: "POST",
            data: JSON.stringify(filter),
            contentType: "application/json",
            success: function(result){
                $(".table-responsive").html(result);
                paintCurrentPage();
            }
        });
}
