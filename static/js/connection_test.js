var button = $("#connection_test");
var url = $("#url");

button.click(function() {
    $.ajax({
        url: "/test_connection",
        data: {
            url: url.val()
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