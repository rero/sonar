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

"""Dublin Core serializer."""

from invenio_records_rest.serializers.dc import DublinCoreSerializer


class SonarDublinCoreSerializer(DublinCoreSerializer):
    """Marshmallow based DublinCore serializer for records."""

    def dump(self, obj, context=None):
        """Serialize object with schema.

        Mandatory to override this method, as invenio-records-rest does not
        use the right way to dump objects (compatible with marshmallow 3.9).
        """
        return self.schema_class(context=context).dump(obj)
