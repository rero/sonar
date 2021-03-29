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

"""Dublin core schema."""

import re

import xmltodict
from marshmallow import Schema, fields, post_dump, pre_dump

from sonar.modules.pdf_extractor.utils import force_list

TYPE_MAPPINGS = {
    'Book': 'coar:c_2f33',
    'Book Section': 'coar:c_3248',
    'Conference': 'coar:c_c94f',
    'Workshop Item': 'coar:c_c94f',
    'Research Data': 'coar:c_ddb1',
    'Article': 'coar:c_6501',
    'Newspaper': 'coar:c_998f',
    'Magazine Article': 'coar:c_998f',
    'Audiovisual Material & Event': 'non_textual_object',
    'Preprint': 'coar:c_816b',
    'Thesis': 'coar:c_db06',
    'Working Paper': 'coar:c_8042',
    'Other': 'coar:c_1843'
}


class DublinCoreSchema(Schema):
    """Dublin Core marshmallow schema."""

    identifiedBy = fields.Method('get_identifiers')
    language = fields.Method('get_language')
    title = fields.Method('get_title')
    provisionActivity = fields.Method('get_provision_activity')
    documentType = fields.Method('get_document_type')
    abstracts = fields.Method('get_abstracts')
    subjects = fields.Method('get_subjects')
    contribution = fields.Method('get_contribution')

    def dump(self, obj):
        """Serialize an object to native Python data types.

        :param obj: The object to serialize.
        :returns: Serialized data
        """
        result = xmltodict.parse(obj)

        if not result.get('record', {}).get('metadata', {}).get('oai_dc:dc'):
            return None

        record = result['record']['metadata']['oai_dc:dc']
        record['id'] = result['record']['header']['identifier']

        return super().dump(record)

    @pre_dump
    def store_language(self, item, **kwargs):
        """Store language."""
        item['languages'] = []

        for language in force_list(item.get('dc:language', [])):
            if language == 'deu':
                language = 'ger'

            if language == 'fra':
                language = 'fre'

            item['languages'].append(language)

        if not item['languages']:
            item['languages'] = ['eng']

        return item

    @post_dump
    def remove_empty_values(self, data, **kwargs):
        """Remove empty values before dumping data."""
        return {key: value for key, value in data.items() if value}

    def get_identifiers(self, obj):
        """Get identifiers."""
        identifiers = [{
            'type': 'bf:Local',
            'source': 'edoc',
            'value': obj['id']
        }]

        if not obj.get('dc:identifier'):
            return identifiers

        for identifier in force_list(obj['dc:identifier']):
            # DOI
            match = re.search(r'^info:doi\/(.+)$', identifier)
            if match:
                identifiers.append({'type': 'bf:Doi', 'value': match.group(1)})
                continue

            # PMID
            match = re.search(r'^info:pmid\/(.+)$', identifier)
            if match:
                identifiers.append({
                    'type': 'bf:Local',
                    'value': match.group(1),
                    'source': 'PMID'
                })
                continue

            # URN
            match = re.search(r'^urn:(.+)$', identifier)
            if match:
                identifiers.append({'type': 'bf:Urn', 'value': match.group(1)})
                continue

            # Other identifier
            identifiers.append({'type': 'bf:Identifier', 'value': identifier})

        return identifiers

    def get_language(self, obj):
        """Get language."""
        return [{
            'type': 'bf:Language',
            'value': item
        } for item in obj['languages']]

    def get_title(self, obj):
        """Get title."""
        title = 'Default title'
        subtitle = None

        if obj.get('dc:title'):
            # Title + subtitle
            match = re.search(r'^(.+)\s:\s(.+)$', obj['dc:title'])
            if match:
                title = match.group(1)
                subtitle = match.group(2)
            else:
                title = obj.get('dc:title')

        title = {
            'type': 'bf:Title',
            'mainTitle': [{
                'value': title,
                'language': obj['languages'][0]
            }]
        }

        if subtitle:
            title['subtitle'] = [{
                'value': subtitle,
                'language': obj['languages'][0]
            }]

        return [title]

    def get_provision_activity(self, obj):
        """Get provisition activity."""
        if not obj.get('dc:date'):
            return None

        match = re.search(r'^[0-9]{4}$', obj['dc:date'])

        if not match:
            return None

        return [{'type': 'bf:Publication', 'startDate': obj['dc:date']}]

    def get_document_type(self, obj):
        """Get document type."""
        for type in force_list(obj.get('dc:type', [])):
            if TYPE_MAPPINGS.get(type):
                return TYPE_MAPPINGS[type]

        return TYPE_MAPPINGS['Other']

    def get_abstracts(self, obj):
        """Get abstracts."""
        if not obj.get('dc:description'):
            return None

        return [{
            'language': obj['languages'][0],
            'value': obj['dc:description']
        }]

    def get_subjects(self, obj):
        """Get subjects."""
        if not obj.get('dc:subject'):
            return []

        subjects = []

        for subject in force_list(obj.get('dc:subject', [])):
            subjects.append(subject)

        return [{
            'label': {
                'language': obj['languages'][0],
                'value': subjects
            }
        }]

    def get_contribution(self, obj):
        """Get contribution."""
        contributors = []

        for creator in force_list(obj.get('dc:creator', [])):
            contributors.append({
                'agent': {
                    'type': 'bf:Person',
                    'preferred_name': creator
                },
                'role': ['cre']
            })

        for contributor in force_list(obj.get('dc:contributor', [])):
            contributors.append({
                'agent': {
                    'type': 'bf:Person',
                    'preferred_name': contributor
                },
                'role': ['ctb']
            })

        return contributors
