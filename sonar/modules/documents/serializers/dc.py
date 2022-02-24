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

from dcxml import simpledc
from flask_resources.serializers import SerializerMixin

from sonar.modules.documents.serializers.schemas.dc import DublinCoreSchema


class SonarDublinCoreXMLSerializer(SerializerMixin):
    """DublinCore serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        self.schema_class = DublinCoreSchema

    def transform_record(self, obj):
        """Tranform record."""
        # TODO: Remove this hack after migrate to invenio ressources
        return self.schema_class().dump(dict(metadata=obj))

    def serialize_object_xml(self, obj):
        """Serialize a single record and persistent identifier to etree.

        :param obj: Record instance
        """
        json = self.transform_record(obj["_source"])
        return simpledc.dump_etree(json)


def sonar_dublin_core(pid, record):
    """Get DublinCore XML for OAI-PMH."""
    return SonarDublinCoreXMLSerializer()\
        .serialize_object_xml(record)
