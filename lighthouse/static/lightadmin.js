(function($) {
    $(document).ready(function($) {
        $(".object-tools").append('<li><a href="javascript:alertLight()">Blink Light</a></li>');
        $(".object-tools").append('<li><a href="javascript:onLight()">On</a></li>');
        $(".object-tools").append('<li><a href="javascript:offLight()">Off</a></li>');
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

function onLight() {
    (function($) {
        $.ajax({
            type: "GET",
            url: "/authentication/staff_member_get_token",
            success: function(data) {
                var token = data["token"];
                $.ajax({
                    type: "POST",
                    url: "/lighthouse/lights",
                    headers: {
                        "Authorization" : "Token " + token,
                    },
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    data: JSON.stringify({
                        "which" : parseInt(document.getElementById("id_which").value),
                        "on" : true,
                        "hue" : 0,
                        "sat" : 0,
                        "bri" : 255,
                        "transitiontime" : 0,
                    }),
                    success: function(data) {
                    }
                });
            }
        });
    })(django.jQuery);  
}

function offLight() {
     (function($) {
        $.ajax({
            type: "GET",
            url: "/authentication/staff_member_get_token",
            success: function(data) {
                var token = data["token"];
                $.ajax({
                    type: "POST",
                    url: "/lighthouse/lights",
                    headers: {
                        "Authorization" : "Token " + token,
                    },
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    data: JSON.stringify({
                        "which" : parseInt(document.getElementById("id_which").value),
                        "on" : false,
                        "hue" : 0,
                        "sat" : 0,
                        "bri" : 255,
                        "transitiontime" : 0,
                    }),
                    success: function(data) {
                    }
                });
            }
        });
    })(django.jQuery); 
}