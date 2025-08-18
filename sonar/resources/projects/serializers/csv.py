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

"""CSV serializer for projects."""

import csv

from flask import stream_with_context
from flask_resources.serializers import BaseSerializer
from invenio_records_rest.serializers.csv import CSVSerializer as BaseCSVSerializer
from invenio_records_rest.serializers.csv import Line


class CSVSerializer(BaseCSVSerializer, BaseSerializer):
    """CSV serializer for HEP Valais projects."""

    def serialize_object(self, obj):
        """Serialize a single object according to the response ctx."""

    def serialize_object_list(self, results):
        """Serialize list to CSV.

        :param results: List of results.
        :returns: A stream to generate CSV rows.
        """

        def generate_csv():
            headers = dict.fromkeys(self.csv_included_fields)
            # Translate header values.
            for key, value in headers.items():
                headers[key] = key

            # Write the CSV output in memory
            line = Line()
            writer = csv.DictWriter(line, delimiter=";", quoting=csv.QUOTE_ALL, fieldnames=headers)
            writer.writerow(headers)
            yield line.read()

            for result in results["hits"]["hits"]:
                data = result["metadata"]
                data["pid"] = result["id"]

                self.format_row(data)

                # Write CSV data for row.
                data = self.process_dict(data)
                writer.writerow(data)
                yield line.read()

        return stream_with_context(generate_csv())

    def format_row(self, data):
        """Format the data for a single row.

        :param data: Data dictionary.
        """
