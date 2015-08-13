(function($) {
    $(document).ready(function($) {
        $(".object-tools").append('<li><a href="javascript:alertLight()">Blink Light</a></li>');
    });
})(django.jQuery);

function alertLight() {
    (function($) {
        $.ajax({
            type: "GET",
            url: "/authentication/staff_member_get_token",
            success: function(data) {
                var token = data["token"];
                $.ajax({
                    type: "POST",
                    url: "/lighthouse/alert",
                    headers: {
                        "Authorization" : "Token " + token,
                    },
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    data: JSON.stringify({"which" : parseInt(document.getElementById("id_which").value)}),
                    success: function(data) {
                    }
                });
            }
        });
    })(django.jQuery);  
}