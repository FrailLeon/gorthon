$(document).ready(function () {

    $("#btn_color").click(function(){
        $.post("/code_highlight", {
            'type': $("#lang-option").val(),
            'code': $("#code").val(),
            'need_no': $(".line-no").attr("checked") ? true : false
            },
            function(html){
                html = html['html'];
                $(".code-src").html(html);
        }, 'json');
        $(".code-type").text($("#lang-option").find("option:selected").text());
        $(".code-box").show();
    });
});
