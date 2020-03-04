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

"""SONAR MARC21 model definition."""

import os
import re

import requests
from dojson import utils
from flask import current_app

from sonar.modules.documents.dojson.utils import SonarMarc21Overdo, \
    error_print, get_field_items, get_field_link_data, get_year_from_date, \
    not_repetitive, remove_trailing_punctuation
from sonar.modules.institutions.api import InstitutionRecord

marc21tojson = SonarMarc21Overdo()


def get_language_script(script):
    """Build the language script code.

    This code is built according to the format
    <lang_code>-<script_code> for example: chi-hani;
    the <lang_code> is retrived from field 008 and 041
    the <script_code> is received as parameter
    """
    languages_scripts = {
        'arab': ('ara', 'per'),
        'cyrl': ('bel', 'chu', 'mac', 'rus', 'srp', 'ukr'),
        'grek': ('grc', 'gre'),
        'hani': ('chi', 'jpn'),
        'hebr': ('heb', 'lad', 'yid'),
        'jpan': ('jpn', ),
        'kore': ('kor', ),
        'zyyy': ('chi', )
    }

    if script in languages_scripts:
        languages = ([marc21tojson.lang_from_008] +
                     marc21tojson.langs_from_041_a +
                     marc21tojson.langs_from_041_h)
        for lang in languages:
            if lang in languages_scripts[script]:
                return '-'.join([lang, script])
        error_print('WARNING LANGUAGE SCRIPTS:', marc21tojson.bib_id, script,
                    '008:', marc21tojson.lang_from_008, '041$a:',
                    marc21tojson.langs_from_041_a, '041$h:',
                    marc21tojson.langs_from_041_h)
    return '-'.join(['und', script])


def get_person_link(bibid, id, key, value):
    """Get MEF person link."""
    # https://mef.test.rero.ch/api/mef/?q=rero.rero_pid:A012327677
    prod_host = 'mef.rero.ch'
    test_host = 'mef.test.rero.ch'
    mef_url = 'https://{host}/api/mef/'.format(host=test_host)
    if os.environ.get('RERO_ILS_MEF_URL'):
        mef_url = os.environ.get('RERO_ILS_MEF_URL')
    mef_link = None
    try:
        identifier = id[1:].split(')')
        url = "{mef}/?q={org}.pid:{pid}".format(mef=mef_url,
                                                org=identifier[0].lower(),
                                                pid=identifier[1])
        request = requests.get(url=url)
        if request.status_code == requests.codes.ok:
            data = request.json()
            hits = data.get('hits', {}).get('hits')
            if hits:
                mef_link = hits[0].get('links').get('self')
                mef_link = mef_link.replace(test_host, prod_host)
        else:
            error_print('ERROR MEF REQUEST:', bibid, url, request.status_code)
    except Exception:
        error_print('WARNING NOT MEF REF:', bibid, id, key, value)
    return mef_link


@marc21tojson.over('type', '^980')
@utils.ignore_value
def marc21_to_type_and_institution(self, key, value):
    """Get document type and institution from 980 field."""
    institution = value.get('b')
    document_type = value.get('a')

    if institution:
        institution = institution.lower()

        if institution not in marc21tojson.registererd_organizations:
            marc21tojson.create_institution(institution)
            marc21tojson.registererd_organizations.append(institution)

        self['institution'] = {
            '$ref': InstitutionRecord.get_ref_link('institutions', institution)
        }

    if document_type:
        self['type'] = document_type.lower()

    return None


@marc21tojson.over('language', '^041')
@utils.ignore_value
def marc21_to_language(self, key, value):
    """Get languages.

    languages: 008 and 041 [$a, repetitive]
    """
    language = self.get('language', [])
    if marc21tojson.lang_from_008 and marc21tojson.lang_from_008 not in \
            marc21tojson.unique_languages:
        language.append({
            'value': marc21tojson.lang_from_008,
            'type': 'bf:Language'
        })
        marc21tojson.unique_languages.append(marc21tojson.lang_from_008)
    for lang_value in marc21tojson.langs_from_041_a:
        if lang_value not in marc21tojson.unique_languages:
            language.append({
                'value': lang_value.strip(),
                'type': 'bf:Language'
            })
            marc21tojson.unique_languages.append(lang_value)
    # if not language:
    #     error_print('ERROR LANGUAGE:', marc21tojson.bib_id, 'set to "und"')
    #     language = [{'value': 'und', 'type': 'bf:Language'}]

    return language or None


@marc21tojson.over('title', '^245..')
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
            'value': main_title,
            'language': language
        }]
    }

    if subtitle:
        title['subtitle'] = [{'value': subtitle, 'language': language}]

    return title


@marc21tojson.over('title', '^246..')
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


@marc21tojson.over('authors', '[17][01]0..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_author(self, key, value):
    """Get author.

    authors: loop:
    authors.name: 100$a [+ 100$b if it exists] or
        [700$a (+$b if it exists) repetitive] or
        [ 710$a repetitive (+$b if it exists, repetitive)]
    authors.date: 100 $d or 700 $d (facultatif)
    authors.qualifier: 100 $c or 700 $c (facultatif)
    authors.type: if 100 or 700 then person, if 710 then organisation
    """
    if not key[4] == '2':
        author = {}
        author['type'] = 'person'
        if value.get('0'):
            refs = utils.force_list(value.get('0'))
            for ref in refs:
                ref = get_person_link(marc21tojson.bib_id, ref, key, value)
                if ref:
                    author['$ref'] = ref
        # we do not have a $ref
        if not author.get('$ref'):
            author['name'] = ''
            if value.get('a'):
                data = not_repetitive(marc21tojson.bib_id, key, value, 'a')
                author['name'] = remove_trailing_punctuation(data)
            author_subs = utils.force_list(value.get('b'))
            if author_subs:
                for author_sub in author_subs:
                    author['name'] += ' ' + \
                        remove_trailing_punctuation(author_sub)
            if key[:3] == '710':
                author['type'] = 'organisation'
            else:
                if value.get('c'):
                    data = not_repetitive(marc21tojson.bib_id, key, value, 'c')
                    author['qualifier'] = remove_trailing_punctuation(data)
                if value.get('d'):
                    data = not_repetitive(marc21tojson.bib_id, key, value, 'd')
                    author['date'] = remove_trailing_punctuation(data)
        return author
    else:
        return None


@marc21tojson.over('copyrightDate', '^264.4')
@utils.ignore_value
def marc21_to_copyright_date(self, key, value):
    """Get Copyright Date."""
    copyright_dates = self.get('copyrightDate', [])
    copyrights_date = utils.force_list(value.get('c'))
    if copyrights_date:
        for copyright_date in copyrights_date:
            match = re.search(r'^([©℗])+\s*(\d{4}.*)', copyright_date)
            if match:
                copyright_date = ' '.join((match.group(1), match.group(2)))
                copyright_dates.append(copyright_date)
            # else:
            #     raise ValueError('Bad format of copyright date')
    return copyright_dates or None


@marc21tojson.over('editionStatement', '^250..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_edition_statement(self, key, value):
    """Get edition statement data.

    editionDesignation: 250 [$a non repetitive] (without trailing /)
    responsibility: 250 [$b non repetitive]
    """
    key_per_code = {'a': 'editionDesignation', 'b': 'responsibility'}

    def build_edition_data(code, label, index, link):
        data = [{'value': remove_trailing_punctuation(label)}]
        try:
            alt_gr = marc21tojson.alternate_graphic['250'][link]
            subfield = \
                marc21tojson.get_subfields(alt_gr['field'])[index]
            data.append({
                'value': remove_trailing_punctuation(subfield),
                'language': get_language_script(alt_gr['script'])
            })
        except Exception as err:
            pass
        return data

    tag_link, link = get_field_link_data(value)
    items = get_field_items(value)
    index = 1
    edition_data = {}
    subfield_selection = {'a', 'b'}
    for blob_key, blob_value in items:
        if blob_key in subfield_selection:
            subfield_selection.remove(blob_key)
            edition_data[key_per_code[blob_key]] = \
                build_edition_data(blob_key, blob_value, index, link)
        if blob_key != '__order__':
            index += 1
    return edition_data or None


@marc21tojson.over('provisionActivity', '^(260..|264.[ 0-3])')
@utils.for_each_value
@utils.ignore_value
def marc21_to_provision_activity(self, key, value):
    """Get publisher data.

    publisher.name: 264 [$b repetitive] (without the , but keep the ;)
    publisher.place: 264 [$a repetitive] (without the : but keep the ;)
    publicationDate: 264 [$c repetitive] (but take only the first one)
    """

    def build_statement(field_value, ind2):
        def build_agent_data(code, label, index, link):
            type_per_code = {'a': 'bf:Place', 'b': 'bf:Agent'}
            agent_data = {
                'type': type_per_code[code],
                'label': [{
                    'value': remove_trailing_punctuation(label)
                }]
            }
            try:
                alt_gr = marc21tojson.alternate_graphic['264'][link]
                subfield = \
                    marc21tojson.get_subfields(alt_gr['field'])[index]
                agent_data['label'].append({
                    'value':
                    remove_trailing_punctuation(subfield),
                    'language':
                    get_language_script(alt_gr['script'])
                })
            except Exception:
                pass
            return agent_data

        # function build_statement start here
        tag_link, link = get_field_link_data(field_value)
        items = get_field_items(field_value)
        statement = []
        index = 1
        for blob_key, blob_value in items:
            if blob_key in ('a', 'b'):
                agent_data = build_agent_data(blob_key, blob_value, index,
                                              link)
                statement.append(agent_data)
            if blob_key != '__order__':
                index += 1
        return statement

    def build_place():
        place = {}
        if marc21tojson.cantons:
            place['canton'] = marc21tojson.cantons[0]
        if marc21tojson.country:
            place['country'] = marc21tojson.country
        if place:
            place['type'] = 'bf:Place'
        return place

    # the function marc21_to_provisionActivity start here
    ind2 = key[4]
    type_per_ind2 = {
        ' ': 'bf:Publication',
        '0': 'bf:Production',
        '1': 'bf:Publication',
        '2': 'bf:Distribution',
        '3': 'bf:Manufacture'
    }
    if key[:3] == '260':
        ind2 = '1'
    publication = {
        'type': type_per_ind2[ind2],
        'statement': [],
    }

    subfields_c = utils.force_list(value.get('c'))
    if ind2 in (' ', '1'):
        start_date = get_year_from_date(marc21tojson.date1_from_008)
        if start_date:
            publication['startDate'] = start_date
        end_date = get_year_from_date(marc21tojson.date2_from_008)
        if end_date:
            publication['endDate'] = end_date
        if (marc21tojson.date_type_from_008 == 'q' or
                marc21tojson.date_type_from_008 == 'n'):
            publication['note'] = 'Date(s) incertaine(s) ou inconnue(s)'
        place = build_place()
        if place:
            publication['place'] = [place]
    publication['statement'] = build_statement(value, ind2)
    if subfields_c:
        subfield_c = subfields_c[0]
        date = {'label': [{'value': subfield_c}], 'type': 'Date'}

        tag_link, link = get_field_link_data(value)
        try:
            alt_gr = marc21tojson.alternate_graphic['264'][link]
            subfield = \
                marc21tojson.get_subfields(alt_gr['field'], code='c')
            date['label'].append({
                'value':
                subfield[0],
                'language':
                get_language_script(alt_gr['script'])
            })
        except Exception:
            pass

        publication['statement'].append(date)
    return publication or None


@marc21tojson.over('formats', '^300..')
@utils.ignore_value
def marc21_to_description(self, key, value):
    """Get extent, otherMaterialCharacteristics, formats.

    extent: 300$a (the first one if many)
    otherMaterialCharacteristics: 300$b (the first one if many)
    formats: 300 [$c repetitive]
    """
    if value.get('a'):
        if not self.get('extent', None):
            self['extent'] = remove_trailing_punctuation(
                not_repetitive(marc21tojson.bib_id, key, value, 'a'))
    if value.get('b'):
        if self.get('otherMaterialCharacteristics', []) == []:
            self['otherMaterialCharacteristics'] = remove_trailing_punctuation(
                not_repetitive(marc21tojson.bib_id, key, value, 'b'))
    if value.get('c'):
        formats = self.get('formats', None)
        if not formats:
            data = value.get('c')
            formats = list(utils.force_list(data))
        return formats
    else:
        return None


@marc21tojson.over('series', '^490..')
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


@marc21tojson.over('abstracts', '^520..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_abstract(self, key, value):
    """Get abstract."""
    abstract = value.get('a')
    language = value.get('9', 'eng')

    if not abstract:
        return None

    abstracts_data = self.get('abstracts', [])
    abstracts_data.append({'value': abstract, 'language': language})

    self['abstracts'] = abstracts_data

    return None


@marc21tojson.over('identifiedBy', '001')
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


@marc21tojson.over('identifiedBy', '^020..')
@utils.ignore_value
def marc21_to_identified_by_from_020(self, key, value):
    """Get identifier from field 020."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a'):
        return None

    identified_by.append({
        'type': 'bf:Isbn',
        'value': value.get('a')
    })

    return identified_by


@marc21tojson.over('identifiedBy', '^0247.')
@utils.ignore_value
def marc21_to_identified_by_from_024(self, key, value):
    """Get identifier from field 024."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a') or value.get('2') != 'urn':
        return None

    identified_by.append({
        'type': 'bf:Urn',
        'value': value.get('a')
    })

    return identified_by


@marc21tojson.over('identifiedBy', '^027..')
@utils.ignore_value
def marc21_to_identified_by_from_027(self, key, value):
    """Get identifier from field 027."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a'):
        return None

    identified_by.append({
        'type': 'bf:Strn',
        'value': value.get('a')
    })

    return identified_by


@marc21tojson.over('identifiedBy', '^035..')
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


@marc21tojson.over('identifiedBy', '^037..')
@utils.ignore_value
def marc21_to_identified_by_from_037(self, key, value):
    """Get identifier from field 037."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a'):
        return None

    identified_by.append({
        'type': 'bf:Local',
        'source': 'Swissbib',
        'value': value.get('a').replace('swissbib.ch:', '').strip()
    })

    return identified_by


@marc21tojson.over('identifiedBy', '^088..')
@utils.ignore_value
def marc21_to_identified_by_from_088(self, key, value):
    """Get identifier from field 088."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a'):
        return None

    identified_by.append({
        'type': 'bf:ReportNumber',
        'value': value.get('a')
    })

    return identified_by


@marc21tojson.over('identifiedBy', '^091..')
@utils.ignore_value
def marc21_to_identified_by_from_091(self, key, value):
    """Get identifier from field 091."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a') or value.get('b') != 'pmid':
        return None

    identified_by.append({
        'type': 'pmid',
        'value': value.get('a')
    })

    return identified_by


@marc21tojson.over('notes', '^500..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_notes(self, key, value):
    """Get  notes.

    note: [500$a repetitive]
    """
    return not_repetitive(marc21tojson.bib_id, key, value, 'a')


@marc21tojson.over('is_part_of', '^773..')
@utils.ignore_value
def marc21_to_is_part_of(self, key, value):
    """Get  is_part_of.

    is_part_of: [773$t repetitive]
    """
    if not self.get('is_part_of', None):
        return not_repetitive(marc21tojson.bib_id, key, value, 't')


@marc21tojson.over('subjects', '^600..|695..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_subjects(self, key, value):
    """Get subjects."""
    subjects = {
        'label': {
            'value': value.get('a').split(' ; ')
        }
    }

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


@marc21tojson.over('files', '^856..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_files(self, key, value):
    """Get files."""
    key = value.get('f')
    url = value.get('u')
    size = int(value.get('s', 0))
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
        'order': order,
        'size': size
    }

    return data


@marc21tojson.over('otherEdition', '^775..')
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


@marc21tojson.over('specificCollections', '^982..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_specific_collection(self, key, value):
    """Extract collection for record."""
    return value.get('a')
