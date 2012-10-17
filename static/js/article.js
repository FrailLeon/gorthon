$(document).ready(function () {
    // 图片缩放
    var $small_img = $("img[src*='small']");
    $small_img.addClass("img-small").attr("title", "点击查看大图").click(function(){
        var url = $small_img.attr("src").replace("small", "raw2");
        var $big = $("<img src='" + url + "' title='点击关闭' class='big-img'>");
        $("#big-img").slideDown("fast");
        $("#img-content").html($big).css({
            left: 200 + "px",
            top: "20px"
        });
    });

    // 编辑器
    var editor = KindEditor.create('#editor', {
        width: "720px",
        minWidth: "720px",
        height: "300px",
        items: [
            'forecolor', 'hilitecolor', 'bold', 'italic', 'underline', '|', 'table',  'baidumap', 'link', 'unlink', '|',
            'justifyleft', 'justifycenter', 'justifyright', 'justifyfull', 'indent', 'outdent', 'subscript',
            'superscript', '|', 'code', 'emoticons'
        ],
        resizeType: 1, // 只可改变高度
        syncType: "" // 不自动同步
    });

    $("#add-comment").click(function(e){
        e.preventDefault();
        var nick = $("#nick").val();
        var mail = $("#email").val();
        var url = $("#url").val();
        var code = $("#code").val();
        var aid = $(this).attr("href");
        var content = editor.html();
        if(content.length == 0 || code.length == 0)
            return alert("请输入评论内容");
        var pid = "";
        var type = "add";
        $.post("/comment", {"content": content, "aid": aid, "nick": nick,
            "code": code, "url": url, "mail": mail, "pid": pid, "type": type
        }, function(ret){
            alert(ret.msg);
        });
    });
});
