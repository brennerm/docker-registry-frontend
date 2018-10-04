var button = $("#connection_test");
var url = $("#url");
var user = $("#user");
var password = $("#password");

button.click(function() {
    $.ajax({
        url: "/test_connection",
        method: 'POST',
        data: {
            url: url.val(),
            user: user.val(),
            password: password.val()
        },
        success: function(data) {
            button.attr("class","btn btn-success");
        },
        error: function(data) {
            button.attr("class","btn btn-danger");
        }
    });
});

url.change(function() {
    button.attr("class","btn btn-default");
})
