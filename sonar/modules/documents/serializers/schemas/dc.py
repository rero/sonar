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

"""Dublin Core marshmallow schema."""

import re

from flask import current_app, request
from marshmallow import fields

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.views import part_of_format

from .base_schema import BaseSchema


class DublinCoreSchema(BaseSchema):
    """Schema for records v1 in JSON."""

    contributors = fields.Method('get_contributors')
    creators = fields.Method('get_creators')
    dates = fields.Method('get_dates')
    descriptions = fields.Method('get_descriptions')
    formats = fields.Method('get_formats')
    identifiers = fields.Method('get_identifiers')
    languages = fields.Method('get_languages')
    publishers = fields.Method('get_publishers')
    relations = fields.Method('get_relations')
    rights = fields.Method('get_rights')
    sources = fields.Method('get_sources')
    subjects = fields.Method('get_subjects')
    titles = fields.Method('get_titles')
    types = fields.Method('get_types')

    def translate_language(self, language):
        """Translate language code ISO-639-3 to ISO-639-2 if possible.

        :param language: language with ISO-639-3 format.
        :returns: language code ISO-639-2 if possible or ISO-639-3.
        """
        langs = current_app.config['SONAR_APP_LANGUAGES_MAP']
        if language in langs and langs[language]:
            return langs[language]
        return language

    def get_contributors(self, obj):
        """Get contributors."""
        items = []
        for contributor in obj['metadata'].get('contribution', []):
            if contributor['role'][0] != 'cre' and contributor['agent'].get(
                    'preferred_name'):
                items.append(self.format_contributor(contributor))

        return items

    def get_creators(self, obj):
        """Get creators."""
        items = []
        for contributor in obj['metadata'].get('contribution', []):
            if contributor['role'][0] == 'cre' and contributor['agent'].get(
                    'preferred_name'):
                items.append(self.format_contributor(contributor))

        return items

    def get_dates(self, obj):
        """Get dates."""
        items = []

        for provision_activity in obj['metadata'].get('provisionActivity', []):
            if provision_activity[
                    'type'] == 'bf:Publication' and provision_activity.get(
                        'startDate'):
                items.append(provision_activity['startDate'])

        if obj['metadata'].get('mainFile') and obj['metadata']['mainFile'][
                'restriction']['date']:
            items.append('info:eu-repo/date/embargoEnd/{date}'.format(
                date=obj['metadata']['mainFile']['embargo_date']))

        return items

    def get_descriptions(self, obj):
        """Get descriptions."""
        items = []
        for abstract in obj['metadata'].get('abstracts', []):
            if 'language' in abstract:
                items.append({
                '@attrs': [{
                    'prefix':'xml',
                    'name':'lang',
                    'value': self.translate_language(abstract['language'])
                }],
                'value':abstract['value']
            })
            else:
                items.append(abstract['value'])

        return items

    def get_formats(self, obj):
        """Get formats."""
        main_file = obj['metadata'].get('mainFile')

        if main_file and main_file.get('mimetype'):
            return [main_file['mimetype']]

        return []

    def get_identifiers(self, obj):
        """Get identifiers."""
        items = [
            DocumentRecord.get_permanent_link(request.host_url,
                                              obj['metadata']['pid'])
        ]
        # If files on the document
        if '_files' in obj['metadata']:
            # Extraction of files only with a type file
            files = filter(
                lambda f: ('type' in f and f['type'] == 'file'),
                obj['metadata']['_files'])
            # Files sorting
            files = sorted(files, key=lambda file: file.get('order', 100))
            # Remove / at the end of host_url
            host = request.host_url[:-1]
            # Add file only the the link is defined in download
            for file in files:
                links = file.get('links', {})
                if 'download' in links and links.get('download'):
                    items.append(host + links.get('download'))

        return items

    def get_languages(self, obj):
        """Get languages."""
        return [
            language['value']
            for language in obj['metadata'].get('language', [])
        ]

    def get_publishers(self, obj):
        """Get publishers."""
        if not obj['metadata'].get('provisionActivity'):
            return []

        items = []

        for provision_activity in obj['metadata']['provisionActivity']:
            if provision_activity[
                    'type'] == 'bf:Publication' and provision_activity.get(
                        'statement'):
                for statement in provision_activity['statement']:
                    if statement['type'] == 'bf:Agent':
                        items.append(statement['label'][0]['value'])

        return items

    def get_relations(self, obj):
        """Get relations."""
        items = [
            other_edition['document']['electronicLocator']
            for other_edition in obj['metadata'].get('otherEdition', [])
        ] + [
            other_edition['document']['electronicLocator']
            for other_edition in obj['metadata'].get('relatedTo', [])
        ]

        result = 'info:eu-repo/semantics/altIdentifier/{schema}/{identifier}'

        # Identifiers
        for identifier in obj['metadata'].get('identifiedBy', []):
            # ARK
            matches = re.match(r'^ark\:\/(.*)$', identifier['value'])
            if matches:
                items.append(
                    result.format(schema='ark', identifier=matches.group(1)))

            # DOI
            matches = re.match(r'^(10\..*)$', identifier['value'])
            if identifier['type'] == 'bf:Doi' and matches:
                items.append(
                    result.format(schema='doi', identifier=matches.group(1)))

            # ISBN
            if identifier['type'] == 'bf:Isbn':
                items.append(
                    result.format(schema='isbn',
                                  identifier=identifier['value']))

            # ISSN
            if identifier['type'] == 'bf:Issn':
                items.append(
                    result.format(schema='issn',
                                  identifier=identifier['value']))

            # PMID
            if identifier['type'] == 'bf:Local' and identifier.get(
                    'source'
            ) and identifier['source'].lower().find('pmid') != -1:
                items.append(
                    result.format(schema='pmid',
                                  identifier=identifier['value']))

            # URN
            if identifier['type'] == 'bf:Urn':
                items.append(
                    result.format(schema='urn',
                                  identifier=identifier['value']))

        return items

    def get_rights(self, obj):
        """Get rights."""
        items = []

        # Main file
        result = 'info:eu-repo/semantics/{access}'

        main_file = obj['metadata'].get('mainFile')
        if main_file:
            if main_file['restriction']['restricted']:
                # Embargo
                if main_file['restriction']['date']:
                    items.append(result.format(access='embargoedAccess'))
                # Restricted
                else:
                    items.append(result.format(access='restrictedAccess'))
            # No restriction
            else:
                items.append(result.format(access='openAccess'))

        # Usage en access policy
        if obj['metadata'].get('usageAndAccessPolicy'):
            result = [obj['metadata']['usageAndAccessPolicy']['license']]

            if obj['metadata']['usageAndAccessPolicy'].get('label'):
                result.append(obj['metadata']['usageAndAccessPolicy']['label'])

            items.append(', '.join(result))

        return items

    def get_sources(self, obj):
        """Get sources."""
        return [
            part_of_format(part_of)
            for part_of in obj['metadata'].get('partOf', [])
        ]

    def get_subjects(self, obj):
        """Get subjects."""
        items = []

        # Subjects
        for subjects in obj['metadata'].get('subjects', []):
            if 'language' in subjects['label']:
                for value in subjects['label']['value']:
                    items.append({
                        '@attrs': [{
                            'prefix': 'xml',
                            'name': 'lang',
                            'value': self.translate_language(
                                subjects['label']['language'])
                        }],
                        'value': value
                    })
            else:
                items = items + subjects['label']['value']

        # Classification
        for classification in obj['metadata'].get('classification', []):
            classification_type = 'udc'

            if classification['type'] == 'bf:ClassificationDdc':
                classification_type = 'ddc'

            items.append(
                'info:eu-repo/classification/{type}/{classification}'.format(
                    type=classification_type,
                    classification=classification['classificationPortion']))

        return items

    def get_titles(self, obj):
        """Get titles."""
        title = {
            '@attrs': [{
                'prefix': 'xml',
                'name': 'lang',
                'value': self.translate_language(
                    obj['metadata']['title'][0]['mainTitle'][0]['language'])
            }],
            'value': obj['metadata']['title'][0]['mainTitle'][0]['value']\
                .strip()
        }
        if obj['metadata']['title'][0].get('subtitle'):
            subtitle = obj['metadata']['title'][0]['subtitle'][0]['value']\
                .strip()
            title['value'] = f"{title['value']} : {subtitle}"

        return [title]

    def get_types(self, obj):
        """Get types."""
        if obj['metadata'].get('documentType', ''):
            types = obj['metadata'].get('documentType', '').split(':')
            if len(types) == 1:
                return [f'{types[0]}']
            if len(types) == 2:
                return [f'http://purl.org/coar/resource_type/{types[1]}']

        return []

    def format_contributor(self, contributor):
        """Format contributor item.

        :param contributor: Contributor dict.
        :returns: Formatted string representing the contributor.
        """
        data = contributor['agent']['preferred_name']

        info = []
        if contributor['agent'].get('number'):
            info.append(contributor['agent']['number'])

        if contributor['agent'].get('date'):
            info.append(contributor['agent']['date'])

        if contributor['agent'].get('place'):
            info.append(contributor['agent']['place'])

        if info:
            data += ' ({info})'.format(info=' : '.join(info))

        return data
