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

from flask import Blueprint, current_app, g, render_template

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


@blueprint.route('/search')
def search():
    """IR search results."""
    search_hidden_params = {'institution': g.ir} \
        if 'ir' in g and g.ir != 'sonar' else None

    return render_template('sonar/search.html',
                           search_hidden_params=search_hidden_params)


def detail(pid, record, template=None, **kwargs):
    """Search details."""
    g.ir = kwargs.get('ir')
    return render_template('documents/record.html', pid=pid, record=record)


@blueprint.app_template_filter()
def authors_format(authors):
    """Format authors for template."""
    output = []
    for author in authors:
        output.append(author['name'])

    return ' ; '.join(output)


@blueprint.app_template_filter()
def nl2br(string):
    r"""Replace \n to <br>."""
    return string.replace('\n', '<br>')


@blueprint.app_template_filter()
def translate_content(records, locale, value_key='value'):
    """Translate record data for the given locale."""
    if not records:
        return None

    lang = get_bibliographic_code_from_language(locale)

    found = [
        abstract for abstract in records
        if abstract['language'] == lang
    ]

    record = None

    if found:
        record = found[0]
    else:
        record = records[0]

    if value_key not in record:
        raise Exception(
            'Value key "{value_key}" in {record} does not exist'.format(
                value_key=value_key, record=record))

    return record[value_key]


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
