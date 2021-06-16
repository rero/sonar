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

"""RERODOC MARC21 model definition."""

import hashlib
import re

from dojson import utils
from flask import current_app
from invenio_db import db

from sonar.modules.collections.api import Record as CollectionRecord
from sonar.modules.documents.dojson.rerodoc.overdo import Overdo
from sonar.modules.organisations.api import OrganisationRecord
from sonar.modules.subdivisions.api import Record as SubdivisionRecord
from sonar.modules.utils import remove_trailing_punctuation

overdo = Overdo()

TYPE_MAPPINGS = {
    'PREPRINT|': 'coar:c_816b',
    'POSTPRINT|ART_JOURNAL': 'coar:c_6501',
    'POSTPRINT|ART_INBOOK': 'coar:c_3248',
    'POSTPRINT|ART_INPROC': 'coar:c_5794',
    'BOOK|': 'coar:c_2f33',
    'DISSERTATION|DISS_MASTER': 'coar:c_bdcc',
    'DISSERTATION|DISS_BACHELOR': 'coar:c_7a1f',
    'DISSERTATION|DISS_CONT_EDU': 'coar:c_46ec',
    'THESIS|': 'coar:c_db06',
    'THESIS|TH_PHD': 'coar:c_db06',
    'THESIS|TH_HABILIT': 'coar:c_46ec',
    'MAP|': 'coar:c_12cc',
    'REPORT|': 'coar:c_18ws',
    'NEWSPAPER|': 'coar:c_2fe3',
    'JOURNAL|': 'coar:c_0640',
    'PRINT_MEDIA|': 'coar:c_2fe3',
    'AUDIO|': 'coar:c_18cc',
    'IMAGE|': 'coar:c_ecc8',
    'PARTITION|': 'coar:c_18cw'
}


@overdo.over('type', '^980')
@utils.ignore_value
def marc21_to_type_and_organisation(self, key, value):
    """Get document type and organisation from 980 field."""
    # organisation
    if value.get('b'):
        organisation = value.get('b').lower()

        # Specific transformation for `unisi`, because the real acronym is
        # `usi`.
        if organisation == 'unisi':
            organisation = 'usi'

        # Specific transformation for `bpuge` and `mhnge`, because the real
        # acronym is `vge`.
        subdivision_name = None

        if organisation in [
                'bpuge', 'mhnge', 'baage', 'bmuge', 'imvge', 'mhsge'
        ]:
            subdivision_name = 'bge' if organisation == 'bpuge' else organisation
            organisation = 'vge'

        if organisation not in overdo.registererd_organisations:
            overdo.create_organisation(organisation)
            overdo.registererd_organisations.append(organisation)

        self['organisation'] = [{
            '$ref':
            OrganisationRecord.get_ref_link('organisations', organisation)
        }]

        if subdivision_name:
            # Store subdivision
            hash_key = hashlib.md5(
                (subdivision_name + organisation).encode()).hexdigest()

            subdivision_pid = SubdivisionRecord.get_pid_by_hash_key(hash_key)

            # No subdivision found
            if not subdivision_pid:
                subdivision = SubdivisionRecord.create({
                    'name': [{
                        'language': 'eng',
                        'value': subdivision_name
                    }],
                    'organisation': {
                        '$ref':
                        OrganisationRecord.get_ref_link(
                            'organisations', organisation)
                    },
                    'hashKey':
                    hash_key
                })
                subdivision.commit()
                subdivision.reindex()
                db.session.commit()
                subdivision_pid = subdivision['pid']

            self['subdivisions'] = [{
                '$ref':
                SubdivisionRecord.get_ref_link('subdivisions', subdivision_pid)
            }]

    # get doc type by mapping
    key = value.get('a', '') + '|' + value.get('f', '')
    if key not in TYPE_MAPPINGS:
        current_app.logger.warning(
            'Document type not found in mapping for type "{type}"'.format(
                type=key))
        return None

    # Store types to records
    self['documentType'] = TYPE_MAPPINGS[key]

    return None


@overdo.over('language', '^041')
@utils.for_each_value
@utils.ignore_value
def marc21_to_language(self, key, value):
    """Get languages."""
    if not value.get('a'):
        return None

    language = self.get('language', [])

    codes = utils.force_list(value.get('a'))

    for code in codes:
        language.append({'type': 'bf:Language', 'value': code})

    self['language'] = language

    return None


@overdo.over('title', '^245..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_title_245(self, key, value):
    """Get title."""
    main_title = value.get('a')
    language = value.get('9', 'eng')
    subtitle = value.get('b')

    if not main_title:
        return None

    title = {
        'type': 'bf:Title',
        'mainTitle': [{
            'value': main_title.rstrip(':'),
            'language': language
        }]
    }

    if subtitle:
        title['subtitle'] = [{'value': subtitle, 'language': language}]

    return title


@overdo.over('title', '^246..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_title_246(self, key, value):
    """Get title."""
    main_title = value.get('a')
    language = value.get('9', 'eng')

    if not main_title:
        return None

    title = self.get('title', [{'type': 'bf:Title', 'mainTitle': []}])

    # Add title 246 to last title in mainTitle propert
    title[-1]['mainTitle'].append({'value': main_title, 'language': language})

    self['title'] = title

    return None


@overdo.over('editionStatement', '^250..')
@utils.ignore_value
def marc21_to_edition_statement(self, key, value):
    """Get edition statement data."""
    if not value.get('a') or not value.get('b'):
        return None

    return {
        'editionDesignation': {
            'value': value.get('a')
        },
        'responsibility': {
            'value': value.get('b')
        },
    }


@overdo.over('provisionActivity', '^260..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_provision_activity_field_260(self, key, value):
    """Get provision activity data from field 260."""
    provision_activity = self.get('provisionActivity', [])

    # Only if there is a date
    if value.get('c'):
        publication = {'type': 'bf:Publication', 'statement': []}

        # Place
        if value.get('a'):
            publication['statement'].append({
                'type':
                'bf:Place',
                'label': [{
                    'value': value.get('a')
                }]
            })

        # Agent
        if value.get('b'):
            publication['statement'].append({
                'type':
                'bf:Agent',
                'label': [{
                    'value': remove_trailing_punctuation(value.get('b'))
                }]
            })

        years = value.get('c').split('-')

        # Start date
        if years and re.match(r'^\d{4}$', years[0]):
            publication['startDate'] = years[0]

            publication['statement'].append({
                'type':
                'Date',
                'label': [{
                    'value': value.get('c')
                }]
            })

        # End date
        if len(years) > 1 and re.match(r'^\d{4}$', years[1]):
            publication['endDate'] = years[1]

        provision_activity.append(publication)

    # Manufacture
    if value.get('e') or value.get('f'):
        manufacture = {'type': 'bf:Manufacture', 'statement': []}

        if value.get('e'):
            manufacture['statement'].append({
                'type':
                'bf:Place',
                'label': [{
                    'value': remove_trailing_punctuation(value.get('e'))
                }]
            })

        if value.get('f'):
            manufacture['statement'].append({
                'type':
                'bf:Agent',
                'label': [{
                    'value': value.get('f')
                }]
            })

        provision_activity.append(manufacture)

    # Re-assign provision activity
    if provision_activity:
        self['provisionActivity'] = provision_activity

    return None


@overdo.over('provisionActivity', '^269..')
@utils.ignore_value
def marc21_to_provision_activity_field_269(self, key, value):
    """Get provision activity data from field 269."""
    # 260$c has priority to this date
    if overdo.blob_record.get('260__', {}).get('c'):
        return None

    # No date, skipping
    if not value.get('c'):
        return None

    # Assign start date
    match = re.search(r'^[0-9]{4}(-[0-9]{2}-[0-9]{2})?$', value.get('c'))

    # Date does not match "YYYY" or "YYYY-MM-DD"
    if not match:
        return None

    add_provision_activity_start_date(self, value.get('c'))

    return None


@overdo.over('formats', '^300..')
@utils.ignore_value
def marc21_to_description(self, key, value):
    """Get extent, otherMaterialCharacteristics, formats.

    extent: 300$a (the first one if many)
    otherMaterialCharacteristics: 300$b (the first one if many)
    formats: 300 [$c repetitive]
    """
    if value.get('a'):
        if not self.get('extent'):
            self['extent'] = remove_trailing_punctuation(
                overdo.not_repetitive(value, 'a'))

    if value.get('b'):
        if self.get('otherMaterialCharacteristics', []) == []:
            self['otherMaterialCharacteristics'] = remove_trailing_punctuation(
                overdo.not_repetitive(value, 'b'))

    if value.get('c'):
        formats = self.get('formats')

        if not formats:
            data = value.get('c')
            formats = list(utils.force_list(data))

        return formats

    return None


@overdo.over('series', '^490..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_series(self, key, value):
    """Get series.

    series.name: [490$a repetitive]
    series.number: [490$v repetitive]
    """
    series = {}

    name = value.get('a')
    if name:
        series['name'] = ', '.join(utils.force_list(name))

    number = value.get('v')
    if number:
        series['number'] = ', '.join(utils.force_list(number))

    return series


@overdo.over('abstracts', '^520..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_abstract(self, key, value):
    """Get abstract."""
    abstract = value.get('a')
    language = value.get('9', 'eng')

    if not abstract:
        return None

    if language == 'fr':
        language = 'fre'

    abstracts_data = self.get('abstracts', [])
    abstracts_data.append({'value': abstract, 'language': language})

    self['abstracts'] = abstracts_data

    return None


@overdo.over('identifiedBy', '001')
@utils.ignore_value
def marc21_to_identified_by_from_001(self, key, value):
    """Get identifier from field 001."""
    identified_by = self.get('identifiedBy', [])

    identified_by.append({
        'type': 'bf:Local',
        'source': 'RERO DOC',
        'value': value
    })

    return identified_by


@overdo.over('identifiedBy', '^020..')
@utils.ignore_value
def marc21_to_identified_by_from_020(self, key, value):
    """Get identifier from field 020."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a'):
        return None

    identified_by.append({'type': 'bf:Isbn', 'value': value.get('a')})

    return identified_by


@overdo.over('identifiedBy', '^0247.')
@utils.ignore_value
def marc21_to_identified_by_from_024(self, key, value):
    """Get identifier from field 024."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a') or value.get('2') != 'urn':
        return None

    identified_by.append({'type': 'bf:Urn', 'value': value.get('a')})

    return identified_by


@overdo.over('identifiedBy', '^027..')
@utils.ignore_value
def marc21_to_identified_by_from_027(self, key, value):
    """Get identifier from field 027."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a'):
        return None

    identified_by.append({'type': 'bf:Strn', 'value': value.get('a')})

    return identified_by


@overdo.over('identifiedBy', '^035..')
@utils.ignore_value
def marc21_to_identified_by_from_035(self, key, value):
    """Get identifier from field 035."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a'):
        return None

    identified_by.append({
        'type': 'bf:Local',
        'source': 'RERO',
        'value': value.get('a')
    })

    return identified_by


@overdo.over('identifiedBy', '^037..')
@utils.ignore_value
def marc21_to_identified_by_from_037(self, key, value):
    """Get identifier from field 037."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a'):
        return None

    identified_by.append({
        'type':
        'bf:Local',
        'source':
        'Swissbib',
        'value':
        value.get('a').replace('swissbib.ch:', '').strip()
    })

    return identified_by


@overdo.over('identifiedBy', '^088..')
@utils.ignore_value
def marc21_to_identified_by_from_088(self, key, value):
    """Get identifier from field 088."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a'):
        return None

    identified_by.append({'type': 'bf:ReportNumber', 'value': value.get('a')})

    return identified_by


@overdo.over('identifiedBy', '^091..')
@utils.ignore_value
def marc21_to_identified_by_from_091(self, key, value):
    """Get identifier from field 091."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a') or value.get('b') != 'pmid':
        return None

    identified_by.append({
        'type': 'bf:Local',
        'value': value.get('a'),
        'source': 'PMID'
    })

    return identified_by


@overdo.over('notes', '^500..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_notes(self, key, value):
    """Get  notes."""
    return overdo.not_repetitive(value, 'a')


@overdo.over('subjects', '^600..|695..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_subjects(self, key, value):
    """Get subjects."""
    if not value.get('a'):
        return None

    subject_values = []

    for item in value.get('a').split(' ; '):
        if item:
            subject_values.append(item)

    subjects = {'label': {'value': subject_values}}

    # If field is 695 and no language is available
    if key == '695__':
        if not value.get('9'):
            return None

        subjects['label']['language'] = value.get('9')

    # If field is 600 and no source is available
    if key == '600__':
        if not value.get('2'):
            return None

        subjects['source'] = value.get('2')

    return subjects


@overdo.over('files', '^856..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_files(self, key, value):
    """Get files."""
    key = value.get('f')
    url = value.get('u')
    mime_type = value.get('q', 'text/plain')

    if not key or not url:
        return None

    # TODO: Check why this type of file exists. Real example with rerodoc ID
    # 29085
    if mime_type == 'pdt/download':
        current_app.logger.warning(
            'File {file} for record {record} has a strange pdt/download mime '
            'type, skipping import of file...'.format(
                file=key, record=self['identifiedBy']))
        return None

    url = url.strip()

    # Retreive file order
    # If order not set we put a value to 99 for easily point theses files
    order = 99
    if value.get('y'):
        match = re.search(r'order:([0-9]+)$', value.get('y'))
        if match:
            order = int(match.group(1))

    data = {
        'key': key,
        'url': url,
        'label': value.get('z', key),
        'type': 'file',
        'order': order
    }

    return data


@overdo.over('otherEdition', '^775..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_other_edition(self, key, value):
    """Get other edition."""
    electronic_locator = value.get('o')
    public_note = value.get('g')

    if not electronic_locator or not public_note:
        return None

    return {
        'document': {
            'electronicLocator': electronic_locator
        },
        'publicNote': public_note
    }


@overdo.over('collections', '^982..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_specific_collection(self, key, value):
    """Extract collection for record."""
    if not value.get('a'):
        return None

    # No organisation found, the collection is not imported.
    if not self.get('organisation'):
        return None

    organisation_pid = OrganisationRecord.get_pid_by_ref_link(
        self['organisation'][0]['$ref'])

    hash_key = hashlib.md5(
        (value.get('a') + organisation_pid).encode()).hexdigest()

    collection_pid = CollectionRecord.get_pid_by_hash_key(hash_key)

    # No collection found
    if not collection_pid:
        collection = CollectionRecord.create({
            'name': [{
                'language': 'eng',
                'value': value.get('a')
            }],
            'organisation': {
                '$ref': self['organisation'][0]['$ref']
            },
            'hashKey':
            hash_key
        })
        collection.commit()
        collection.reindex()
        db.session.commit()
        collection_pid = collection['pid']

    return {
        '$ref': CollectionRecord.get_ref_link('collections', collection_pid)
    }


@overdo.over('classification', '^080..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_classification_field_080(self, key, value):
    """Get classification data from field 080."""
    if not value.get('a'):
        return None

    return {
        'type': 'bf:ClassificationUdc',
        'classificationPortion': value.get('a')
    }


@overdo.over('classification', '^084..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_classification_field_084(self, key, value):
    """Get classification data from field 084."""
    if not value.get('a') or value.get('2') != 'ddc':
        return None

    return {
        'type': 'bf:ClassificationDdc',
        'classificationPortion': value.get('a')
    }


@overdo.over('contentNote', '^505..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_content_note(self, key, value):
    """Extract collection for record."""
    return value.get('a')


@overdo.over('dissertation', '^502..')
@utils.ignore_value
def marc21_to_dissertation_field_502(self, key, value):
    """Extract dissertation degree."""
    if value.get('a'):
        dissertation = self.get('dissertation', {})
        dissertation['degree'] = value.get('a')
        self['dissertation'] = dissertation

    # Try to get start date and store in provision activity
    # 260$c and 269$c have priority to this date
    record = overdo.blob_record
    if (record.get('260__', {}).get('c') or record.get('269__', {}).get('c') or
            record.get('773__', {}).get('g')):
        return None

    # No date, skipping
    if not value.get('9'):
        return None

    # Match either 2019 or 2019-01-01
    match = re.search(r'^[0-9]{4}(-[0-9]{2}-[0-9]{2})?$', value.get('9'))

    if not match:
        return None

    add_provision_activity_start_date(self, value.get('9'))

    return None


@overdo.over('dissertation', '^508..')
@utils.ignore_value
def marc21_to_dissertation_field_508(self, key, value):
    """Extract dissertation note."""
    if not value.get('a'):
        return None

    dissertation = self.get('dissertation', {})
    dissertation['jury_note'] = value.get('a')

    self['dissertation'] = dissertation

    return None


@overdo.over('usageAndAccessPolicy', '^540..')
@utils.ignore_value
def marc21_to_usage_and_access_policy(self, key, value):
    """Extract usage and access policy."""
    if not value.get('a'):
        return None

    return {'label': value.get('a'), 'license': 'License undefined'}


@overdo.over('contribution', '^100..')
@utils.ignore_value
def marc21_to_contribution_field_100(self, key, value):
    """Extract contribution from field 100."""
    if not value.get('a'):
        return None

    contribution = self.get('contribution', [])

    data = {
        'agent': {
            'type': 'bf:Person',
            'preferred_name': value.get('a')
        },
        'role': ['cre']
    }

    # Affiliation
    if value.get('u'):
        data['affiliation'] = value.get('u')

    # Date of birth - date of death
    date_of_birth, date_of_death = overdo.extract_date(value.get('d'))

    if date_of_birth:
        data['agent']['date_of_birth'] = date_of_birth

    if date_of_death:
        data['agent']['date_of_death'] = date_of_death

    contribution.append(data)
    self['contribution'] = contribution

    return None


@overdo.over('contribution', '^700..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_contribution_field_700(self, key, value):
    """Extract contribution from field 100."""
    if not value.get('a'):
        return None

    contribution = self.get('contribution', [])

    role = overdo.get_contributor_role(value.get('e'))

    if not role:
        raise Exception('No role found for contributor {contribution}'.format(
            contribution=value))

    data = {
        'agent': {
            'type': 'bf:Person',
            'preferred_name': value.get('a')
        },
        'role': [role]
    }

    # Affiliation
    if value.get('u'):
        data['affiliation'] = value.get('u')

    # Date of birth - date of death
    date_of_birth, date_of_death = overdo.extract_date(value.get('d'))

    if date_of_birth:
        data['agent']['date_of_birth'] = date_of_birth

    if date_of_death:
        data['agent']['date_of_death'] = date_of_death

    contribution.append(data)
    self['contribution'] = contribution

    return None


@overdo.over('contribution', '^710..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_contribution_field_710(self, key, value):
    """Extract contribution from field 710."""
    if not value.get('a'):
        return None

    contribution = self.get('contribution', [])
    contribution.append({
        'agent': {
            'type': 'bf:Organization',
            'preferred_name': value.get('a')
        },
        'role': ['ctb']
    })
    self['contribution'] = contribution

    return None


@overdo.over('contribution', '^711..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_contribution_field_711(self, key, value):
    """Extract contribution from field 711."""
    if not value.get('a'):
        return None

    contribution = self.get('contribution', [])

    data = {
        'agent': {
            'type': 'bf:Meeting',
            'preferred_name': value.get('a')
        },
        'role': ['cre']
    }

    # Place
    if value.get('c'):
        data['agent']['place'] = value.get('c')

    # Date
    if value.get('d'):
        data['agent']['date'] = value.get('d')

    # Number
    if value.get('n'):
        data['agent']['number'] = value.get('n')

    contribution.append(data)
    self['contribution'] = contribution

    return None


@overdo.over('partOf', '^773..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_part_of(self, key, value):
    """Extract related document for record."""
    if not value.get('g'):
        return None

    # Split value for getting numbering values
    numbering = value.get('g').split('/')

    # Numbering year
    if not numbering[0]:
        return None

    data = {'numberingYear': numbering[0]}

    # Volume
    if len(numbering) > 1 and numbering[1]:
        data['numberingVolume'] = numbering[1]

    # Issue
    if len(numbering) > 2 and numbering[2]:
        data['numberingIssue'] = numbering[2]

    # Pages
    if len(numbering) > 3 and numbering[3] and numbering[3] != '-':
        data['numberingPages'] = numbering[3]

    document = {}

    # Title is found
    if value.get('t'):
        document['title'] = value.get('t')

    # Contribution
    if value.get('c'):
        contributors = []
        for contributor in value.get('c').split(';'):
            if contributor:
                contributors.append(contributor)

        if contributors:
            document['contribution'] = contributors

    record = overdo.blob_record

    # Publication based on document sub type
    sub_type = record.get('980__', {}).get('f')
    if value.get('d') or sub_type == 'ART_INBOOK':
        document['publication'] = {}

        if value.get('d'):
            document['publication']['statement'] = value.get('d')

        if sub_type == 'ART_INBOOK':
            document['publication']['startDate'] = numbering[0]

    # If no field 260$c or 269$c, store start date
    if (not record.get('260__', {}).get('c') and
            not record.get('269__', {}).get('c')):
        add_provision_activity_start_date(self, numbering[0])

    if document:
        data['document'] = document

    return data


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
