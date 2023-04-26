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

from flask_resources.serializers import SerializerMixin
from invenio_oaiserver.utils import sanitize_unicode
from lxml import etree

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

        :param obj: Record instance.
        :returns: an etree element.
        """
        data = self.transform_record(obj["_source"])
        return self.serialize_dict_to_etree(data)

    def serialize_dict_to_etree(self, data):
        """Serialize json to etree.

        :param data: transformed record to dict.
        :returns: an etree element.
        """
        ns = {
            'dc': 'http://purl.org/dc/elements/1.1/',
            'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
            'xml': 'xml',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        }
        container = '{http://www.openarchives.org/OAI/2.0/oai_dc/}dc'
        """Default container element."""
        attrib = {
            '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation':
            'http://www.openarchives.org/OAI/2.0/oai_dc/ '
            'http://www.openarchives.org/OAI/2.0/oai_dc.xsd'
        }
        """Default container element attributes."""
        elements = {
            'contributors': 'contributor',
            'creators': 'creator',
            'dates': 'date',
            'descriptions': 'description',
            'formats': 'format',
            'identifiers': 'identifier',
            'languages': 'language',
            'publishers': 'publisher',
            'relations': 'relation',
            'rights': 'rights',
            'sources': 'source',
            'subjects': 'subject',
            'titles': 'title',
            'types': 'type'
        }

        root = etree.Element(container, nsmap=ns, attrib=attrib)

        for key, values in data.items():
            if key in elements:
                for value in values:
                    attrs = {}
                    if isinstance(value, dict):
                        val = value['value']
                        if '@attrs' in value:
                            for attr in value['@attrs']:
                                prefix = attr['prefix'] \
                                    if 'prefix' in attr else 'xml'
                                attrs[f'{{{prefix}}}{attr["name"]}'] = \
                                    attr['value']
                    else:
                        val = value
                    field = etree.SubElement(
                        root,
                        f'{{http://purl.org/dc/elements/1.1/}}{elements[key]}',
                        attrs
                        )
                    field.text = sanitize_unicode(val)
        return root


def sonar_dublin_core(pid, record):
    """Get DublinCore XML for OAI-PMH."""
    return SonarDublinCoreXMLSerializer()\
        .serialize_object_xml(record)
