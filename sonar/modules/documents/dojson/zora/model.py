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

"""DOJSON transformation for ZORA."""

import re

from dojson import utils

from sonar.modules.documents.dojson.overdo import Overdo

overdo = Overdo()


@overdo.over('identifiedBy', '001')
@utils.ignore_value
def identified_by_from_001(self, key, value):
    """Get identifier from field 001."""
    identified_by = self.get('identifiedBy', [])

    identified_by.append({
        'type': 'bf:Local',
        'source': 'ZORA',
        'value': value
    })

    return identified_by


@overdo.over('identifiedBy', '^0247.')
@utils.ignore_value
def identified_by_from_024(self, key, value):
    """Get identifier from field 024."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a'):
        return None

    if value.get('2') == 'doi':
        identified_by.append({'type': 'bf:Doi', 'value': value.get('a')})
    elif value.get('2') == 'pmid':
        identified_by.append({
            'type': 'bf:Local',
            'value': value.get('a'),
            'source': 'PMID'
        })
    else:
        identified_by.append({
            'type': 'bf:Identifier',
            'value': value.get('a')
        })

    return identified_by


@overdo.over('title', '^245..')
@utils.for_each_value
@utils.ignore_value
def title_from_245(self, key, value):
    """Get title from field 245."""
    main_title = value.get('a', 'No title found')
    subtitle = value.get('b')
    language = value.get('9', 'eng')

    title = {
        'type': 'bf:Title',
        'mainTitle': [{
            'value': main_title,
            'language': language
        }]
    }

    if subtitle:
        title['subtitle'] = [{'value': subtitle, 'language': language}]

    return title


@overdo.over('documentType', '^655')
@utils.ignore_value
def document_type_from_655(self, key, value):
    """Get document type from 655 field."""
    type = value.get('2')
    value = value.get('a')

    if self.get('documentType') or not value or not type:
        return None

    record = overdo.blob_record

    # Book
    if type == 'local' and value == 'Herausgegebenes wissenschaftliches Werk':
        return 'coar:c_2f33'

    if type == 'local' and value == 'Monografie':
        return 'coar:c_2f33'

    # Book part
    if type == 'local' and value == 'Buchkapitel':
        return 'coar:c_3248'

    # Conference paper
    if type == 'local' and value == 'Konferenzbeitrag':
        return 'coar:c_5794'

    # Journal article
    if type == 'local' and value == 'Artikel':
        return 'coar:c_6501'

    # Newspaper article
    if type == 'local' and value == 'Zeitungsartikel':
        return 'coar:c_998f'

    # Research report
    if type == 'gnd-content' and value == 'Forschungsbericht':
        return 'coar:c_18ws'

    # Doctoral thesis
    if type == 'gnd-content' and value == 'Hochschulschrift' and record.get(
            '502__', {}).get('b') == 'Dissertation':
        return 'coar:c_db06'

    # Master thesis
    if type == 'gnd-content' and value == 'Hochschulschrift' and record.get(
            '502__', {}).get('b') == 'Masterarbeit':
        return 'coar:c_bdcc'

    # Habilitation thesis
    if type == 'gnd-content' and value == 'Hochschulschrift' and record.get(
            '502__', {}).get('b') == 'Habilitation':
        return 'habilitation_thesis'

    # Working paper
    if type == 'local' and value == 'Working Paper':
        return 'coar:c_8042'

    return 'coar:c_1843'


@overdo.over('language', '^041')
@utils.for_each_value
@utils.ignore_value
def language_from_041(self, key, value):
    """Get languages."""
    if not value.get('a'):
        return None

    language = self.get('language', [])

    codes = utils.force_list(value.get('a'))

    for code in codes:
        language.append({'type': 'bf:Language', 'value': code})

    self['language'] = language

    return None


@overdo.over('abstracts', '^520..')
@utils.for_each_value
@utils.ignore_value
def abstract_from_520(self, key, value):
    """Get abstract."""
    abstract = value.get('a')
    language = value.get('9', 'eng')

    if not abstract:
        return None

    abstracts_data = self.get('abstracts', [])
    abstracts_data.append({'value': abstract, 'language': language})

    self['abstracts'] = abstracts_data

    return None


@overdo.over('date', '^264..')
@utils.ignore_value
def date_from_264(self, key, value):
    """Get date from field 264."""
    # No date, skipping
    if not value.get('c'):
        return None

    # Assign start date
    match = re.search(r'^[0-9]{4}$', value.get('c'))

    # Date does not match "YYYY" or "YYYY-MM-DD"
    if not match:
        return None

    add_provision_activity_start_date(self, value.get('c'))

    return None


@overdo.over('dissertation', '^502..')
@utils.ignore_value
def dissertation_from_field_502(self, key, value):
    """Extract dissertation degree."""
    if not value.get('b'):
        return None

    dissertation = {'degree': value.get('b')}

    if value.get('c'):
        dissertation['grantingInstitution'] = value.get('c')

    if value.get('d'):
        dissertation['date'] = value.get('d')

    return dissertation


@overdo.over('partOf', '^773..')
@utils.ignore_value
def host_document_from_field_773(self, key, value):
    """Host document."""
    if not value.get('t'):
        return None

    part_of = {'document': {'title': value.get('t')}}

    if not value.get('g'):
        if self.get('provisionActivity'):
            match = re.search(r'^(\d{4})',
                              self['provisionActivity'][0]['startDate'])
            part_of['numberingYear'] = match.group(1)
    else:
        # Year
        match = re.search(r'\((\d{4})\)$', value.get('g'))
        if match:
            part_of['numberingYear'] = match.group(1)

        # Volume
        match = re.search(r'Bd\.\s(\d+)', value.get('g'))
        if match:
            part_of['numberingVolume'] = match.group(1)

        # Issue
        match = re.search(r'Nr\.\s(\d+)', value.get('g'))
        if match:
            part_of['numberingIssue'] = match.group(1)

        # Pages
        match = re.search(r'S\.\s(.+)\s\(', value.get('g'))
        if match:
            part_of['numberingPages'] = match.group(1)

    if not part_of.get('numberingYear'):
        return None

    return [part_of]


@overdo.over('contribution', '^[17]00..')
@utils.ignore_value
def contribution_from_field_100_700(self, key, value):
    """Extract contribution from field 100 or 700."""
    if not value.get('a'):
        return None

    contribution = self.get('contribution', [])

    data = {
        'agent': {
            'type': 'bf:Person',
            'preferred_name': value.get('a')
        },
        'role': ['cre' if value.get('4') == 'aut' else value.get('4')]
    }

    if value.get('0'):
        match = re.search(r'^\(orcid\)(.*)$', value.get('0'))
        if match:
            data['agent']['identifiedBy'] = {
                'type': 'bf:Local',
                'source': 'ORCID',
                'value': match.group(1)
            }

    contribution.append(data)
    self['contribution'] = contribution

    return None


def add_provision_activity_start_date(data, date):
    """Add start date for provision activity.

    :param data: Data dictionary.
    :param date: Date to add.
    """
    provisition_activity = data.get('provisionActivity', [])

    def get_publication():
        """Get stored publication."""
        for key, item in enumerate(provisition_activity):
            if item['type'] == 'bf:Publication':
                return provisition_activity.pop(key)

        return {'type': 'bf:Publication', 'startDate': None}

    publication = get_publication()

    publication['startDate'] = date

    # Inject publiction into provision activity
    provisition_activity.append(publication)

    # Re-assign provisionActivity
    data['provisionActivity'] = provisition_activity
