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

"""DOJSON transformation for ArODES."""

import re

from dojson import utils

from sonar.modules.documents.dojson.overdo import Overdo

overdo = Overdo()

TYPE_MAPPINGS = {
    'livre': 'coar:c_2f33',
    'chapitre': 'coar:c_3248',
    'conference': 'coar:c_5794',
    'scientifique': 'coar:c_6501',
    'professionnel': 'coar:c_3e5a',
    'rapport': 'coar:c_18ws',
    'THESES': 'coar:c_db06',
    'other': 'coar:c_1843'
}

OA_STATUS = ['green', 'gold', 'hybrid', 'bronze', 'closed']


@overdo.over('identifiedBy', '001')
@utils.ignore_value
def identified_by_from_001(self, key, value):
    """Get identifier from field 001."""
    identified_by = self.get('identifiedBy', [])

    identified_by.append({
        'type': 'bf:Local',
        'source': 'ArODES',
        'value': value
    })

    return identified_by


@overdo.over('identifiedBy', '^0247.')
@utils.ignore_value
def identified_by_from_024(self, key, value):
    """Get identifier from field 024."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a') or not value.get('2') in ['DOI', 'PMID']:
        return None

    if value.get('2') == 'DOI':
        identified_by.append({'type': 'bf:Doi', 'value': value.get('a')})

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


@overdo.over('documentType', '^980')
@utils.ignore_value
def document_type_from_980(self, key, value):
    """Get document type from 980 field."""
    document_type = value.get('a', None)

    if self.get('documentType') or not document_type:
        return None

    if document_type not in TYPE_MAPPINGS:
        document_type = 'other'

    return TYPE_MAPPINGS[document_type]


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


@overdo.over('oa_status', '^906..')
@utils.ignore_value
def oa_status_from_906(self, key, value):
    """Get abstract."""
    oa_status = value.get('a', 'none').lower()

    if not oa_status or oa_status not in OA_STATUS:
        return None

    return oa_status


@overdo.over('date', '^269..')
@utils.ignore_value
def date_from_269(self, key, value):
    """Get date from field 269."""
    # No date, skipping
    if not value.get('a'):
        return None

    # Assign start date
    match = re.search(r'^[0-9]{4}-[0-9]{2}$', value.get('a'))

    # Date does not match "YYYY" or "YYYY-MM-DD"
    if not match:
        return None

    add_provision_activity_start_date(self, value.get('a') + '-01')

    return None


@overdo.over('date', '^260..')
@utils.ignore_value
def date_from_260(self, key, value):
    """Get date from field 260."""
    # No date, skipping
    if not value.get('c'):
        return None

    # Assign start date
    match = re.search(r'^[0-9]{4}-[0-9]{2}$', value.get('c'))

    # Date does not match "YYYY" or "YYYY-MM-DD"
    if not match:
        return None

    add_provision_activity_start_date(self, value.get('c') + '-01')

    return None


@overdo.over('subjects', '^653..')
@utils.for_each_value
@utils.ignore_value
def subjects_from_653(self, key, value):
    """Get abstract."""
    subject = value.get('a')
    language = value.get('9', 'eng')

    if not subject:
        return None

    subject_data = get_subject_for_language(self, language)
    subject_data['label']['value'].append(subject)

    return None


@overdo.over('dissertation', '^502..')
@utils.ignore_value
def dissertation_from_field_502(self, key, value):
    """Extract dissertation degree."""
    if not value.get('b'):
        return None

    return {'degree': value.get('b')}


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
        match = re.search(r'^(\d{4})', value.get('g'))
        if match:
            part_of['numberingYear'] = match.group(1)

        # Volume
        match = re.search(r'vol\.\s(\d+)', value.get('g'))
        if match:
            part_of['numberingVolume'] = match.group(1)

        # Issue
        match = re.search(r'no\.\s(\d+)', value.get('g'))
        if match:
            part_of['numberingIssue'] = match.group(1)

        # Pages
        match = re.search(r'pp\.\s([0-9\-–]+)', value.get('g'))
        if match:
            part_of['numberingPages'] = match.group(1)

    if not part_of.get('numberingYear'):
        return None

    return [part_of]


@overdo.over('contribution', '^700..')
@utils.for_each_value
@utils.ignore_value
def contribution_from_700(self, key, value):
    """Get contribution."""
    name = value.get('a')
    affiliation = value.get('u')

    if not name:
        return None

    contribution = {
        'agent': {
            'type': 'bf:Person',
            'preferred_name': name
        },
        'role': ['ctb']
    }

    if affiliation:
        contribution['affiliation'] = affiliation

    return contribution


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


def get_subject_for_language(data, language):
    """Return the subject item corresponding to language.

    :param dict data: Overdo data
    :param str language: Language code
    :returns: Subject object
    :rtype: Dict
    """
    if not data.get('subjects'):
        data['subjects'] = []

    subjects = [
        subject for subject in data.get('subjects', [])
        if subject['label']['language'] == language
    ]

    # Create an empty subject
    if not subjects:
        subject = {'label': {'language': language, 'value': []}}
        data['subjects'].append(subject)
        return subject

    return subjects[0]
