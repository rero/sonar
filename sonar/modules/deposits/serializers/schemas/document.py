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

"""Document serializer."""

from marshmallow import Schema, fields, post_dump, pre_dump


class RemoveEmptyValuesMixin():
    """Mixin for removing empty values from schema."""

    @post_dump
    def remove_empty_values(self, data, **kwargs):
        """Remove empty values before dumping data."""
        return {key: value for key, value in data.items() if value}


class DocumentMetadataSchema(Schema, RemoveEmptyValuesMixin):
    """Serialize deposit metadata."""

    title = fields.Method('get_title')
    subtitle = fields.Method('get_subtitle')
    identifiedBy = fields.List(fields.Dict())
    language = fields.Method('get_language')
    abstracts = fields.Method('get_abstracts')
    documentType = fields.Str()
    contentNote = fields.List(fields.Str())
    extent = fields.Str()
    dissertation = fields.Dict()
    additionalMaterials = fields.Str()
    formats = fields.List(fields.Str())
    otherMaterialCharacteristics = fields.Str()
    editionStatement = fields.Dict()
    documentDate = fields.Method('get_date')
    statementDate = fields.Method('get_statement_date')
    publicationPlace = fields.Method('get_publication_place')
    publisher = fields.Method('get_publisher')
    notes = fields.List(fields.Str())
    series = fields.List(fields.Dict())
    publication = fields.Method('get_publication')

    def get_title(self, obj):
        """Get title."""
        if not obj.get('title'):
            return None

        return obj['title'][0]['mainTitle'][0]['value']

    def get_subtitle(self, obj):
        """Get subttitle."""
        if not obj.get('title') or not obj['title'][0].get('subtitle'):
            return None

        return obj['title'][0]['subtitle'][0]['value']

    def get_language(self, obj):
        """Get language."""
        if not obj.get('language'):
            return None

        return obj['language'][0]['value']

    def get_abstracts(self, obj):
        """Get abstracts."""
        if not obj.get('abstracts'):
            return None

        return [{
            'language': item['language'],
            'abstract': item['value']
        } for item in obj['abstracts']]

    def get_date(self, obj):
        """Get date."""
        for provision_activity in obj.get('provisionActivity', []):
            if provision_activity.get('startDate'):
                return provision_activity['startDate']

        return None

    def get_statement_date(self, obj):
        """Get statement date."""
        for provision_activity in obj.get('provisionActivity', []):
            for statement in provision_activity.get('statement', []):
                if statement['type'] == 'Date':
                    return statement['label']['value']

        return None

    def get_publication_place(self, obj):
        """Get publication place."""
        for provision_activity in obj.get('provisionActivity', []):
            for statement in provision_activity.get('statement', []):
                if statement['type'] == 'bf:Place':
                    return statement['label']['value']

        return None

    def get_publisher(self, obj):
        """Get publisher."""
        for provision_activity in obj.get('provisionActivity', []):
            for statement in provision_activity.get('statement', []):
                if statement['type'] == 'bf:Agent':
                    return statement['label']['value']

        return None

    def get_publication(self, obj):
        """Get publication."""
        for part_of in obj.get('partOf', []):
            data = {
                'publishedIn': part_of['document']['title']
            }

            if part_of.get('numberingYear'):
                data['year'] = part_of['numberingYear']

            if part_of.get('numberingVolume'):
                data['volume'] = part_of['numberingVolume']

            if part_of.get('numberingIssue'):
                data['number'] = part_of['numberingIssue']

            if part_of.get('numberingPages'):
                data['pages'] = part_of['numberingPages']

            if part_of.get('document', {}).get('contribution'):
                data['editors'] = part_of['document']['contribution']

            if part_of.get('document', {}).get('identifiedBy'):
                data['identifiedBy'] = part_of['document']['identifiedBy']

            return data

        return None



class DocumentSchema(Schema, RemoveEmptyValuesMixin):
    """Serialize deposit from document schema."""

    metadata = fields.Nested(DocumentMetadataSchema)
    contributors = fields.Method('get_contributors')

    @pre_dump
    def init_data(self, item, **kwargs):
        """Initialize data before processing."""
        contribution = item.pop('contribution', None)
        item = {'metadata': item, 'contribution': contribution}
        return item

    def get_contributors(self, obj):
        """Get contributors."""
        if not obj.get('contribution'):
            return None

        contributors = []
        for item in obj['contribution']:
            contributor = {
                'name': item['agent']['preferred_name'],
                'role': item['role'][0]
            }
            if 'date_of_birth' in item['agent']:
                contributor['date_of_birth'] = item['agent']['date_of_birth']
            if 'date_of_death' in item['agent']:
                contributor['date_of_death'] = item['agent']['date_of_death']
            contributors.append(contributor)

        return contributors

