# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Serializers."""

import csv

from flask import current_app
from invenio_records_rest.serializers.csv import \
    CSVSerializer as BaseCSVSerializer
from invenio_records_rest.serializers.csv import Line
from invenio_records_rest.serializers.response import record_responsify, \
    search_responsify

from sonar.modules.serializers import JSONSerializer
from sonar.theme.views import format_date

from ..schemas import RecordSchema


class CSVSerializer(BaseCSVSerializer):
    """Mixin serializing records as JSON."""

    def _format_csv(self, records):
        """Return the list of records as a CSV string.

        :param list recors: Records list
        """
        assert len(records) == 1
        record = records[0]
        headers = [
            'organisation', 'type', 'documents', 'full_text', 'no_full_text'
        ]

        # Write header
        line = Line()
        writer = csv.DictWriter(line, fieldnames=headers)
        writer.writeheader()
        yield line.read()

        # Dump values
        for value in record['metadata']['values']:
            value['documents'] = len(value['pids'])
            value['no_full_text'] = value['documents'] - value['full_text']
            value.pop('pids', None)
            writer.writerow(value)
            yield line.read()

    def process_dict(self, dictionary):
        """Transform record dict with nested keys to a flat dict.

        Needed to override the parent method to do nothing.
        :param dictionary: An input dictionary
        :returns: an untouched dictionary
        :rtype: dict
        """
        return dictionary


# Serializers
# ===========
#: JSON serializer definition.
json_v1 = JSONSerializer(RecordSchema)
#: CSV serializer definition.
csv_v1 = CSVSerializer()

# Records-REST serializers
# ========================
#: JSON record serializer for individual records.
json_v1_response = record_responsify(json_v1, 'application/json')
#: JSON record serializer for search results.
json_v1_search = search_responsify(json_v1, 'application/json')


def csv_record_responsify(serializer, mimetype):
    """Create a Records-REST response serializer.

    This function is the same as the `invenio-records-rest`, but it adds an
    header to change the download file name.

    :param serializer: Serializer instance.
    :param mimetype: MIME type of response.
    :returns: Function that generates a record HTTP response.
    """

    def view(pid, record, code=200, headers=None, links_factory=None):
        response = current_app.response_class(serializer.serialize(
            pid, record, links_factory=links_factory),
                                              mimetype=mimetype)
        response.status_code = code
        response.cache_control.no_cache = True
        response.set_etag(str(record.revision_id))
        response.last_modified = record.updated
        if headers is not None:
            response.headers.extend(headers)

        # set the output filename
        date = format_date(record.created, '%Y%m%d%H%M')
        filename = f'stats-{date}.csv'
        if not response.headers.get('Content-Disposition'):
            response.headers['Content-Disposition'] = \
                f'attachment; filename="{filename}"'

        return response

    return view


#: CSV record serializer for individual records.
csv_v1_response = csv_record_responsify(csv_v1, 'text/csv')

__all__ = (
    'json_v1',
    'json_v1_response',
    'json_v1_search',
)
