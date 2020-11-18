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

"""Blueprint definitions."""

from __future__ import absolute_import, print_function

from flask import Blueprint, abort, current_app, g, render_template, request
from flask_babelex import gettext as _
from invenio_i18n.ext import current_i18n

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.utils import has_external_urls_for_files, \
    populate_files_properties
from sonar.modules.organisations.api import OrganisationRecord
from sonar.modules.projects.api import ProjectRecord
from sonar.modules.projects.marshmallow.json import ProjectMetadataSchemaV1
from sonar.modules.utils import format_date

from .utils import publication_statement_text

blueprint = Blueprint('documents',
                      __name__,
                      template_folder='templates',
                      static_folder='static',
                      url_prefix='/<view>')
"""Blueprint used for loading templates and static assets

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""


@blueprint.url_defaults
def default_view_code(endpoint, values):
    """Add default view code."""
    values.setdefault('view',
                      current_app.config.get('SONAR_APP_DEFAULT_ORGANISATION'))


@blueprint.before_request
def store_organisation():
    """Add organisation record to global variables."""
    view = request.view_args.get(
        'view', current_app.config.get('SONAR_APP_DEFAULT_ORGANISATION'))

    if view != current_app.config.get('SONAR_APP_DEFAULT_ORGANISATION'):
        organisation = OrganisationRecord.get_record_by_pid(view)

        if not organisation or not organisation.get('isShared'):
            abort(404)

        g.organisation = organisation.dumps()


@blueprint.route('/')
def index(view='global'):
    """Homepage."""
    return render_template('sonar/frontpage.html')


@blueprint.route('/search/documents')
def search(view='global'):
    """Search results page."""
    return render_template('sonar/search.html')


@blueprint.route('/documents/<pid_value>')
def detail(pid_value, view='global'):
    """Document detail page."""
    record = DocumentRecord.get_record_by_pid(pid_value)

    if not record:
        abort(404)

    # Add restriction, link and thumbnail to files
    if record.get('_files'):
        # Check if organisation's record forces to point file to an external
        # url
        record['external_url'] = has_external_urls_for_files(record)

        populate_files_properties(record)

    # Resolve $ref properties
    record = record.replace_refs()

    return render_template('documents/record.html',
                           pid=pid_value,
                           record=record)


@blueprint.route('/projects/<pid_value>')
def project_detail(pid_value, view='global'):
    """Project detail view.

    :param pid_value: Project PID.
    :param view: Organisation's view.
    :returns: Rendered template.
    """
    record = ProjectRecord.get_record_by_pid(pid_value)

    if not record:
        abort(404)

    record = record.replace_refs()
    # Serialize record to have the same transformation as REST API.
    record = ProjectMetadataSchemaV1().dump(record)

    return render_template('sonar/projects/detail.html',
                           pid=pid_value,
                           record=record)


@blueprint.app_template_filter()
def nl2br(string):
    r"""Replace \n to <br>."""
    return string.replace('\n', '<br>')


@blueprint.app_template_filter()
def title_format(title, language):
    """Format title for template.

    :param list title: List of titles.
    :param str language: Language to retreive title from.
    """
    language = get_bibliographic_code_from_language(language)

    preferred_languages = get_preferred_languages(language)

    def get_value(items):
        """Return the value for the given language."""
        if not items:
            return None

        for preferred_language in preferred_languages:
            for item in items:
                if item['language'] == preferred_language:
                    return item['value']

        return items[0]['value']

    output = []
    main_title = get_value(title.get('mainTitle', []))
    if main_title:
        output.append(main_title)

    subtitle = get_value(title.get('subtitle', []))
    if subtitle:
        output.append(subtitle)

    return " : ".join(output)


@blueprint.app_template_filter()
def create_publication_statement(provision_activity):
    """Create publication statement from place, agent and date values."""
    return publication_statement_text(provision_activity)


@blueprint.app_template_filter()
def file_size(size):
    """Return file size human readable.

    :param size: integer representing the size of the file.
    """
    return str(round(size / (1024 * 1024), 2)) + 'Mb'


@blueprint.app_template_filter()
def part_of_format(part_of):
    """Format partOf property for display.

    :param part_of: Object representing partOf property
    """
    items = []
    if part_of.get('document', {}).get('title'):
        items.append(part_of['document']['title'])

    items.append(part_of['numberingYear'])

    if 'numberingVolume' in part_of:
        items.append('{label} {value}'.format(
            label=_('vol.'), value=part_of['numberingVolume']))

        if 'numberingIssue' in part_of:
            items.append('{label} {value}'.format(
                label=_('no.'), value=part_of['numberingIssue']))

        if 'numberingPages' in part_of:
            items.append('{label} {value}'.format(
                label=_('p.'), value=part_of['numberingPages']))

    return ', '.join(items)


@blueprint.app_template_filter()
def contributors(record):
    """Get ordered list of contributors."""
    if not record.get('contribution'):
        return []

    priorities = ['cre', 'ctb', 'dgs', 'edt', 'prt']

    return sorted(record['contribution'],
                  key=lambda i: priorities.index(i['role'][0]))


@blueprint.app_template_filter()
def abstracts(record):
    """Get ordered list of abstracts."""
    if not record.get('abstracts'):
        return []

    language = get_bibliographic_code_from_language(
        current_i18n.locale.language)
    preferred_languages = get_preferred_languages(language)

    return sorted(
        record['abstracts'],
        key=lambda abstract: preferred_languages.index(abstract['language']))


@blueprint.app_template_filter()
def dissertation(record):
    """Get dissertation text."""
    if not record.get('dissertation'):
        return None

    dissertation_text = [record['dissertation']['degree']]

    # Dissertation has grantingInstitution or date
    if record['dissertation'].get(
            'grantingInstitution') or record['dissertation'].get('date'):
        dissertation_text.append(': ')

        # Add grantingInstitution
        if record['dissertation'].get('grantingInstitution'):
            dissertation_text.append(
                record['dissertation']['grantingInstitution'])

        # Add date
        if record['dissertation'].get('date'):
            dissertation_text.append(', {date}'.format(
                date=format_date(record['dissertation']['date'])))

    # Add jury note
    if record['dissertation'].get('jury_note'):
        dissertation_text.append(' ({label}: {note})'.format(
            label=_('Jury note').lower(),
            note=record['dissertation']['jury_note']))

    return ''.join(dissertation_text)


@blueprint.app_template_filter()
def contribution_text(contribution):
    """Display contribution row text.

    :param contribution: Dict representing the contribution.
    :returns: Formatted text.
    """
    data = [contribution['agent']['preferred_name']]

    # Meeting
    if contribution['agent']['type'] == 'bf:Meeting':
        meeting = []
        if contribution['agent'].get('number'):
            meeting.append(contribution['agent']['number'])

        if contribution['agent'].get('date'):
            meeting.append(contribution['agent']['date'])

        if contribution['agent'].get('place'):
            meeting.append(contribution['agent']['place'])

        data.append('({meeting})'.format(meeting=' : '.join(meeting)))

    # Person
    if contribution['agent'][
            'type'] == 'bf:Person' and contribution['role'][0] != 'cre':
        data.append('({role})'.format(role=_('contribution_role_{role}'.format(
            role=contribution['role'][0])).lower()))

    return ' '.join(data)


def get_language_from_bibliographic_code(language_code):
    """Return language code from bibliographic language.

    For example, get_language_code_from_bibliographic_language('ger') will
    return 'de'

    :param language_code: Bibliographic language
    :return str
    """
    languages_map = current_app.config.get('SONAR_APP_LANGUAGES_MAP')

    if language_code not in languages_map:
        raise Exception('Language code not found for "{language_code}"'.format(
            language_code=language_code))

    return languages_map[language_code]


def get_bibliographic_code_from_language(language_code):
    """Return bibliographic language code from language.

    For example, get_bibliographic_code_from_language("de") will
    return "ger"

    :param language_code: Bibliographic language
    :return str
    """
    for key, lang in current_app.config.get('SONAR_APP_LANGUAGES_MAP').items():
        if lang == language_code:
            return key

    raise Exception('Language code not found for "{language_code}"'.format(
        language_code=language_code))


def get_preferred_languages(force_language=None):
    """Get the ordered list of preferred languages.

    :param forceLanguage: String, force a language to be the first.
    """
    preferred_languages = current_app.config.get(
        'SONAR_APP_PREFERRED_LANGUAGES', []).copy()

    if force_language:
        preferred_languages.insert(0, force_language)

    return list(dict.fromkeys(preferred_languages))
