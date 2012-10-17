$(document).ready(function(){
    $("#right-box a, #profile").click(function(e){
        e.preventDefault();
        var self = $(this);
        var $body = $("#body");
        $.post("/backstage", {"operation": self.attr("id")}, function(data){
            switch(self.attr("id")){
                case "profile": // 个人中心
                    $("#body").html(data);
                    break;
                case "article": // 文章管理
                    break;
                case "comment": // 评论管理
                    $("#body").html(data);
                    break;
                case "class": // 分类管理
                    var colors = ["purple", "red", "orange", "blue", "green", "black",
                    "yellow-orange", "brown", "cyan", "dark-red", "light-green"];
                    $body.empty();
                    var html = "<div class='box-container' id='classes'>";
                    for(var i in data){
                        var r = parseInt(Math.random() * 11);
                        html += "<a class='" + colors[r] + "'><input class='cls' value='" + data[i] + "'/>"
                            + "<label id='" + i + "' title='删除'>×</label></a>";
                    }
                    r = parseInt(Math.random() * 11);
                    html += "<a class='" + colors[r] + "'><input type='text' class='cls' placeholder='添加分类' /></a></div>";
                    $body.append($(html));
                    $("#classes a:first").empty().append("<a class='cls'>默认分类</a>");
                    // 删除分类
                    $("#classes a label").die().live("click", function(){
                        var self = $(this);
                        var id = $(this).attr("id");
                        if(id == "1")return;
                        $.get("/delete/class/" + id, function(suc){
                            if(!suc)
                                alert("删除失败");
                            else
                                self.parent().remove();
                        });
                    });
                    // 添加分类
                    $("#classes a input:last").blur(function(e){
                        $(this).val("");
                    });
                    $("#classes a input").die().live("click", function(e){
                        $(this).select();
                    });
                    $("#classes a input").keyup(function(e){
                        var self = $(this);
                        var txt = self.val();
                        if(e.keyCode == 13 && txt != "" && txt!=self.attr("title")){
                            var same = 0;
                            $(".cls").each(function(){
                                if($(this).val() == txt){
                                    same += 1;
                                }
                                if(same == 2)
                                    return false;
                            });
                            if(same == 2){
                                alert("已经存在此分类");
                                self.select();
                                return false;
                            }
                            var id = self.next().attr("id");
                            $.post("/add-classes", {"cls": txt, "id": id}, function(data){
                                for(var i in data){
                                    if(i == "-1")
                                        return alert(data[i]);
                                    r = parseInt(Math.random() * 11);
                                    if(!id){ // 添加
                                        self.parent().before($(
                                            "<a class='" + colors[r] + "'><input class='cls' value='" + data[i] + "'/>"
                                                + "<label id='" + i + "' title='删除'>×</label>"
                                        ));
                                        self.val("");
                                    }
                                    self.attr("title", txt);
                                }
                            });
                        }
                    }).mouseenter(function(){
                            // 只有在最初进入即没有获得焦点的时候才记录title
                            if($(this).is(":not(:focus)"))$(this).attr("title", $(this).val());
                    }).blur(function(){
                            $(this).val($(this).attr("title"));
                    });
                    break;
                case "tag": // 标签管理
                    break;
                case "link": // 友链管理
                    break;
                case "strategy": // 图表统计
                    break;
            }  // enf switch
            $('#bread-crumbs').text($('label', self).text());
        });
    });
    //$("#class").click(); // 自动进入分类管理界面
    //$("#profile").click();
    $("#comment").click(); // 自动进入分类管理界面
});
