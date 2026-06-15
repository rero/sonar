# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""CSV serializer for projects."""

import csv

from flask import stream_with_context
from flask_resources.serializers import BaseSerializer
from invenio_records_rest.serializers.csv import CSVSerializer as BaseCSVSerializer
from invenio_records_rest.serializers.csv import Line


class CSVSerializerMixin(BaseCSVSerializer, BaseSerializer):
    """Project csv serializer mixin."""

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
            for key in headers:
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


class CSVSerializer(CSVSerializerMixin):
    """Projects cvs serializer."""

    def __init__(self):
        """Constructor."""
        super().__init__(
            csv_included_fields=[
                "pid",
                "name",
                "description",
                "startDate",
                "endDate",
            ],
            csv_excluded_fields=[],
            header_separator="_",
        )
