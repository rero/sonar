# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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

"""JSON serializer for SONAR."""

from flask import request
from invenio_jsonschemas import current_jsonschemas
from invenio_records_rest.serializers.json import \
    JSONSerializer as _JSONSerializer


class JSONSerializer(_JSONSerializer):
    """JSON serializer for SONAR."""

    def preprocess_record(self, pid, record, links_factory=None, **kwargs):
        """Prepare record for serialization."""
        if request and request.args.get('resolve') == '1':
            record = record.replace_refs()

        return super(JSONSerializer,
                     self).preprocess_record(pid=pid,
                                             record=record,
                                             links_factory=links_factory,
                                             kwargs=kwargs)


def schema_from_context(_, context, data, schema):
    """Get the record's schema from context."""
    record = (context or {}).get('record', {})

    return record.get('$schema', current_jsonschemas.path_to_url(schema))
