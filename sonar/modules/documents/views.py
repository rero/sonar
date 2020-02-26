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

import re

from flask import Blueprint, current_app, g, render_template

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.utils import change_filename_extension

from .utils import edition_format_text, localized_data_name, \
    publication_statement_text, series_format_text

blueprint = Blueprint('documents',
                      __name__,
                      template_folder='templates',
                      static_folder='static',
                      url_prefix='/organization/<ir>')
"""Blueprint used for loading templates and static assets

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""


@blueprint.url_defaults
def add_ir(endpoint, values):
    """Add default ir parameter."""
    values.setdefault('ir', 'sonar')


@blueprint.url_value_preprocessor
def pull_ir(endpoint, values):
    """Add ir parameter to global variables."""
    g.ir = values.pop('ir')


@blueprint.route('/')
def index():
    """IR (and SONAR) home view."""
    return render_template('sonar/frontpage.html')


@blueprint.route('/search/<resource_type>')
def search(resource_type=None):
    """IR search results."""
    return render_template('sonar/search.html')


def detail(pid, record, template=None, **kwargs):
    """Search details."""
    g.ir = kwargs.get('ir')
    return render_template('documents/record.html', pid=pid, record=record)


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
def authors_format(pid, language='en', viewcode='sonar'):
    """Format authors for template in given language."""
    doc = DocumentRecord.get_record_by_pid(pid)
    doc = doc.replace_refs()
    output = []
    for author in doc.get('authors', []):
        line = []
        name = localized_data_name(data=author, language=language)
        line.append(name)
        qualifier = author.get('qualifier')
        if qualifier:
            line.append(qualifier)
        date = author.get('date')
        if date:
            line.append(date)

        line = ', '.join(str(x) for x in line)

        output.append(line)

    return '; '.join(output)


@blueprint.app_template_filter()
def edition_format(editions):
    """Format edition for template."""
    output = []
    for edition in editions:
        languages = edition_format_text(edition)
        if languages:
            output.append(languages['default'])
            del languages['default']
            for key, value in languages.items():
                output.append(value)
    return output


@blueprint.app_template_filter()
def publishers_format(publishers):
    """Format publishers for template."""
    output = []
    for publisher in publishers:
        line = []
        places = publisher.get('place', [])
        if places:
            line.append('; '.join(str(x) for x in places) + ': ')
        names = publisher.get('name')
        line.append('; '.join(str(x) for x in names))
        output.append(''.join(str(x) for x in line))
    return '; '.join(str(x) for x in output)


@blueprint.app_template_filter()
def series_format(series):
    """Format series for template."""
    output = []
    for serie in series:
        output.append(series_format_text(serie))
    return '; '.join(str(x) for x in output)


@blueprint.app_template_filter()
def abstracts_format(abstracts):
    """Format abstracts for template."""
    output = []
    for abstract in abstracts:
        output.append(re.sub(r'\n+', '\n', abstract['value']))
    return '\n\n'.join(str(x) for x in output)


@blueprint.app_template_filter()
def subjects_format(subjects):
    """Format subjects for template."""
    output = []
    for subject in subjects:
        output.append(' ; '.join(subject['value']))
    return '\n'.join(str(x) for x in output)


@blueprint.app_template_filter()
def create_publication_statement(provision_activity):
    """Create publication statement from place, agent and date values."""
    return publication_statement_text(provision_activity)


@blueprint.app_template_filter()
def identifiedby_format(identifiedby):
    """Format identifiedby for template."""
    output = []
    for identifier in identifiedby:
        status = identifier.get('status')
        id_type = identifier.get('type')
        if (not status or status == 'valid') and id_type != 'bf:Local':
            if id_type.find(':') != -1:
                id_type = id_type.split(':')[1]
            output.append({'type': id_type, 'value': identifier.get('value')})
    return output


@blueprint.app_template_filter()
def files_by_type(files, file_type='file'):
    """Return only files corresponding to type.

    :param files: List of files associated with record
    :param file_type: Type of the files to return.
    :return Filtered list
    """
    return [file for file in files if file['type'] == file_type]


@blueprint.app_template_filter()
def file_size(size):
    """Return file size human readable.

    :param size: integer representing the size of the file.
    """
    return str(round(size / (1024 * 1024), 2)) + 'Mb'


@blueprint.app_template_filter()
def file_title(file):
    """Return file label or key if label not exists.

    :param file: File to get title from.
    """
    if file.get('label'):
        return file['label']

    return file['key']


@blueprint.app_template_filter()
def thumbnail(file, files):
    """Get thumbnail from file.

    :param file: Dict of file from which thumbnail will be returned.
    :param files: Liste of files of the record.
    """
    key = change_filename_extension(file['key'], 'jpg')

    matches = [file for file in files if file['key'] == key]

    if not matches:
        return None

    return matches[0]


@blueprint.app_template_filter()
def has_external_urls_for_files(record):
    """Check if files point to external website.

    :param record: Current record.
    """
    return record.get('institution', {}).get('pid') and record['institution'][
        'pid'] in current_app.config.get(
            'SONAR_DOCUMENTS_INSTITUTIONS_EXTERNAL_FILES')


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
