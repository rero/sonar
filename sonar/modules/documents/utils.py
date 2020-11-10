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

"""Blueprint used for loading templates."""

from __future__ import absolute_import, print_function

import re
from datetime import datetime

from flask import current_app, g, request

from sonar.modules.api import SonarRecord
from sonar.modules.utils import change_filename_extension, format_date, \
    remove_trailing_punctuation


def publication_statement_text(provision_activity):
    """Create publication statement from place, agent and date values."""
    # Only if provision activity is imported from field 269 (no statement,
    # but start date)
    if 'statement' not in provision_activity:
        return format_date(provision_activity['startDate'])

    punctuation = {'bf:Place': ' ; ', 'bf:Agent': ', '}

    statement_with_language = {'default': ''}
    statement_type = None

    for statement in provision_activity['statement']:
        labels = statement['label']

        for label in labels:
            language = label.get('language', 'default')

            if not statement_with_language.get(language):
                statement_with_language[language] = ''

            if statement_with_language[language]:
                if statement_type == statement['type']:
                    statement_with_language[language] += punctuation[
                        statement_type]
                else:
                    if statement['type'] == 'bf:Place':
                        statement_with_language[language] += ' ; '
                    elif statement['type'] == 'Date':
                        statement_with_language[language] += ', '
                    else:
                        statement_with_language[language] += ' : '

            statement_with_language[language] += label['value']
        statement_type = statement['type']

    # date field: remove ';' and append
    for key, value in statement_with_language.items():
        value = remove_trailing_punctuation(value)
        statement_with_language[key] = value
    return statement_with_language


def get_current_organisation_code():
    """Return current organisation by globals or query parameter."""
    # Organisation is present in query parameters, useful for API calls.
    organisation = request.args.get('view')
    if organisation:
        return organisation

    # Organisation stored in globals
    if g.get('organisation', {}).get('code'):
        return g.organisation['code']

    # Default organisation
    return current_app.config.get('SONAR_APP_DEFAULT_ORGANISATION')


def get_file_links(file, record):
    """Return link data to preview and/or download the file.

    :param file: File record.
    :param record: Record.
    :returns: Dict containing the URL, the download URL and the type of link.
    """
    links = {'external': None, 'preview': None, 'download': None}

    # File is restricted, no link.
    if file['restriction']['restricted']:
        return links

    # File has an external url
    if record['external_url'] and file.get('external_url'):
        links['external'] = file['external_url']
        return links

    match = re.search(r'\.(.*)$', file['key'])
    if not match:
        return links

    links['download'] = '/documents/{pid}/files/{key}'.format(
        pid=record['pid'], key=file['key'])

    if not match.group(1) in current_app.config.get(
            'SONAR_APP_FILE_PREVIEW_EXTENSIONS', []):
        return links

    links['preview'] = '/documents/{pid}/preview/{key}'.format(
        pid=record['pid'], key=file['key'])
    return links


def get_file_restriction(file, record):
    """Check if current file can be displayed.

    :param file: File dict
    :param record: Current record
    :returns object containing result and possibly embargo date
    """

    def is_restricted_by_scope(file):
        """File is restricted by scope (internal, rero or organisation).

        :param file: File object.
        """
        # File is restricted by internal IPs
        if file['restricted'] == 'internal':
            return request.remote_addr not in current_app.config.get(
                'SONAR_APP_INTERNAL_IPS')

        # File is restricted by organisation
        organisation = get_current_organisation_code()

        # We are in global organisation, so restriction is active
        if organisation == current_app.config.get(
                'SONAR_APP_DEFAULT_ORGANISATION'):
            return True

        # No organisation in record, restriction is active
        if not record.get('organisation', {}).get('pid'):
            return True

        # Record organisation is different from current organisation
        if organisation != record['organisation']['pid']:
            return True

        return False

    restricted = {'restricted': False, 'date': None}

    try:
        embargo_date = datetime.strptime(file.get('embargo_date'), '%Y-%m-%d')
    except Exception:
        embargo_date = None

    # Store embargo date if greater than now
    if embargo_date and embargo_date > datetime.now():
        restricted['restricted'] = True
        restricted['date'] = embargo_date.strftime('%d/%m/%Y')

    # File is restricted by organisation
    if file.get('restricted'):
        restricted['restricted'] = is_restricted_by_scope(file)

    if not restricted['restricted']:
        restricted['date'] = None

    return restricted


def has_external_urls_for_files(record):
    """Check if files point to external website.

    :param record: Current record.
    :returns: True if record's organisation is configured to point files to an
    external URL.
    """
    if not record.get('organisation', {}):
        return False

    organisation_pid = SonarRecord.get_pid_by_ref_link(
        record['organisation']['$ref']) if record['organisation'].get(
            '$ref') else record['organisation']['pid']

    return organisation_pid in current_app.config.get(
        'SONAR_DOCUMENTS_ORGANISATIONS_EXTERNAL_FILES')


def get_thumbnail(file, record):
    """Get thumbnail from file.

    If file is restricted, a restricted image is returned. If no thumbnail
    found, a default image is returned.

    :param file: Dict of file from which thumbnail will be returned.
    :param record: Record object.
    :returns: URL to thumbnail file.
    """
    if file['restriction']['restricted']:
        return 'static/images/restricted.png'

    key = change_filename_extension(file['key'], 'jpg')

    matches = [file for file in record['_files'] if file['key'] == key]

    if not matches:
        return 'static/images/no-image.png'

    return '/documents/{pid}/files/{key}'.format(pid=record['pid'], key=key)


def populate_files_properties(record):
    """Add restriction, link and thumbnail to file.

    :param record: Record object
    :param file: File dict
    """
    for file in record['_files']:
        if file.get('type') == 'file':
            file['restriction'] = get_file_restriction(file, record)
            file['thumbnail'] = get_thumbnail(file, record)
            file['links'] = get_file_links(file, record)
