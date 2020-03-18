$(function () {
    $("#add").click(add);
    $("#parse").click(parse);
});

function add(){
    data = {
        'authors_raw': $('#input-authors-raw').text().trim(),
        'title': $('#input-title').text().trim(),
        'journal': $('#input-journal').text().trim(),
        'volume': $('#input-volume').text().trim(),
        'issue': $('#input-issue').text().trim(),
        'pages': $('#input-pages').text().trim(),
        'year': $('#input-year').text().trim(),
        'doi': $('#input-doi').text().trim(),
        'pub_type': $('#input-pub-type').text().trim(),
    }
    $.ajax({
        url: '/add',
        type: 'POST',
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function(result){
            console.log(result);
        }
    });
}

function parse(){
    raw = $("#input-area").text().trim();

}
