$(document).ready(function(){
    $("#body-profile a").mouseenter(function(){
        $(this).children("input").focus().select();
    });

    $("#old").blur(function(){
        var self = $(this);
        var txt = self.val();
        if(txt.length == 0)return;
        $.post("/login", {"lol": enc(txt)}, function(data){
            if(!data.lol){self.val("").attr("placeholder", "旧密码错误");}
            else self.attr("disabled", true).val("").data("pwd", enc(txt)).attr("placeholder", "旧密码正确");
        });
    });

    $("#confirm").blur(function(){
        if($("#new").val() != $(this).val())
            $(this).val("").attr("placeholder", "两次输入的密码不一致").data("err", true);
        else $(this).attr("placeholder", "╭(￣m￣*)╮").data("err", false);
    });

    $("#body-profile a:last").click(function(){
        var self = $(this);
        if(self.hasClass("busy") || $("#confirm").data("err"))
            return false;
        var old = $("#old").data("pwd");
        var new_ = $("#new").val();
        var confirm = $("#confirm").val();
        if([new_, confirm].indexOf("")!=-1){
            return alert("密码不能为空");
        }
        self.addClass("busy");
        $.post("/change-pwd", {"old": old,
            "new": enc(new_), "confirm": enc(confirm)}, function(data){
            alert(data);
            self.removeClass("busy");
        });
    });
});
