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

"""schema.org marshmallow schema."""

from __future__ import absolute_import, print_function, unicode_literals

from flask import request
from marshmallow import fields, post_dump

from .base_schema import BaseSchema

TYPE_MAPPING = {
    'coar:c_2f33': 'Book',
    'coar:c_3248': 'Chapter',
    'coar:c_c94f': 'CreativeWork',
    'coar:c_5794': 'ScholarlyArticle',
    'coar:c_18cp': 'ScholarlyArticle',
    'coar:c_6670': 'Poster',
    'coar:c_18co': 'Poster',
    'coar:c_f744': 'Book',
    'coar:c_ddb1': 'Dataset',
    'coar:c_3e5a': 'Article',
    'coar:c_beb9': 'ScholarlyArticle',
    'coar:c_6501': 'ScholarlyArticle',
    'coar:c_998f': 'NewsArticle',
    'coar:c_dcae04bc': 'ScholarlyArticle',
    'coar:c_8544': 'Course',
    'non_textual_object': 'MediaObject',
    'coar:c_8a7e': 'VideoObject',
    'coar:c_ecc8': 'ImageObject',
    'coar:c_12cc': 'Map',
    'coar:c_18cc': 'AudioObject',
    'coar:c_18cw': 'MusicComposition',
    'coar:c_5ce6': 'SoftwareApplication',
    'coar:c_15cd': 'CreativeWork',
    'coar:c_2659': 'Periodical',
    'coar:c_0640': 'Periodical',
    'coar:c_2cd9': 'Periodical',
    'coar:c_2fe3': 'Newspaper',
    'coar:c_816b': 'ScholarlyArticle',
    'coar:c_93fc': 'Report',
    'coar:c_18ww': 'Report',
    'coar:c_18wz': 'Report',
    'coar:c_18wq': 'Report',
    'coar:c_186u': 'Report',
    'coar:c_18op': 'Report',
    'coar:c_ba1f': 'Report',
    'coar:c_18hj': 'Report',
    'coar:c_18ws': 'Report',
    'coar:c_18gh': 'Report',
    'coar:c_46ec': 'Thesis',
    'coar:c_7a1f': 'Thesis',
    'coar:c_db06': 'Thesis',
    'coar:c_bdcc': 'Thesis',
    'habilitation_thesis': 'Thesis',
    'advanced_studies_thesis': 'Thesis',
    'other_thesis': 'Thesis',
    'coar:c_8042': 'CreativeWork',
    'coar:c_1843': 'CreativeWork',
    'coar:R60J-J5BD': 'CreativeWork',
    'coar:c_ba08': 'Review'
}


class SchemaOrgV1(BaseSchema):
    """Marshmallow schema for schema.org/ScholarlyArticle."""

    type_ = fields.Method('get_type', data_key='@type')
    context_ = fields.Constant('http://schema.org', data_key='@context')
    id_ = fields.Method('get_id', data_key='@id')
    name = fields.Method('get_title')
    abstract = fields.Method('get_abstract')
    description = fields.Method('get_abstract')
    inLanguage = fields.Method('get_in_language')
    creator = fields.Method('get_creator')
    headline = fields.Method('get_title')
    datePublished = fields.Method('get_start_date')
    url = fields.Method('get_file_urls')
    keywords = fields.Method('get_keywords')
    identifier = fields.Method('get_id')
    license = fields.Method('get_license')
    image = fields.Method('get_image')
    pagination = fields.Method('get_pages')
    pageStart = fields.Method('get_first_page')
    pageEnd = fields.Method('get_last_page')

    def get_type(self, obj):
        """Get type."""
        if obj['metadata'].get('documentType') and TYPE_MAPPING.get(
                obj['metadata']['documentType']):
            return TYPE_MAPPING[obj['metadata']['documentType']]

        return 'CreativeWork'

    def get_abstract(self, obj):
        """Get abstract."""
        for abstract in obj['metadata'].get('abstracts', []):
            return abstract['value']

        return None

    def get_in_language(self, obj):
        """Get inLanguage."""
        for language in obj['metadata'].get('language', []):
            return language['value']

        return None

    def get_creator(self, obj):
        """Get authors."""
        items = []
        for contributor in obj['metadata'].get('contribution', []):
            if contributor['role'][0] == 'cre' and contributor['agent'].get(
                    'preferred_name'):
                items.append({
                    '@type': 'Person',
                    'name': contributor['agent']['preferred_name']
                })

        return items

    def get_license(self, obj):
        """Get license."""
        if obj['metadata'].get('usageAndAccessPolicy'):
            result = [obj['metadata']['usageAndAccessPolicy']['license']]

            if obj['metadata']['usageAndAccessPolicy'].get('label'):
                result.append(obj['metadata']['usageAndAccessPolicy']['label'])

            return ', '.join(result)

        return None

    def get_image(self, obj):
        """Get image."""
        if obj['metadata'].get('mainFile', {}).get('thumbnail'):
            return '{host}{image}'.format(
                host=request.host_url.rstrip('/'),
                image=obj['metadata']['mainFile']['thumbnail'])

        return None

    def get_file_urls(self, obj):
        """Get file URLs."""
        files = []

        for file in obj['metadata'].get('_files', []):
            if file.get('type') == 'file' and file.get('links'):
                if file['links'].get('download'):
                    files.append('{host}{image}'.format(
                        host=request.host_url.rstrip('/'),
                        image=file['links']['download']))

                if file['links'].get('external'):
                    files.append(file['links']['external'])

        return files

    @post_dump
    def remove_empty_values(self, data, **kwargs):
        """Remove empty values before dumping data."""
        return {key: value for key, value in data.items() if value}
