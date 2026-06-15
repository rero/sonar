// SPDX-FileCopyrightText: Fondation RERO+
// SPDX-License-Identifier: AGPL-3.0-or-later

function syntaxHighlight(json) {
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

$(document).ready(function () {
    var context = 'metadata'

    $('#metadata').click(function() {
        context = 'metadata'
    })

    $('#fulltext').click(function() {
        context = 'full-text'
    })

    $('#pdfForm').submit(function () {
        var file_data = $('#file').prop('files')[0];
        var form_data = new FormData();
        form_data.append('file', file_data);

        $('#loading').removeClass('d-none')

        $.ajax({
            url: '/api/pdf-extractor/' + context,
            dataType: 'json',
            cache: false,
            contentType: false,
            processData: false,
            data: form_data,
            type: 'post',
            success: function (data) {
                var json = JSON.stringify(data, null, 2)
                
                $('#loading').addClass('d-none')
                $('#error').addClass('d-none')
                $('#result').removeClass('d-none').html(syntaxHighlight(json))
            },
            error: function (data) {
                $('#loading').addClass('d-none')
                $('#result').addClass('d-none')
                $('#error').removeClass('d-none').text(data.responseJSON.error)
            }
        });

        return false;
    })
})