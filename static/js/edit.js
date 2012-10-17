$(document).ready(function () {
    $("#article-title").focus();
    $("#submit, #save, #preview").click(function(){
        var title = $("#article-title").val();
        var content = editor.html();
        var error = title == "" ? "请输入标题" : (content == "" ? "请输入内容" : false);
        if(error){
            alert(error+"!!");
            return false;
        }
        var type = $("#type a[class=current]").text(); // 类型(原创 | 转载 | 翻译)
        $.post("/post", {
            "operation": $(this).attr("id"), // 操作类型(保存 | 发表)
            "title": title,
            "content": content,
            "tags": $.map($("#tags a[class*=current]"), function(tag){return tag.text;}).join(" "), // 标签
            "type": type,
            "classes": $.map($("#classes a[class=current]"), function(cls){return cls.id.substr(8)}).join(" "), // 分类
            "origin": type == "转载" ? $("#origin-url").val() : "",
            "announcement": type == "转载" ? $("#announcement").val() : "",
            "pwd": $("#settings-pwd").hasClass("current"),
            "reviewable": !$("#settings-reviewable").hasClass("current"),
            "reproduced": !$("#settings-reproduced").hasClass("current"),
            "aid": $("#article-id").val()
        }, function(ret){
            var msg = ret.msg;
            alert(msg);
        }, 'json');
    });

    $("#article-settings a").die().live("click", function(){ // 用die和live使得后续添加的元素难免绑定此事件
        var self = $(this);
        var parent = self.parent();
        var pid = parent.attr("id");
        if(pid == "type"){ // 原创 | 转载 | 翻译
            self.siblings().removeClass("current").end().addClass("current");
            if(self.attr("id") == "reproduced"){
                $("#reproduce-box").toggle("fast");
                $("#origin-url").focus().select();
            }else{
                $("#reproduce-box").hide("fast");
            }
        }else if(pid == "classes"){ // 分类
            self.toggleClass("current");
            var $default = parent.children(":first");
            if($default.attr("id") == self.attr("id")){
                self.siblings().removeClass("current").end().addClass("current");
            }
            else if(parent.children(".current").length == 0){
                $default.addClass("current");
            }else{
                $default.removeClass("current");
            }
        }else{ // 标签
            self.toggleClass("current");
        }
    });

    // 新增分类
    var $add = $("#article-settings .add");
    $add.hover(function(){
        if(!$add.is(":focus"))
            $(this).val("点击输入");
    }, function(){
        if(!$add.is(":focus"))
            $(this).val("添加＋");
    });
    $add.blur(function(){
        $(this).val("添加＋");
        $(this).css("width", "60px");
    });
    $add.click(function(){
        $(this).css("width", "auto");
        $(this).attr("size", 25);
        $(this).val("空格分隔多个，回车提交").select();
    });

    // 处理添加事件
    var $adds = $("#add-classes, #add-tags, #add-url");
    $adds.unbind("input propertychange change");
    $adds.bind("input propertychange change", function(){
        var self = $(this);
        var val = self.val();
        if(val.length > 15 && self.attr("id") != "add-url")
            self.val(val.substring(0, 15));
        if(val.length > 75 && self.attr("id") == "add-url")
            self.val(val.substring(0, 75));
    });
    $adds.keyup(function(e){
        var self = $(this);
        self.css("width", "auto");
        var txt = self.val().trim();
        var size = txt.replace(/[^\u0000-\u00ff]/g, "aa").length;
        size = size > 8 ? size : 8;
        self.attr("size", size);
        if(e.keyCode == 13 && txt != ""){
            if(txt.indexOf("回车提交") != -1)
                return self.blur();
            var _unique = function(id){
                var classes = new Array(); // 得到所有分类 | 标签
                $.each($(id + " a"), function(i, v){classes[i] = v.text;});
                $.each(tags, function(i, tag){
                    if($.inArray(tag, classes) != -1){ // 已经存在此分类
                        tags = $.grep(tags, function(v, i){return v != tag;}); // 将已经存在的元素滤去
                        var $ele = $(id + " a:contains(" + tag + ")").filter(function(i, v){return v.text == tag});
                        $ele.slideToggle();
                        $ele.slideToggle();
                        $ele.addClass("current");
                    }
                });
                return tags;
            };
            var tags = $.unique(txt.split(" "));
            if(self.attr("id") == "add-classes"){ // 添加分类
                tags = _unique("#classes"); // 得到滤去已经存在的分类
                if(tags.length > 0){
                    $.post("/add-classes", {"cls": tags.join(" ")}, function(ret){
                        $.each(ret, function(id, cls){
                            self.before($('<a id ="classes-' + id + '" class="current">' + cls + '</a>'));
                            self.parent().children(":first").removeClass("current");
                        });
                    }, "json");
                }
            }else{ // 添加标签
                $.each(_unique("#tags"), function(i, tag){
                    self.before('<a class="tags current">' + tag + '</a>');
                });
            }
            self.css("width", "60px");
            self.blur();
        }
    });

    // 设置
    $("#settings a").click(function(){
        var self = $(this);
        self.text({
            "settings-pwd": ["访问密码：不要", "访问密码：需要"],
            "settings-reviewable": ["可否评论：可以", "可否评论：不可"],
            "settings-reproduced": ["允许转载：允许", "允许转载：不许"]
        }[self.attr("id")][self.hasClass("current") ? 0 : 1]);
    });

    // 编辑器
    var editor = KindEditor.create('#editor', {
        width: "720px",
        minWidth: "720px",
        height: "550px",
        items: [
            'source', '|', 'undo', 'redo', '|', 'preview', 'print', 'template',
            'plainpaste', 'wordpaste', '|', 'justifyleft', 'justifycenter', 'justifyright',
            'justifyfull', 'insertorderedlist', 'insertunorderedlist', 'indent', 'outdent', 'subscript',
            'superscript', 'clearhtml', 'quickformat', '|', 'code', 'pagebreak', 'fullscreen', '/',
            'formatblock', 'fontname', 'fontsize', '|', 'forecolor', 'hilitecolor', 'bold',
            'italic', 'underline', 'strikethrough', 'lineheight', 'removeformat', '|', 'image',
            'flash', 'media', 'insertfile', 'table', 'hr', 'emoticons',  'baidumap',
            'link', 'unlink', 'anchor', "highlight"
        ],
        resizeType: 1, // 只可改变高度
        syncType: "" // 不自动同步
    });
    KindEditor.lang({
        highlight: "你好"
    });
/*
    setInterval(function(){
        var $ifm = $($("iframe")[0]);
        var $body = $($ifm[0].contentWindow.document.body);
        $ifm.height($body.height());
    }, 10);*/
    // add handler here
});
