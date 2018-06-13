var categoryTable = $('#categoryTable').DataTable({
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
var paperTable = $('#paperTable').DataTable({
    select: true,
    columnDefs: [
        {
            "targets": [0],
            "width": 500
        }, {
            "targets": [1],
            "visible": false
        }
    ]
});
var datetimePicker = $('#dateTimePicker').datetimepicker({
    format: 'YYYYMMDD',
    locale: 'vi',
    showClear: true,
    minDate: new Date(2018, 2, 21),
    maxDate: new Date()
});
;
// Waiting Dialog
var waitingDialog = waitingDialog || (function ($) {
    'use strict';

    // Creating modal dialog's DOM
    var $dialog = $(
        '<div class="modal fade" data-backdrop="static" data-keyboard="false" tabindex="-1" role="dialog" aria-hidden="true" style="padding-top:15%; overflow-y:visible;">' +
        '<div class="modal-dialog modal-m">' +
        '<div class="modal-content">' +
        '<div class="modal-header"><h3 style="margin:0;"></h3></div>' +
        '<div class="modal-body">' +
        '<div class="progress progress-striped active" style="margin-bottom:0;"><div class="progress-bar" style="width: 100%"></div></div>' +
        '</div>' +
        '</div></div></div>');

    return {
        /**
         * Opens our dialog
         * @param message Custom message
         * @param options Custom options:
         *                  options.dialogSize - bootstrap postfix for dialog size, e.g. "sm", "m";
         *                  options.progressType - bootstrap postfix for progress bar type, e.g. "success", "warning".
         */
        show: function (message, options) {
            // Assigning defaults
            if (typeof options === 'undefined') {
                options = {};
            }
            if (typeof message === 'undefined') {
                message = 'Loading';
            }
            var settings = $.extend({
                dialogSize: 'm',
                progressType: '',
                onHide: null // This callback runs after the dialog was hidden
            }, options);

            // Configuring dialog
            $dialog.find('.modal-dialog').attr('class', 'modal-dialog').addClass('modal-' + settings.dialogSize);
            $dialog.find('.progress-bar').attr('class', 'progress-bar');
            if (settings.progressType) {
                $dialog.find('.progress-bar').addClass('progress-bar-' + settings.progressType);
            }
            $dialog.find('h3').text(message);
            // Adding callbacks
            if (typeof settings.onHide === 'function') {
                $dialog.off('hidden.bs.modal').on('hidden.bs.modal', function (e) {
                    settings.onHide.call($dialog);
                });
            }
            // Opening dialog
            $dialog.modal();
        },
        /**
         * Closes dialog
         */
        hide: function () {
            $dialog.modal('hide');
        }
    };
})(jQuery);

/**
 * FUNCTION
 **/

// load paper list
function loadPapers() {
    // show waiting dialog
    waitingDialog.show('Đang tải danh sách bài báo');
    var category = categoryTable.row('.selected').data()[0];
    var date = $('#inputDataTimePicker')[0].value;

    var data = {
        category: category,
        date: date
    };

    $.post(window.location.origin + "/get-papers-cat-dat", data,
        function (bean, status) {
            if (status === 'success' && bean.code === true) {
                data = bean.data;
                paperTable.clear();
                // Todo: change path to id
                for (var current = 0; current < data.length; current++) {
                    paperTable.row.add([
                        data[current][0],
                        data[current][1],
                        '<button type="button" class="btn btn-labeled btn-default" id="loadPaperBtn"">' +
                        '<span class="btn-label">' +
                        '<i class="glyphicon glyphicon-open-file"></i>' +
                        '</span>Mở bài báo' +
                        '</button>' +
                        '<button type="button" class="btn btn-labeled btn-default" id="loadKeywordsBtn"">' +
                        '<span class="btn-label">' +
                        '<i class="glyphicon glyphicon-tasks"></i>' +
                        '</span>Tải từ khóa' +
                        '</button>'
                    ]);
                }
                paperTable.draw(false);
                waitingDialog.hide();
            } else {
            }
        }
    );
}

// open paper
function loadPaper(row_data) {
    // Todo: change path to id and method GET
    var paper_name = row_data[0];
    var path = row_data[1]; // get path of paper

    var data = {
        path: path
    };
    $.post(window.location.origin + "/load-paper", data, function (bean, status) {
        if (bean.code === true) {
            BootstrapDialog.show({
                type: BootstrapDialog.TYPE_INFO,
                size: BootstrapDialog.SIZE_NORMAL,
                title: paper_name,
                message: bean.data,
                buttons: [{
                    label: 'Đóng',
                    cssClass: 'btn-default',
                    action: function (dialog) {
                        dialog.close();
                    }
                }]
            });
        } else {
            BootstrapDialog.show({
                type: BootstrapDialog.TYPE_WARNING,
                size: BootstrapDialog.SIZE_NORMAL,
                title: paper_name,
                message: 'Bài báo này đã bị xóa!',
                buttons: [{
                    label: 'Đóng',
                    cssClass: 'btn-default',
                    action: function (dialog) {
                        dialog.close();
                    }
                }]
            });
        }
    });
}

// Keyword extracting
function loadKeywords(row_data) {
    // Todo: change path to id and method GET
    var paper_name = row_data[0];
    var path = row_data[1]; // get path of paper

    var data = {
        path: path
    };
    $.post(window.location.origin + "/load-keywords", data, function (bean, status) {
        if (bean.code === true) {
            data = bean.data;
        } else {
        }
    });
}

// paperTable onclick event
paperTable.on('click', 'button', function () {
    var row_data = paperTable.row($(this).parents('tr')).data();
    var btn_id = $(this).attr('id');
    switch (btn_id) {
        case 'loadPaperBtn':
            loadPaper(row_data);
            break;
        case 'loadKeywordsBtn':
            loadKeywords(row_data);
            break;
    }
});

// RUN WHEN THE WEB HAS FINISHED LOADING
$(function () {
    // Category table
    $('#categoryTable tbody').on('click', 'tr', function () {
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
        }
        else {
            categoryTable.$('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }
    });

    // Paper table
    $('#paperTable tbody').on('click', 'tr', function () {
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
        }
        else {
            paperTable.$('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }
    });

    $.get(window.location.origin + "/category", function (bean, status) {
        if (status === "success" && bean.code === true) {
            // Load category into category table
            data = bean.data;
            for (var current = 0; current < data.length; current++) {
                categoryTable.row.add([
                    data[current],
                    data[current]
                ]).draw(false);
            }
        } else {
            console.log('failed')
        }
    });
});
