var filter = {};
var columns = {};
$(document).ready(function (){
    // Drop filter button
    $("[id^='drop-']").click(function(){
        var inputId = this.id.replace("drop","input");
        var key = this.id.replace("drop-","");
        $("#"+inputId).val("");
        if (key in filter){
            delete filter[key];
        }
        deselectOptions(inputId);
        deactivateBtnClass(this.id);
        sendFilters('drop');
    });
    //Drop selected filters onload
    $("[id^='drop-']").each(function(i,el){
        var inputId = el.id.replace("drop","input");
        deselectOptions(inputId);
    }) 
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
        sendFilters('select');
    });
    $("#input-title").change(function(){
        var id = this.id.replace("input","drop");
        activateBtnClass(id);
        filter["title"] = this.value;
        sendFilters('title');
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
        else if (this.name == "sw-intersect"){
            key = "ath_intersection";
            filter[key] = this.checked
        }
        else {
            key = "quartile";
            var qs = $("[name='quartile']:checked").map(function(){
                return parseInt(this.value.slice(1));
            })
            .toArray()
            filter[key] = qs;
        }
        if (key in filter && filter[key].length==0){
            delete filter[key];
        }
        sendFilters('inputs');
    });
    // Navigation <a> - ajax
    bindNavBtns();
    // Sorting
    $("[id^='sort-a']").on('click', sortA);
    $("[id^='sort-d']").on('click', sortD);
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
        $.ajax({
            url: "/output",
            async: false,
            type: "POST",
            data: JSON.stringify({'type':'csv','filters':filter}),
            contentType: "application/json",
            success: saveData
        });
    });
    $("[id^='colsel-']").change(columnVisChanged);
    // Editable Cell
    $(".editable-cell").on('dblclick',startEditing);
    // Modal Btns
    // column selector events
    $("#column-selector-update").click(function (){
        $("#column-selector-modal").modal('hide');
        for (key in columns) {
            pub_columns[key] = columns[key];
        }
        filter['pub_columns'] = pub_columns;
        navigate();
    });
    $("#add-new-column").click(function(){
        var field = $("#new-column-input").val();
        $.ajax({
            url: "/addcolumn",
            type: "POST",
            data: field,
            success: function(result){
                if ($('#new-column-input').hasClass("is-invalid")){
                    $('#new-column-input').removeClass("is-invalid");
                }
                $('#column-selector-list').append(result);
                columns[field] = true;
                $("#colsel-"+field).change(columnVisChanged);
            },
            error: function(result){
                $('#new-column-input').addClass("is-invalid");
            },
        });
    });
    $("#delete-columns-btn").click(function(){
        var ids = $(".table-success").map(function(){
                return $(this).children().first().text();
            })
            .get();
        $.ajax({
            url: "/deletepubs",
            type: "POST",
            data: JSON.stringify(ids),
            contentType: "application/json",
        });
        $(".table-success").toggle();
        $("#delete-columns-modal").modal('hide');
    });
    // Row Selection
    $("tbody tr").on('click', selectRow);
    // GOTO Up
    $('#gotoup').click(function(){
        $("html, body").animate({ scrollTop: 0 }, "slow");
        return false;
    });
    $(window).on('scroll', function(){
        if ($(document).scrollTop()>60 && $(window).scrollTop() <= ($(document).height() - $(window).height() - 30)){
            $("#gotoup").show();
        }
        else {
            $("#gotoup").hide();
        }
    });
    // Items PerPage
    $(document).on('change',"[id^='perpage-']", function(){
        var pp = $(this).attr('id').split('-')[1];
        filter['per_page'] = pp
        sendFilters();
    });
});
function saveData(data) {
    var a = document.createElement("a");
    document.body.appendChild(a);
    a.style = "display: none";
    var blob = new Blob([data[0]], {type: "text/plain"}),
        url = window.URL.createObjectURL(blob);
    a.href = url;
    a.download = data[1];
    a.click();
    window.URL.revokeObjectURL(url);
}
function deselectOptions(inputId){
        if ($("#"+inputId).length > 0){
            $("#"+inputId)[0].selectedIndex = 0;
        }
}
function activateBtnClass(id){
        $("#"+id).removeClass("btn-outline-light");
        $("#"+id).addClass("btn-outline-secondary");
}
function deactivateBtnClass(id) {
        $("#"+id).removeClass("btn-outline-secondary");
        $("#"+id).addClass("btn-outline-light");
}
function sendFilters(sender){
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
            $(".editable-cell").on('dblclick',startEditing);
            $("[id^='sort-a']").on('click', sortA);
            $("[id^='sort-d']").on('click', sortD);
            $("tbody tr").on('click', selectRow);
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
function sortA() {
    event.preventDefault();
    $(this).blur();
    sortT2($(this).closest('th').get(0),true);
}
function sortD() {
    event.preventDefault();
    $(this).blur();
    sortT2($(this).closest('th').get(0),false);
}
function sortT2(th, n){
        const table = th.closest('table');
        Array.from(table.children[1].querySelectorAll('tr:nth-child(n+1)'))
        .sort(comparer(Array.from(th.parentNode.children).indexOf(th), n))
        .forEach(tr => table.children[1].appendChild(tr) );
}
function startEditing() {
    event.stopPropagation();
    var currentEle = $(this);
    var value = $(this).html();
    if ($(this).has("input").length > 0){return}
    updateVal(currentEle, value);
}
function updateVal(currentEle, value) {
    var field = $(currentEle).attr("id").split(':')[0];
    var id = $(currentEle).attr("id").split(':')[1];
    var data = { 'id': id };
    if ($(currentEle).attr('id').split(":")[0]=="pub_type"){
        $(currentEle).html('<a class="test-cls" href="#">value</a>');
        $(currentEle).html(html_pub_dd.replace('curr-pub',value));
        $("#pub_type_dd_btn").focus();
        var new_pub_type = '----------';
        $('.context-pub-type-selector').on('click', function(){
            event.stopPropagation();
            new_pub_type = $(this).text();
            $(currentEle).html(new_pub_type);   
            data[field] = new_pub_type;
            updatePublication(data);
        });
        $("#pub_type_dd").on('hidden.bs.dropdown', function(){
            $(currentEle).html(value);   
        });
    }
    else {
        $(currentEle).html('<input class="thVal form-control" size="1" type="text" value="' + value + '" />');
    }
    $(".thVal").select();
    $(".thVal").keyup(function (event) {
        if (event.keyCode == 13) {
            $(currentEle).html($(".thVal").val().trim());
            data[field] = $(currentEle).text();
            if ('main_id' in data && data['main_id'] != ''){
                $(currentEle).parent().addClass("table-info");
            }
            else{
                $(currentEle).parent().removeClass("table-info");
            }
            updatePublication(data);
        }
    });
    $(".thVal").focusout(function(event){
        $(currentEle).html(value);
    });
}
function updatePublication(data){
    $.ajax({
        url: "/update",
        type: "POST",
        data: JSON.stringify(data),
        contentType: "application/json",
    });
}
function columnVisChanged(){
    var key = $(this).attr("value");
    var value = $(this).is(":checked");
    columns[key] = value;
}
function selectRow(){
    if ($(this).hasClass("table-success")){
        $(this).removeClass("table-success");
    }
    else{
        $(this).addClass("table-success");
    }
    $('#delete-cols-toolbar-btn').toggle($(".table-success").length>0);
}

