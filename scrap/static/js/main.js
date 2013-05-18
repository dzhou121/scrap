$(document).ready(function() {
    $("#search").submit(function() {
        $("#Google").html('');
        $("#Baidu").html('');
        $("#Bing").html('');
        $("input:checkbox:checked").each(function() {
            var search_engine = $(this).val()
            $("#" + search_engine).html('<h3>' + search_engine + '</h3><hr>');
            $.ajax({
                url: '/search', 
                type: 'POST',
                data: {
                    'keyword': $("#keyword").val(),
                    'domain': $("#domain").val(),
                    'search_engine': search_engine,
                },
                beforeSend: function() {
                    $("#" + search_engine).append('<div class="result"><p class="alert alert-success">now searching</p></div>');
                },
                success: function(data) {
                    var links = data['links'];
                    if(links.length == 0) {
                        $("#" + search_engine + ' .result').html('<p class="alert alert-important">0 results</p>');
                    }
                    else {
                        var html = '<table class="table table-bordered table-striped">';
                        html = html + '<tr><th>Rank</th><th>Url</th></tr>'; 
                        $.each(links, function(index, value){
                            html = html + '<tr><td>' + value['rank'] + '</td><td>' + value['url'] + '</td></tr>';
                        });
                        html = html + '</table>';
                        $("#" + search_engine + ' .result').html(html);
                    }
                },
                error: function(data) {
                    $("#" + search_engine + ' .result').html('<p class="alert alert-error">Unknown Error</p>');
                },
                cache: false
            });
        });
        return false;
    });
});
