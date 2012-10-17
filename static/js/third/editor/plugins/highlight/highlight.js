KindEditor.plugin('highlight', function(K) {
    var self = this, name = 'highlight';
    self.clickToolbar(name, function() {
        var lang = self.lang(name + '.'),
            html = [
                '<div class="language-wrapper">',
                    '<select id="lang-option">',
                        '<option value=".c">C</option>',
                        '<option value=".cpp">C++</option>',
                        '<option value=".css">CSS</option>',
                        '<option value=".html">Html</option>',
                        '<option value=".js">JavaScript</option>',
                        '<option value=".py" selected="selected">Python</option>',
                    '</select>',
                    '<textarea rows="10" cols="60" id="code-textarea"></textarea>',
                '</div>'].join(""),
            dialog = self.createDialog({
                name : name,
                width : 450,
                title : self.lang(name),
                body : html,
                yesBtn : {
                    name : self.lang('yes'),
                    click : function(e) {
                        var box = $([
                                '<link href="/static/js/third/editor/plugins/highlight/code_box.css" rel="stylesheet" type="text/css"/>',
                                '<link href="/static/js/third/editor/plugins/highlight/python.css" rel="stylesheet" type="text/css"/>',
                            '<div class="code-box">',
                            '<div class="code-header">',
                            '<div class="code-type"></div>',
                            '</div>',
                        '<div class="code-src"></div>',
                        '<div class="code-labels">',
                            '<label class="line-no">隐藏行号</label>',
                            '<label class="fixed-height">固定高度</label>',
                        '<label class="bar">折叠</label>',
                        '</div>',
                        '</div>'].join(""));
                        $("#editor").before(box);
                        $.post("/code_highlight", {
                                'type': $("#lang-option").val(),
                                'code': $("#code-textarea").val(),
                                'need_no': $(".line-no").attr("checked") ? true : false
                            },
                            function(code){
                                code = code['html'];
                                $(".code-src").html(code);
                                self.insertHtml($(".code-src").html()).hideDialog().focus();
                            }, 'json');
                        $(".code-type").text($("#lang-option").find("option:selected").text());
                        $(".code-box").show();
                    }
                }
            }),
            textarea = K('textarea', dialog.div);
        textarea[0].focus();
    });
    // 滚动条动态显示 / 隐藏
    $(".code-box").hover(
        function(e){
            $(this).children(".code-src").css("overflow", "auto");
        },
        function(){
            $(this).children(".code-src").css("overflow", "hidden");
            $(this).children(".code-labels").hide("fast");
        });

    $(".code-box").mousemove(function(e){
        var y = e.pageY;
        var offset_y = $(this).position().top;
        if($(this).height() + offset_y -10 < y)
            $(this).children(".code-labels").hide("fast");
        else if(offset_y + 25 < y && $(this).find(".bar").text() == "折叠"){
            $(this).children(".code-labels").css({
                display: "block",
                top: y - offset_y - 15 + "px"
            });
        }else{
            $(this).children(".code-labels").css({
                display: "block",
                top: "9px"
            });
            $(this).children(".code-labels").show("fast");
        }
    });

    // 显示行号
    $(".line-no").click(function(){
        if($(this).text() == "显示行号"){
            $(".line-no").text("隐藏行号");
            $(".linenodiv").show(500);
            $(".highlight pre").css({
                "white-space": "pre"
            });
        }else{
            $(".line-no").text("显示行号");
            $(".linenodiv").hide();
            $(".highlight pre").css({
                "white-space": "pre-wrap"
            });
        }
    });

    // 固定高度
    $(".fixed-height").click(function(){
        if($(this).text() == "固定高度"){
            $(this).text("自适高度");
            $(".code-src").css({
                "overflow-y": "auto",
                height:"300px"
            });
        }else{
            $(this).text("固定高度");
            $(".code-src").css({
                "overflow-y": "hidden",
                height:"100%"
            });
        }
    });

    // 代码折叠
    $(".bar").click(function(){
        self = $(this);
        if(self.text() == "折叠"){
            self.text("展开");
        }else{
            self.text("折叠");
        }
        self.parents(".code-box:first").find(".code-src").animate({
            height: "toggle"
        }, 500);
    });
});