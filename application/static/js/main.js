var tableCategory;
var tablePaper;
var datetimePicker;

// Run from start
$(function () {
    // Date time picker
    datetimePicker = $('#dateTimePicker').datetimepicker({
        format: 'YYYYMMDD',
        locale: 'vi',
        showClear: true,
        minDate: new Date(2018, 2, 21),
        maxDate: new Date()
    });

    // Category table
    tableCategory = $('#tableCategory').DataTable({
        pageLength: 6,
        paging: false,
        searching: false,
        ordering: false,
        info: false,
        select: true,
        columnDefs: [
            {
                "targets": [0],
                "visible": false
            }
        ]
    });
    $('#tableCategory tbody').on( 'click', 'tr', function () {
    if ( $(this).hasClass('selected') ) {
        $(this).removeClass('selected');
    }
    else {
        tableCategory.$('tr.selected').removeClass('selected');
        $(this).addClass('selected');
    }
    });

    // Paper table
    tablePaper = $('#tablePaper').DataTable({
        select: true,
        columnDefs: [
            {
                "targets": [0],
                "width": 850
            }
        ]
    });
    $('#tablePaper tbody').on( 'click', 'tr', function () {
    if ( $(this).hasClass('selected') ) {
        $(this).removeClass('selected');
    }
    else {
        tablePaper.$('tr.selected').removeClass('selected');
        $(this).addClass('selected');
    }
    });

    $.get(window.location.origin + "/category", function (bean, status) {
        if (status === "success" && bean.result === true){
            // Load category into category table
            data = bean.data;
            for (var current = 0; current < data.length; current ++){
                tableCategory.row.add([
                    data[current],
                    data[current]
                ]).draw(false);
            }
        } else {
            console.log('failed')
        }
    });


});

function loadPaper(){
    var category = tableCategory.row('.selected').data()[0];
    var date = $('#inputDataTimePicker')[0].value;

    var data = {
        category: category,
        date: date
    };

    $.post(window.location.origin + "/get-papers-cat-dat", data,
        function (bean, status) {
            if (status === 'success' && bean.result === true){
                data = bean.data;
                tablePaper.clear();

                for (var current = 0; current < data.length; current++){
                    tablePaper.row.add([
                        data[current][0],
                        '<button type="button" class="btn btn-labeled btn-default" id="btnOpenDocument"">' +
                        '<span class="btn-label">' +
                        '<i class="glyphicon glyphicon-open-file"></i>' +
                        '</span>Mở bài báo' +
                        '</button>' +
                        '<button type="button" class="btn btn-labeled btn-default" id="btnLoadKeyword"">' +
                        '<span class="btn-label">' +
                        '<i class="glyphicon glyphicon-tasks"></i>' +
                        '</span>Tải từ khóa' +
                        '</button>'
                    ]).draw(false);
                }
            } else{
            }
        }
    );
};