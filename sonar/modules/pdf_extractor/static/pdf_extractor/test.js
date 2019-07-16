/*
 * Swiss Open Access Repository
 * Copyright (C) 2019 RERO
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, version 3 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
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