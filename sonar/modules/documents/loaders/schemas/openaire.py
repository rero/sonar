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

"""Openaire schema."""

import xmltodict
from marshmallow import Schema, fields, pre_dump

from sonar.modules.pdf_extractor.utils import force_list


class OpenaireSchema(Schema):
    """Openaire marshmallow schema."""

    identifiedBy = fields.Method('get_identifiers')
    title = fields.Method('get_title')

    @pre_dump
    def parse_xml(self, data, **kwargs):
        """Parse xml data and convert into OrderedDict.

        :param data: XML string.
        :returns: OrderedDict.
        """
        result = xmltodict.parse(data)

        if not result.get('record', {}).get('metadata', {}).get('resource'):
            return {}

        return result['record']['metadata']['resource']

    def get_identifiers(self, obj):
        """Create identifiers."""
        identifiers = []

        # Main identifier
        if obj.get('datacite:identifier'):
            identifiers.append({
                'type': 'bf:Local',
                'source': 'BORIS',
                'value': obj['datacite:identifier']['#text']
            })

        # DOI
        if obj.get('datacite:alternateIdentifiers'):
            for identifier in force_list(obj['datacite:alternateIdentifiers']
                                         ['datacite:alternateIdentifier']):
                if identifier['@identifierType'] == 'DOI':
                    identifiers.append({
                        'type': 'bf:Doi',
                        'value': identifier['#text']
                    })

        # PMID
        if obj.get('datacite:relatedIdentifiers'):
            for identifier in force_list(obj['datacite:relatedIdentifiers']
                                         ['datacite:relatedIdentifier']):
                if identifier['@relationType'] == 'IsVersionOf' and identifier[
                        '@relatedIdentifierType'] == 'PMID':
                    identifiers.append({
                        'type': 'bf:Local',
                        'source': 'PMID',
                        'value': identifier['#text']
                    })

        return identifiers

    def get_title(self, obj):
        """Get title."""
        titles = []

        for title in force_list(
                obj.get('datacite:titles', {}).get('datacite:title', [])):
            titles.append({
                'type':
                'bf:Title',
                'mainTitle': [{
                    'value': title['#text'],
                    'language': title.get('@xml:lang', 'eng')
                }]
            })

        return titles
