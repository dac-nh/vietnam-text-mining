// Category table
// Date time picker
$(function () {
    $('#dateTimePicker').datetimepicker({
        format: 'YYYY - MMMM - DD',
        locale: 'vi',
        showClear: true
    });
});

$(document).ready(function () {
    var categoryTable = $('#categoryTable').DataTable({
        pageLength: 6
    });

    $.get(window.location.origin + "/category", function (bean, status) {
        if (status === "success" && bean.result === true){
            // Load category into category table
            data = bean.data;
            for (var current = 0; current < data.length; current ++){
               categoryTable.row.add([
                    data[current],
                    'demo'
               ]).draw(false);
            }
        }
    });
});