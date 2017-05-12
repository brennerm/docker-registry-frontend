

$(document).ready( function () {
    $.extend( $.fn.dataTable.defaults, {
        lengthChange: false
    });

    $('#registry_table').DataTable({
        info: false,
        paging: false,
        searching: false
    });

    $('#repo_table').DataTable();
    $('#tag_table').DataTable();
});