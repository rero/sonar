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

"""DOJSON transformation for SRU."""

import re

from dojson import utils

from sonar.modules.documents.dojson.overdo import Overdo

overdo = Overdo()

CONTRIBUTOR_ROLES_MAPPING = {
    'aut': 'cre',
    'cmp': 'cre',
    'pht': 'cre',
    'ape': 'cre',
    'aqt': 'cre',
    'arc': 'cre',
    'art': 'cre',
    'aus': 'cre',
    'chr': 'cre',
    'cll': 'cre',
    'com': 'cre',
    'drt': 'cre',
    'dsr': 'cre',
    'enj': 'cre',
    'fmk': 'cre',
    'inv': 'cre',
    'ive': 'cre',
    'ivr': 'cre',
    'lbt': 'cre',
    'lsa': 'cre',
    'lyr': 'cre',
    'pra': 'cre',
    'prg': 'cre',
    'rsp': 'cre',
    'scl': 'cre',
    'hnr': 'cre',
    'apl': 'cre',
    'cng': 'cre',
    'cou': 'cre',
    'csl': 'cre',
    'dfd': 'cre',
    'dgg': 'cre',
    'dte': 'cre',
    'fmd': 'cre',
    'fmp': 'cre',
    'his': 'cre',
    'jud': 'cre',
    'jug': 'cre',
    'med': 'cre',
    'orm': 'cre',
    'prn': 'cre',
    'pro': 'cre',
    'ptf': 'cre',
    'rcp': 'cre',
    'rpc': 'cre',
    'spn': 'cre',
    'tlp': 'cre',
    'cre': 'cre',
    'dub': 'cre',
    'mus': 'cre',
    'ctb': 'ctb',
    'ill': 'ctb',
    'prf': 'ctb',
    'trl': 'ctb',
    'abr': 'ctb',
    'act': 'ctb',
    'adi': 'ctb',
    'adp': 'ctb',
    'aft': 'ctb',
    'anm': 'ctb',
    'ann': 'ctb',
    'arr': 'ctb',
    'ato': 'ctb',
    'clr': 'ctb',
    'cnd': 'ctb',
    'ctg': 'ctb',
    'auc': 'ctb',
    'aui': 'ctb',
    'bkd': 'ctb',
    'bnd': 'ctb',
    'brd': 'ctb',
    'brl': 'ctb',
    'bsl': 'ctb',
    'cas': 'ctb',
    'clt': 'ctb',
    'cwt': 'ctb',
    'cmm': 'ctb',
    'cns': 'ctb',
    'col': 'ctb',
    'cor': 'ctb',
    'crt': 'ctb',
    'cst': 'ctb',
    'ctr': 'ctb',
    'cur': 'ctb',
    'dnc': 'ctb',
    'dnr': 'ctb',
    'dpt': 'ctb',
    'drm': 'ctb',
    'dst': 'ctb',
    'dto': 'ctb',
    'edm': 'ctb',
    'egr': 'ctb',
    'etr': 'ctb',
    'exp': 'ctb',
    'fac': 'ctb',
    'fds': 'ctb',
    'fmo': 'ctb',
    'hst': 'ctb',
    'ilu': 'ctb',
    'ins': 'ctb',
    'dgs': 'dgs',
    'edt': 'edt',
    'isb': 'edt',
    'pbd': 'edt',
    'mfr': 'prt',
    'prt': 'prt',
    'itr': 'ctb',
    'lgd': 'ctb',
    'ltg': 'ctb',
    'mod': 'ctb',
    'msd': 'ctb',
    'mtk': 'ctb',
    'nrt': 'ctb',
    'osp': 'ctb',
    'oth': 'ctb',
    'own': 'ctb',
    'pan': 'ctb',
    'pat': 'ctb',
    'pbl': 'ctb',
    'plt': 'ctb',
    'ppm': 'ctb',
    'ppt': 'ctb',
    'pre': 'ctb',
    'prm': 'ctb',
    'prs': 'ctb',
    'rcd': 'ctb',
    'rce': 'ctb',
    'rdd': 'ctb',
    'res': 'ctb',
    'rsr': 'ctb',
    'sds': 'ctb',
    'sgd': 'ctb',
    'sll': 'ctb',
    'sng': 'ctb',
    'spk': 'ctb',
    'srv': 'ctb',
    'stl': 'ctb',
    'tch': 'ctb',
    'tld': 'ctb',
    'trc': 'ctb',
    'vac': 'ctb',
    'vdg': 'ctb',
    'wac': 'ctb',
    'wal': 'ctb',
    'wat': 'ctb',
    'win': 'ctb',
    'wpr': 'ctb',
    'wst': 'ctb'
}


@overdo.over('identifiedBy', '001')
@utils.ignore_value
def marc21_to_identified_by_from_001(self, key, value):
    """Get identifier from field 001."""
    identified_by = self.get('identifiedBy', [])

    identified_by.append({
        'type': 'bf:Local',
        'source': 'swisscovery',
        'value': value
    })

    return identified_by


@overdo.over('identifiedBy', '^020..')
@utils.ignore_value
def marc21_to_identified_by_from_020(self, key, value):
    """Get identifier from field 020."""
    if not value.get('a'):
        return None

    identified_by = self.get('identifiedBy', [])
    identified_by.append({'type': 'bf:Isbn', 'value': value.get('a')})

    self['identifiedBy'] = identified_by

    return None


@overdo.over('identifiedBy', '^022..')
@utils.ignore_value
def marc21_to_identified_by_from_022(self, key, value):
    """Get identifier from field 022."""
    if not value.get('a') and not value.get('l'):
        return None

    identified_by = self.get('identifiedBy', [])

    if value.get('a'):
        identified_by.append({'type': 'bf:Issn', 'value': value.get('a')})

    if value.get('l'):
        identified_by.append({'type': 'bf:IssnL', 'value': value.get('l')})

    self['identifiedBy'] = identified_by

    return None


@overdo.over('identifiedBy', '^024..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_identified_by_from_024(self, key, value):
    """Get identifier from field 024."""
    if not value.get('a') or not value.get('2'):
        return None

    type = 'bf:Local'

    if value.get('2') == 'doi':
        type = 'bf:Doi'

    if value.get('2') == 'urn':
        type = 'bf:Urn'

    if value.get('2') == 'uri':
        type = 'uri'

    document_type = {'type': type, 'value': value.get('a')}

    if type == 'bf:Local':
        document_type['source'] = value.get('2')

    identified_by = self.get('identifiedBy', [])
    identified_by.append(document_type)

    self['identifiedBy'] = identified_by

    return None


@overdo.over('identifiedBy', '^027..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_identified_by_from_027(self, key, value):
    """Get identifier from field 027."""
    if not value.get('a'):
        return None

    identified_by = self.get('identifiedBy', [])
    identified_by.append({'type': 'bf:Strn', 'value': value.get('a')})

    self['identifiedBy'] = identified_by

    return None


@overdo.over('identifiedBy', '^088..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_identified_by_from_088(self, key, value):
    """Get identifier from field 088."""
    if not value.get('a'):
        return None

    identified_by = self.get('identifiedBy', [])
    identified_by.append({'type': 'bf:ReportNumber', 'value': value.get('a')})

    self['identifiedBy'] = identified_by

    return None


@overdo.over('language', '^008')
@utils.ignore_value
def marc21_to_language_and_provision_activity_from_008(self, key, value):
    """Get language from field 008."""
    # Language
    language = self.get('language', [])
    language.append({'type': 'bf:Language', 'value': value[-5:-2]})
    self['language'] = language

    # Provision activity
    provision_activity = self.get('provisionActivity', [])
    if not provision_activity:
        provision_activity.append({})

    provision_activity[0]['type'] = 'bf:Publication'
    provision_activity[0]['startDate'] = value[7:11]

    end_date = value[11:15]
    if re.match(r'^[0-9]{4}$', end_date):
        provision_activity[0]['endDate'] = end_date

    self['provisionActivity'] = provision_activity

    return None


@overdo.over('title', '^245..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_title_from_245(self, key, value):
    """Get title from field 245."""
    main_title = value.get('a')
    language = self['language'][0]['value'] if self.get('language') else 'eng'
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


@overdo.over('abstracts', '^520..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_abstracts_from_520(self, key, value):
    """Get abstracts from field 520."""
    if not value.get('a'):
        return None

    return {
        'value': value.get('a'),
        'language':
        self['language'][0]['value'] if self.get('language') else 'eng'
    }


@overdo.over('contentNote', '^505..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_content_note_from_505(self, key, value):
    """Get abstracts from field 505."""
    if not value.get('a'):
        return None

    return value['a']


@overdo.over('contribution', '^(100|700|710|711)..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_contribution_from_100_700(self, key, value):
    """Get contribution from field 100."""
    if not value.get('a'):
        return None

    is_100_or_700 = key.startswith('100') or key.startswith('700')

    separator = ' ' if is_100_or_700 else '. '

    name = value.get('a')
    if value.get('b'):
        name = name + separator + separator.join(utils.force_list(value['b']))

    contribution = self.get('contribution', [])

    type = 'bf:Person'

    if key == '710__':
        type = 'bf:Organization'

    if key == '711__':
        type = 'bf:Meeting'

    role = 'cre' if is_100_or_700 else 'ctb'
    if value.get('4'):
        for item in utils.force_list(value['4']):
            if item in CONTRIBUTOR_ROLES_MAPPING:
                role = CONTRIBUTOR_ROLES_MAPPING[item]

    data = {'agent': {'type': type, 'preferred_name': name}, 'role': [role]}

    if is_100_or_700 and value.get('d'):
        date_of_birth = date_of_death = None
        try:
            date_of_birth, date_of_death = overdo.extract_date(value['d'][:9])
        except Exception:
            pass

        if date_of_birth:
            data['agent']['date_of_birth'] = date_of_birth

        if date_of_death:
            data['agent']['date_of_death'] = date_of_death

    if key == '711__':
        if value.get('c'):
            data['agent']['place'] = value['c']

        if value.get('d'):
            data['agent']['date'] = value['d']

        if value.get('n'):
            data['agent']['number'] = value['n']

    contribution.append(data)

    self['contribution'] = contribution

    return None


@overdo.over('extent', '^300..')
@utils.ignore_value
def marc21_to_extent_from_300(self, key, value):
    """Get extent from field 300."""
    # Extent
    if value.get('a'):
        self['extent'] = value['a']

    # Other material characteristics
    if value.get('b'):
        self['otherMaterialCharacteristics'] = value['b']

    # Formats
    if value.get('c'):
        self['formats'] = [value['c']]

    # Additional materials
    if value.get('e'):
        self['additionalMaterials'] = value['e']

    return None


@overdo.over('dissertation', '^502..')
@utils.ignore_value
def marc21_to_dissertation_from_502(self, key, value):
    """Get dissertation from field 502."""
    if not value.get('a') and not value.get('b'):
        return None

    degree = []
    if value.get('a'):
        degree.append(value['a'])
    if value.get('b'):
        degree.append(value['b'])

    data = {'degree': '. '.join(degree)}

    if value.get('c'):
        data['grantingInstitution'] = value['c']

    if value.get('d'):
        try:
            data['date'] = overdo.extract_date(value['d'])[0]
        except Exception:
            pass

    return data


@overdo.over('editionStatement', '^250..')
@utils.ignore_value
def marc21_to_edition_statement_from_250(self, key, value):
    """Get edition statement from field 250."""
    if not value.get('a'):
        return None

    data = {'editionDesignation': {'value': value['a']}}

    if value.get('b'):
        data['responsibility'] = {'value': value['b']}

    return data


@overdo.over('documentType', 'leader')
@utils.ignore_value
def marc21_to_document_type_from_leader(self, key, value):
    """Get document type from leader."""

    def determine_type(field):
        """Determine type of document."""
        # Bachelor thesis
        if 'bachelor' in field.get(
                'a', '').lower() or 'bachelor' in field.get('b', '').lower():
            return 'coar:c_7a1f'

        # Master thesis
        if 'master' in field.get('a', '').lower() or 'master' in field.get(
                'b', '').lower():
            return 'coar:c_bdcc'

        # Doctoral thesis
        if 'dissertation' in field.get(
                'a', '').lower() or 'dissertation' in field.get(
                    'b', '').lower() or 'thèse' in field.get(
                        'a', '').lower() or 'thèse' in field.get('b', '')\
                            .lower():
            return 'coar:c_db06'


    leader_06 = value[6]

    # Still image
    if leader_06 == 'k':
        return 'coar:c_ecc8'

    # Musical notation
    if leader_06 in ['c', 'd']:
        return 'coar:c_18cw'

    # Cartographic material
    if leader_06 in ['e', 'f']:
        return 'coar:c_12cc'

    # Moving image
    if leader_06 == 'g':
        return 'coar:c_8a7e'

    # Soung
    if leader_06 in ['i', 'j']:
        return 'coar:c_18cc'

    # Dataset
    if leader_06 == 'm':
        return 'coar:c_ddb1'

    if leader_06 == 'a':
        leader_07 = value[7]

        # Contribution to journal
        if leader_07 == 'b':
            return 'coar:c_3e5a'

        # Book part
        if leader_07 == 'a':
            return 'coar:c_3248'

        # Periodical
        if leader_07 == 's':
            return 'coar:c_2659'

        field_502 = overdo.blob_record.get('502__')
        if field_502:
            if type(field_502) == tuple:
                for fld502 in field_502:
                    doctype = determine_type(fld502)
                    if doctype:
                        return doctype
            else:
                doctype = determine_type(field_502)
                if doctype:
                    return doctype
            # Thesis
            return 'coar:c_46ec'
        # Book
        if leader_07 == 'm':
            return 'coar:c_2f33'

    # Other
    return 'coar:c_1843'


@overdo.over('provisionActivity', '^264.1')
@utils.ignore_value
def marc21_to_provision_activity_from_264_1(self, key, value):
    """Get provision activity from field 264."""
    provision_activity = self.get('provisionActivity', [])
    if not provision_activity:
        provision_activity.append({'type': 'bf:Publication', 'statement': []})

    if not provision_activity[0].get('statement'):
        provision_activity[0]['statement'] = []

    for place in utils.force_list(value.get('a', [])):
        provision_activity[0]['statement'].append({
            'type': 'bf:Place',
            'label': {
                'value': place
            }
        })

    for agent in utils.force_list(value.get('b', [])):
        provision_activity[0]['statement'].append({
            'type': 'bf:Agent',
            'label': {
                'value': agent
            }
        })

    if value.get('c'):
        provision_activity[0]['statement'].append({
            'type': 'Date',
            'label': {
                'value': value['c']
            }
        })

    self['provisionActivity'] = provision_activity

    return None


@overdo.over('provisionActivity', '^264.(1|3)')
@utils.ignore_value
def marc21_to_provision_activity_from_264_3(self, key, value):
    """Get provision activity from field 264."""
    provision_activity = self.get('provisionActivity', [])

    manufacture = {'type': 'bf:Manufacture', 'statement': []}

    for place in utils.force_list(value.get('a', [])):
        manufacture['statement'].append({
            'type': 'bf:Place',
            'label': {
                'value': place
            }
        })

    for agent in utils.force_list(value.get('b', [])):
        manufacture['statement'].append({
            'type': 'bf:Agent',
            'label': {
                'value': agent
            }
        })

    if value.get('c'):
        manufacture['statement'].append({
            'type': 'Date',
            'label': {
                'value': value['c']
            }
        })

    provision_activity.append(manufacture)
    self['provisionActivity'] = provision_activity

    return None


@overdo.over('notes', '^(500|504|508|510|511|530|545|555)..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_notes(self, key, value):
    """Get notes from several fields."""
    if not value.get('a'):
        return None

    return value['a']


@overdo.over('series', '^490..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_series_from_490(self, key, value):
    """Get series from field 490."""
    if not value.get('a'):
        return None

    serie = {'name': value['a']}

    if value.get('v'):
        serie['number'] = value['v']

    return serie


@overdo.over('partOf773', '^773..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_partof_from_773(self, key, value):
    """Get partOf from field 773."""
    if not value.get('t'):
        return None

    part_of = self.get('partOf', [])

    data = {'document': {'title': value['t']}}

    # Contribution
    contributions = []
    for contribution in utils.force_list(value.get('a', [])):
        contributions.append(contribution)
    if contributions:
        data['document']['contribution'] = contributions

    # Identifiers
    identifiers = []
    if value.get('x'):
        identifiers.append({'type': 'bf:Issn', 'value': value['x']})
    if value.get('z'):
        identifiers.append({'type': 'bf:Isbn', 'value': value['z']})
    if identifiers:
        data['document']['identifiedBy'] = identifiers

    # Numbering
    for numbering in utils.force_list(value.get('g', [])):
        # Pages
        matches = re.match(r'^.*S\.\s([0-9\-]+).*$', numbering)
        if matches:
            data['numberingPages'] = matches.group(1)

        # Year
        matches = re.match(r'^yr:([0-9]{4})$', numbering)
        if matches:
            data['numberingYear'] = matches.group(1)
        matches = re.match(r'^.*\(([0-9]{4})\).*$', numbering)
        if matches:
            data['numberingYear'] = matches.group(1)

        # Volume
        matches = re.match(r'^.*Vol\.\s([0-9]+).*$', numbering, re.IGNORECASE)
        if matches:
            data['numberingVolume'] = matches.group(1)

        # Issue
        matches = re.match(r'^no:([0-9]+)$', numbering, re.IGNORECASE)
        if matches:
            data['numberingIssue'] = matches.group(1)
        matches = re.match(r'^.*No\s([0-9]+).*$', numbering, re.IGNORECASE)
        if matches:
            data['numberingIssue'] = matches.group(1)
        matches = re.match(r'^.*Nr\.\s([0-9]+).*$', numbering, re.IGNORECASE)
        if matches:
            data['numberingIssue'] = matches.group(1)

    part_of.append(data)
    self['partOf'] = part_of

    return None


@overdo.over('partOf800830', '^800|830..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_partof_from_800(self, key, value):
    """Get partOf from field 800."""
    # Title
    title = None
    if key.startswith('800'):
        title = value.get('t')
    else:
        title = []
        if value.get('a'):
            title.append(value['a'])

        if value.get('p'):
            title.append(value['p'])

        if title:
            title = '. '.join(title)

    if not title:
        return None

    part_of = self.get('partOf', [])

    data = {'document': {'title': title}}

    # Contribution
    if key.startswith('800'):
        contributions = []
        for contribution in utils.force_list(value.get('a', [])):
            contributions.append(contribution)
        if contributions:
            data['document']['contribution'] = contributions

    # Identifiers
    identifiers = []
    if value.get('x'):
        identifiers.append({'type': 'bf:Issn', 'value': value['x']})
    if value.get('z'):
        identifiers.append({'type': 'bf:Isbn', 'value': value['z']})
    if identifiers:
        data['document']['identifiedBy'] = identifiers

    # Numbering volume
    if value.get('v'):
        data['numberingVolume'] = value['v']

    part_of.append(data)
    self['partOf'] = part_of

    return None
