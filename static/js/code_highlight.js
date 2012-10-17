$(document).ready(function () {
    var show = function(msg){$("#separator").text(msg)};

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