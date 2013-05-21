function show_result(search_engine, keyword, domain) {
    $("#" + search_engine).html('<h3>' + search_engine + ' <span class="pending label label-info">pending<span></h3><hr>');
    $("#" + search_engine).append('<div class="result"></div>');
    var url = '/search/' + search_engine + ':' + keyword + ':' + domain;
    $.ajax({
        url: url, 
        type: 'PUT',
        success: function(data) {
            var task_status = data['status'];
            if (task_status == null) {
                create_task(search_engine, keyword, domain);
            }
            else {
                get_task(search_engine, keyword, domain);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            resp = $.parseJSON(jqXHR.responseText);
            $("#" + search_engine + ' .result').html('<span class="alert alert-error">' + resp['message'] + '</span>');
        },
        cache: false
    });
}

function create_task(search_engine, keyword, domain) {
    var url = '/search/' + search_engine + ':' + keyword + ':' + domain;
    $.ajax({
        url: url, 
        type: 'POST',
        success: function(data) {
            get_task(search_engine, keyword, domain);
        },
        cache: false
    });
}

function get_task(search_engine, keyword, domain) {
    var url = '/search/' + search_engine + ':' + keyword + ':' + domain;
    $.ajax({
        url: url, 
        type: 'PUT',
        success: function(data) {
            var task_status = data['status'];
            $.ajax({
                url: url, 
                type: 'GET',
                success: function(data) {
                    var links = data['links'];
                    var html = '<table class="table table-bordered table-striped">';
                    html = html + '<tr><th>Rank</th><th>Url</th></tr>'; 
                    $.each(links, function(index, value){
                        html = html + '<tr><td>' + value['rank'] + '</td><td>' + value['url'] + '</td></tr>';
                    });
                    html = html + '</table>';
                    $("#" + search_engine + ' .result').html(html);
                },
            });
            if(task_status != 'ok') {
                setTimeout(function() { get_task(search_engine, keyword, domain); }, 500);
            }
            else {
                $("#" + search_engine + ' span').remove();
            }
        },
        cache: false
    });
}

function init_result() {
    $("#google").html('');
    $("#baidu").html('');
    $("#bing").html('');
}

$(document).ready(function() {
    $("#search").submit(function() {
        var keyword = $("#keyword").val();
        var domain = $("#domain").val();
        init_result();
        $("input:checkbox:checked").each(function() {
            var search_engine = $(this).val()
            show_result(search_engine, keyword, domain);
        });
        return false;
    });
});
