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
