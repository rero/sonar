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

"""Test projects CSV serializer."""

from sonar.resources.projects.serializers.csv import CSVSerializer


def test_serializer(app):
    """Test serializer."""
    csv = CSVSerializer(csv_included_fields=["pid"])

    records = {
        "hits": {"hits": [{"id": "1", "metadata": {}}, {"id": "2", "metadata": {}}]}
    }

    result = "".join(csv.serialize_object_list(records))
    assert result == '"pid"\r\n"1"\r\n"2"\r\n'
