$(document).ready(function(){
    $('#body-comment .article-item').hover(function(){
        var h = $(this).height();
        $(this).css('height', '100%');
        var h2 = $(this).height();
        $(this).css('height', h + 'px');
        $(this).animate({'height': h2 < 255 ? 255 : h2});
    }, function(){
        $(this).animate({'height': '225px'});
    });
});
