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

from flask import request
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
        return [file['value'] for file in obj['metadata'].get('abstracts', [])]

    def get_formats(self, obj):
        """Get formats."""
        main_file = obj['metadata'].get('mainFile')

        if main_file and main_file.get('mimetype'):
            return [main_file['mimetype']]

        return []

    def get_identifiers(self, obj):
        """Get identifiers."""
        return [
            DocumentRecord.get_permanent_link(request.host_url,
                                              obj['metadata']['pid'])
        ]

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
        title = [obj['metadata']['title'][0]['mainTitle'][0]['value']]

        if obj['metadata']['title'][0].get('subtitle'):
            title.append(obj['metadata']['title'][0]['subtitle'][0]['value'])

        return [' : '.join(title)]

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
