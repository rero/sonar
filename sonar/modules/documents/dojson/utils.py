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

"""Dojson utils."""

import csv
import os
import re
import sys

import click
from dojson import Overdo, utils

from sonar.modules.institutions.api import InstitutionRecord


def error_print(*args):
    """Error printing to sdterr."""
    msg = ''
    for arg in args:
        msg += str(arg) + '\t'
    msg.strip()
    click.echo(msg, err=True)
    sys.stderr.flush()


def get_year_from_date(date):
    """Returns the year corresponding to the given date."""
    try:
        int_date = int(date)
        if -9999 <= int_date < 9999:
            return str(int_date)
    except Exception:
        pass
    return None


def not_repetitive(bibid, key, value, subfield, default=None):
    """Get the first value if the value is a list or tuple."""
    if default is None:
        data = value.get(subfield)
    else:
        data = value.get(subfield, default)
    if isinstance(data, (list, tuple)):
        error_print('WARNING NOT REPETITIVE:', bibid, key, subfield, value)
        data = data[0]
    return data


def get_field_link_data(value):
    """Get field link data from subfield $6."""
    subfield_6 = value.get('6', '')
    tag_link = subfield_6.split('-')
    link = ''
    if len(tag_link) == 2:
        link = tag_link[1]
    return tag_link, link


def get_field_items(value):
    """Get field items."""
    if isinstance(value, utils.GroupableOrderedDict):
        return value.iteritems(repeated=True)

    return utils.iteritems(value)


def remove_trailing_punctuation(data,
                                punctuation=',',
                                spaced_punctuation=':;/-'):
    """Remove trailing punctuation from data.

    The punctuation parameter list the
    punctuation characters to be removed
    (preceded by a space or not).

    The spaced_punctuation parameter list the
    punctuation characters needing one or more preceding space(s)
    in order to be removed.
    """
    punctuation = punctuation.replace('.', r'\.').replace('-', r'\-')
    spaced_punctuation = \
        spaced_punctuation.replace('.', r'\.').replace('-', r'\-')
    return re.sub(r'([{0}]|\s+[{1}])$'.format(punctuation, spaced_punctuation),
                  '', data.rstrip()).rstrip()


class SonarOverdo(Overdo):
    """Specialized Overdo.

    The purpose of this class is to store the blob record in order to
    have access to all the record fields during the Overdo processing.
    This class provide also record field manipulation functions.
    """

    blob_record = None

    def __init__(self, bases=None, entry_point_group=None):
        """Sonaroverdo init."""
        super(SonarOverdo, self).__init__(bases=bases,
                                          entry_point_group=entry_point_group)

    def do(self, blob, ignore_missing=True, exception_handlers=None):
        """Translate blob values and instantiate new model instance."""
        self.blob_record = blob
        result = super(SonarOverdo,
                       self).do(blob,
                                ignore_missing=ignore_missing,
                                exception_handlers=exception_handlers)
        return result

    def get_fields(self, tag=None):
        """Get all fields having the given tag value."""
        fields = []
        items = get_field_items(self.blob_record)
        for blob_key, blob_value in items:
            field_data = {}
            tag_value = blob_key[0:3]
            if (tag_value == tag) or not tag:
                field_data['tag'] = tag_value
                if len(blob_key) == 3:  # if control field
                    field_data['data'] = blob_value.rstrip()
                else:
                    field_data['ind1'] = blob_key[3:4]
                    field_data['ind2'] = blob_key[4:5]
                    field_data['subfields'] = blob_value
                fields.append(field_data)
        return fields

    @staticmethod
    def get_control_field_data(field):
        """Get control fields data."""
        field_data = None
        if int(field['tag']) < 10:
            field_data = field['data']
        else:
            raise ValueError('control field expected (tag < 01x)')
        return field_data

    @staticmethod
    def get_subfields(field, code=None):
        """Get all subfields having the given subfield code value."""
        subfields = []
        if int(field['tag']) >= 10:
            items = get_field_items(field['subfields'])
            for subfield_code, subfield_data in items:
                if (subfield_code == code) or not code:
                    subfields.append(subfield_data)
        else:
            raise ValueError('data field expected (tag >= 01x)')
        return subfields


class SonarMarc21Overdo(SonarOverdo):
    """Specialized Overdo.

    This class adds RERO Marc21 properties and functions to the SonarOverdo.
    """

    bib_id = ''
    field_008_data = ''
    lang_from_008 = None
    date1_from_008 = None
    date2_from_008 = None
    date_type_from_008 = ''
    langs_from_041_a = []
    langs_from_041_h = []
    unique_languages = []
    registererd_organizations = []
    alternate_graphic = {}
    country = None
    cantons = []
    affiliations = []

    def __init__(self, bases=None, entry_point_group=None):
        """SonarMarc21Overdo init."""
        super(SonarMarc21Overdo,
              self).__init__(bases=bases, entry_point_group=entry_point_group)
        self.count = 0

    def do(self, blob, ignore_missing=True, exception_handlers=None):
        """Translate blob values and instantiate new model instance."""
        self.count += 1
        result = None
        self.blob_record = blob
        try:
            self.bib_id = self.get_fields(tag='001')[0]['data']
        except Exception as err:
            self.bib_id = '???'
        self.field_008_data = ''
        self.date1_from_008 = None
        self.date2_from_008 = None
        self.date_type_from_008 = ''
        fields_008 = self.get_fields(tag='008')
        if fields_008:
            self.field_008_data = self.get_control_field_data(
                fields_008[0]).rstrip()
            self.date1_from_008 = self.field_008_data[7:11]
            self.date2_from_008 = self.field_008_data[11:15]
            self.date_type_from_008 = self.field_008_data[6]
        self.init_lang()
        self.init_country()
        self.init_alternate_graphic()
        result = super(SonarMarc21Overdo,
                       self).do(blob,
                                ignore_missing=ignore_missing,
                                exception_handlers=exception_handlers)
        return result

    @staticmethod
    def get_link_data(subfields_6_data):
        """Extract link and script data from subfields $6 data."""
        link = None
        tag, extra_data = subfields_6_data.split('-')
        if extra_data:
            link_and_script_data = extra_data.split('/')
            link = link_and_script_data[0]
            try:
                script_code = link_and_script_data[1]
            except Exception:
                script_code = 'latn'
            try:
                script_dir = link_and_script_data[2]
            except Exception:
                script_dir = ''
        return tag, link, script_code, script_dir

    @staticmethod
    def create_institution(institution_key):
        """Create institution if not existing and return it.

        :param str institution_key: Key (PID) of the institution.
        """
        if not institution_key:
            raise Exception('Not key provided')

        # Get institution record from database
        organization = InstitutionRecord.get_record_by_pid(institution_key)

        if not organization:
            # Create organization record
            organization = InstitutionRecord.create(
                {
                    'pid': institution_key,
                    'name': institution_key
                },
                dbcommit=True)
            organization.reindex()

    @staticmethod
    def extract_date(date=None):
        """Try to extract date of birth and date of death from field.

        :param date: String, date to parse
        :returns: Tuple containing date of birth and date of death
        """
        if not date:
            return (None, None)

        # Match a full date
        match = re.search(r'^([0-9]{4}-[0-9]{2}-[0-9]{2})$', date)
        if match:
            return (match.group(1), None)

        # Match these value: "1980-2010"
        match = re.search(r'^([0-9]{4})-([0-9]{4})$', date)
        if match:
            return (match.group(1), match.group(2))

        # Match these value: "1980-" or "1980"
        match = re.search(r'^([0-9]{4})-?', date)
        if match:
            return (match.group(1), None)

        raise Exception('Date "{date}" is not recognized'.format(date=date))

    def get_affiliations(self, full_affiliation):
        """Get controlled affiliations list based on reference CSV file.

        :param full_affiliation: String representing complete affiliation
        """
        if not full_affiliation:
            return []

        if not self.affiliations:
            self.load_affiliations()

        full_affiliation = full_affiliation.lower()

        controlled_affiliations = []

        for affiliations in self.affiliations:
            for affiliation in affiliations:
                if affiliation.lower() in full_affiliation:
                    controlled_affiliations.append(affiliations[0])
                    break

        return controlled_affiliations

    @staticmethod
    def load_affiliations():
        """Load affiliations from reference file."""
        csv_file = os.path.dirname(
            __file__) + '/../../../../data/affiliations.csv'

        SonarMarc21Overdo.affiliations = []

        with open(csv_file, 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                affiliation = []
                for index, value in enumerate(row):
                    if index > 0 and value:
                        affiliation.append(value)

                if affiliation:
                    SonarMarc21Overdo.affiliations.append(affiliation)

    def get_contributor_role(self, role_700=None):
        """Return contributor role.

        :param role_700: String, role found in field 700$e
        :returns: String containing the mapped role or None
        """
        if role_700 in ['Dir.', 'Codir.']:
            return 'dgs'

        if role_700 == 'Libr./Impr.':
            return 'prt'

        if role_700 == 'joint author':
            return 'cre'

        if not role_700:
            doc_type = self.blob_record.get('980__', {}).get('a')

            if not doc_type:
                return None

            if doc_type in ['PREPRINT', 'POSTPRINT', 'DISSERTATION', 'REPORT']:
                return 'cre'

            if doc_type in [
                    'BOOK', 'THESIS', 'MAP', 'JOURNAL', 'PARTITION', 'AUDIO',
                    'IMAGE'
            ]:
                return 'ctb'

        return None

    def init_country(self):
        """Initialization country (008 and 044)."""
        self.country = None
        self.cantons = []
        fields_044 = self.get_fields(tag='044')
        if fields_044:
            field_044 = fields_044[0]
            cantons_codes = self.get_subfields(field_044, 'c')
            for cantons_codes in self.get_subfields(field_044, 'c'):
                try:
                    canton = cantons_codes.split('-')[1].strip()
                    self.cantons.append(canton)
                except Exception:
                    error_print('ERROR INIT CANTONS:', self.bib_id,
                                cantons_codes)
            if self.cantons:
                self.country = 'sz'
        else:
            try:
                self.country = self.field_008_data[15:18].rstrip()
            except Exception:
                pass

    def init_lang(self):
        """Initialization languages (008 and 041)."""

        def init_lang_from(fields_041, code):
            """Construct list of language codes from data."""
            langs_from_041 = []
            for field_041 in fields_041:
                lang_codes = self.get_subfields(field_041, code)
                for lang_from_041 in lang_codes:
                    if lang_from_041 not in langs_from_041:
                        langs_from_041.append(lang_from_041)
            return langs_from_041

        self.lang_from_008 = ''
        self.langs_from_041_a = []
        self.langs_from_041_h = []
        self.unique_languages = []

        try:
            self.lang_from_008 = self.field_008_data[35:38]
        except Exception:
            self.lang_from_008 = 'und'
            error_print('WARNING:', "set 008 language to 'und'")

        fields_041 = self.get_fields(tag='041')
        self.langs_from_041_a = init_lang_from(fields_041, code='a')
        self.langs_from_041_h = init_lang_from(fields_041, code='h')

    def init_alternate_graphic(self):
        """Initialization of alternate graphic representation.

        Parse all the 880 fields and populate a dictionary having as first
        level keys the tag of the linked field and as secound level key the
        link code (from $6) of the linked field. The language script is
        extracted from $6 and used to qualify the alternate graphic value.
        """

        def get_script_from_lang(asian=False):
            """Initialization of alternate graphic representation."""
            script_per_lang_asia = {
                'jpn': 'jpan',
                'kor': 'kore',
                'chi': 'hani'
            }
            script_per_lang_not_asian = {
                'gre': 'grek',
                'grc': 'grek',
                'ara': 'arab',
                'per': 'arab',
                'bel': 'cyrl',
                'rus': 'cyrl',
                'mac': 'cyrl',
                'srp': 'cyrl',
                'ukr': 'cyrl',
                'chu': 'cyrl',
                'yid': 'hebr',
                'heb': 'hebr',
                'lad': 'hebr',
                'chi': 'hani'
            }
            script = None
            default_script = 'zyyy'
            script_per_lang = script_per_lang_not_asian
            if asian:
                default_script = 'hani'
                script_per_lang = script_per_lang_asia
            script = script_per_lang.get(self.lang_from_008, None)
            if not script:
                for lang in self.langs_from_041_a:
                    if lang in script_per_lang:
                        script = script_per_lang[lang]
                        break
                if not script:
                    script = default_script
            return script

        # function init_alternate_graphic start here
        self.alternate_graphic = {}
        script_per_code = {
            '(S': 'grek',
            '(3': 'arab',
            '(B': 'latn',
            '(N': 'cyrl',
            '(2': 'hebr'
        }
        fields_880 = self.get_fields(tag='880')
        for field_880 in fields_880:
            try:
                subfields_6 = self.get_subfields(field_880, code='6')
                for subfield_6 in subfields_6:
                    tag, link, script_code, script_dir = self.get_link_data(
                        subfield_6)
                    tag_data = self.alternate_graphic.get(tag, {})
                    link_data = tag_data.get(link, {})
                    if script_code == '$1':
                        script = get_script_from_lang(asian=True)
                    elif script_per_code.get(script_code) is None:
                        script = script_per_code[script_code]
                    else:
                        script = get_script_from_lang()
                    link_data['script'] = script
                    link_data['field'] = field_880
                    if script_dir == 'r':
                        link_data['right_to_left'] = True
                    tag_data[link] = link_data
                    self.alternate_graphic[tag] = tag_data
            except Exception as exp:
                click.secho('Error in init_alternate_graphic: {error}'.format(
                    error=exp),
                            fg='red')
