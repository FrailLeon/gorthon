$(document).ready(function () {
    if($.browser.msie && $.browser.version != "9.0"){
        //document.write("<span style='color: red;margin: 100px 10%;font-size: 30px;text-align: center;width: 30%;'>本站不支持ie内核的浏览器访问<span>");
        alert("您使用的是基于IE内核的浏览器，请更换其他浏览器(如chrome, firefox, opera, ie9等)，否则界面显示可能出现问题");
    }
    $(window).scroll(function(){
        if($(document).scrollTop() > 300)
            $("#go-top").slideDown("slow");
        else
            $("#go-top").slideUp("slow");
    });

    $("#go-top").click(function(){
        var go = function(){
            var h = $(window).scrollTop();
            h -= Math.ceil(h * 15 / 100);
            if(h < 5) h = 0;
            $("html, body").scrollTop(h);
            if(h == 0) clearInterval(timer);
        };
        var timer = setInterval(go, 10);
    });

    $(".nav li").click(function(){
        $(".nav li").removeClass("current");
        $(this).addClass("current");
    });

    $(".nav li").hover(
        function(){
            $(this).children("a").text($(this).text().split(" ").reverse().join(" "));
            $(this).animate({
                paddingRight: "+=5px"
            }, "fast");
        },
        function(){
            $(this).children("a").text($(this).text().split(" ").reverse().join(" "));
            $(this).animate({
                paddingRight: "-=5px"
            }, "fast");
    });

    $("#sidebar").mouseenter(function(e){
        if(e.pageY>500){
            $("#right-sidebar").show("fast");
            $("#footer-counter").hide("fast");
            $("#pwd").attr("placeholder", "为自由而生，为自由而死");
            if($("#btn-login").text() != "注销")$("#pwd").val("").focus(); // ff
        }
        $("#zen").css("height", "0");
        $("#empty-line, #footer-slogan").hide("fast");
    });
    $("#sidebar").mouseleave(function(){
        $("#right-sidebar").hide("fast");
        $("#footer-counter").show("fast");
        $("#zen").css({
            height: "1030px",
            top: "0"
        });
        $("#empty-line, #footer-slogan").show("fast");
    });

    var list = ['The Zen of Python, by Tim Peters', 'Beautiful is better than ugly.', 'Explicit is better than implicit.', 'Simple is better than complex.', 'Complex is better than complicated.', 'Flat is better than nested.', 'Sparse is better than dense.', 'Readability counts.', "Special cases aren't special enough to break the rules.", 'Although practicality beats purity.', 'Errors should never pass silently.', 'Unless explicitly silenced.', 'In the face of ambiguity, refuse the temptation to guess.', 'There should be one-- and preferably only one --obvious way to do it.', "Although that way may not be obvious at first unless you're Dutch.", 'Now is better than never.', 'Although never is often better than *right* now.', "If the implementation is hard to explain, it's a bad idea.", 'If the implementation is easy to explain, it may be a good idea.', "Namespaces are one honking great idea -- let's do more of those!"]
    var txt = $('#zen');  // The container in which to render the list
    var options = {
        duration: 1000,          // Time (ms) each blurb will remain on screen
        rearrangeDuration: 1000, // Time (ms) a character takes to reach its position
        effect: 'slideTop',        // Animation effect the characters use to appear
        centered: true           // Centers the text relative to its container
    };
    txt.textualizer(list, options); // textualize it!
    txt.textualizer('start'); // start

    // 登录 | 注销
    $("#btn-login").click(function(e){
        var self = $("#btn-login");
        var $pwd = $("#pwd");
        if(self.text() == "登录"){
	    e.preventDefault();
            if($pwd.val().length == 0 || self.hasClass("wait")){
                return $pwd.attr("placeholder", "Born fo liberty, die for freedom.").focus();
            }
            self.addClass("wait").text("稍后回来...");
            $.post("/login", {"lol": enc($("#pwd").val())}, function(data){
                if(data.lol){
                    self.removeClass("wait").text("注销");
                    $pwd.val("").attr("placeholder", "为自由而生，为自由而死").attr("readonly", "readonly");
                    $("#post-wrapper").load("admin");
                    window.location = '/';
                }else{
                    self.removeClass("wait").text("登录");
                    $pwd.val("").attr("placeholder", "Born fo liberty, die for freedom.");
                }
            });
        }else{
            /*
            // 注销
            $.get("/logout", function(){
                window.location = "/";
            });
            */
        }
    });
    $("#pwd").keyup(function(e){
        $("#btn-login").attr("disabled","true");
        if(e.keyCode == 13 && !$("#btn-login").hasClass("wait")){
            $("#btn-login").click();
            e.stopPropagation();
        }
    });

    // header.js
    var showDate = function(){
        var datetime = new Date();
        var months = ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"];
        var weekdays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
        var date = datetime.getDate();
        date = date < 10 ? "0" + date : date;
        var year = datetime.getFullYear();
        var month = months[datetime.getMonth()];
        month = month < 10 ? "0" + month : month;
        var weekday =  weekdays[datetime.getDay()];
        var hour = datetime.getHours();
        hour = hour < 10 ? "0" + hour : hour;
        var minute = datetime.getMinutes();
        minute = minute < 10 ? "0" + minute : minute;
        var second = datetime.getSeconds();
        second = second < 10 ? "0" + second : second;
        var html = '<ul class="clock-item"><li class="clock-item-number">' + date + '</li><li class="clock-item-chinese">' + month + "&nbsp;&nbsp;&nbsp;" + weekday + '</li></ul>';
        html += '<span>' + year + '</span>';
        html += '<ul class="clock-item"><li class="clock-item-number">' + hour + '</li><li class="clock-item-chinese">时</li></ul>';
        html += '<ul class="clock-item"><li class="clock-item-number">' + minute + '</li><li class="clock-item-chinese">分</li></ul>';
        html += '<ul class="clock-item"><li class="clock-item-number">' + second + '</li><li class="clock-item-chinese">秒</li></ul>';
        $("#clock").html(html);
    };
    showDate();
    setInterval(showDate, 1000); // 1s

    // 动态显示 | 隐藏 rss
    $("#header-wrapper").hover(
        function(){
        $("#rss").show("fast");
    }, function(){
        $("#rss").hide("fast");
    });

    // rss
    $("#rss").click(function(){
        alert("s");
    });

    // 自定义的弹窗插件
    jQuery.gorthon = {
        doModel: function(option){
            var defaults = {
                "title": "标题",
                "type": "info",
                "content": "内容",
                "btns": ["确定", "取消"]
            };
            var init = function(){
                var options = $.extend(defaults, option);
                var $dlg = $("#decorator .g-dlg");
                var $title = $("#decorator .g-dlg-title");
                var $content = $("#decorator .g-dlg-content");
                var $btns = $("#decorator .g-dlg-btns");
                var $body = $("#decorator .g-dlg-body");
                var html = "";
                $.each(options["btns"], function(i, v){
                    html += "<a class='g-dlg-btn" + i + "' href='" + options["src"].attr("href") + "'>" + v + "</a> ";
                });
                $btns.html(html);

                $title.text(options["title"]);
                $content.html(options["content"]);
                $dlg.slideDown("fast");
                $("#decorator .g-dlg input:first").focus();
                // 拖动弹窗
                $title.mousedown(function(e){
                    $title.addClass("title-move");
                    var offset = $(this).offset();
                    var x = e.pageX - offset.left;
                    var y = e.pageY - offset.top;
                    $dlg.mousemove(function(e){
                        var _x = e.pageX - x;
                        var _y = e.pageY - y;
                        var max_height = $(".g-dlg-mask").height() - $body.height();
                        var max_width = $(".g-dlg-mask").width() - $body.width();
                        _y -=  $(document).scrollTop();
                        _y = _y > max_height ? max_height : (_y < 0 ? 0 : _y);
                        _x = _x > max_width ? max_width : (_x < 0 ? 0 : _x);
                        $body.css({left: _x + "px", top: _y + "px"});
                    });
                    $title.mouseup(function(){
                        $dlg.unbind("mousemove");
                        $title.removeClass("title-move");
                    });
                    e.preventDefault(); // 阻止默认事件，不然鼠标样式会变成光标，因为他会认为你移动的时候再选择文本。
                });
            };
            init();
        }
    };// end 弹窗插件

    $("#decorator .g-dlg-btn0").die().live("click", function(e){
        e.preventDefault();
        var self = $(this);
        var lol = $("#decorator .g-dlg input:first").val();
        if(lol.length == 0 || self.hasClass("wait"))
            return false;
        self.addClass("wait");
        $.post("/delete", {"aid": $(this).attr("href").slice(8, 14),
                                    "lol": enc(lol)}, function(ret){
            self.removeClass("wait");
            var msg = ret.msg;
            var $dlg = $("#decorator .g-dlg");
            var $pwd = $("input:first", $dlg);
            var $err = $("#decorator .error-msg");
            $err.text(msg);
            $err.show("fast");
            if(msg == "删除成功")
                setTimeout(function(){$dlg.slideUp("fast", function(){window.location = "/";})}, 1000);
            else{
                $pwd.focus().select();
                $err.slideUp(4000);
            }
        }, "json");
    });
    $("#decorator .g-dlg-btn1").die().live("click", function(e){
        e.preventDefault();
        $("#decorator .g-dlg").slideUp("fast");
    });

    $("#content .gorthon-dlg").click(function(e){
        e.preventDefault();
        $.gorthon.doModel({
            "title": "此功能需要密码",
            "content": "<input type='password' placeholder='为自由而生，为自由而死' autofocus/><br />"+
                "<span class='error-msg' style='display: none;color: red;'></span>",
            "src": $(this)
        });
    });
    $("#decorator .g-dlg input:first").die().live("keyup", function(e){
        if(e.keyCode == 13){
            $("#decorator .g-dlg-btn0").click();
            e.stopPropagation();
        }else{
            $("#decorator .error-msg").stop().hide("fast");
        }
    });
    $("#big-img .g-dlg-mask, #decorator .g-dlg-mask, .big-img").die().live("click", function(){
        $("#decorator .g-dlg, #big-img").slideUp("fast");
    });


    $("body").keyup(function(e){
        if(e.keyCode == 27){
            $("#decorator .g-dlg").slideUp("fast");
        }
    });
});
