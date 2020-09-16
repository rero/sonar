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

"""Test deposits utils."""

import os

import pytest
from flask import g

from sonar.modules.documents.views import store_organisation
from sonar.modules.utils import change_filename_extension, \
    create_thumbnail_from_file, format_date, get_current_language, \
    get_specific_theme, get_switch_aai_providers, get_view_code


def test_change_filename_extension(app):
    """Test change filename extension."""
    with pytest.raises(Exception) as e:
        change_filename_extension('test', 'txt')
    assert str(e.value) == 'test is not a valid filename'

    assert change_filename_extension('test.pdf', 'txt') == 'test.txt'


def test_create_thumbnail_from_file():
    """Test thumbnail creation from file path."""
    # Mime type is not allowed
    with pytest.raises(Exception) as exception:
        create_thumbnail_from_file('file/path/test.pdf', 'text/plain')
    assert str(
        exception.value
    ) == 'Cannot create thumbnail from file file/path/test.pdf with mimetype' \
        ' "text/plain", only images and PDFs are allowed'

    # File not exists
    with pytest.raises(Exception) as exception:
        create_thumbnail_from_file('file/path/test.pdf', 'application/pdf')
    assert str(exception.value).startswith('unable to open image')

    # Thumbnail creation for PDF is OK
    file = os.path.dirname(__file__) + '/data/sample.pdf'
    assert create_thumbnail_from_file(
        file, 'application/pdf').startswith(b'Fake thumbnail image content')

    # Thumbnail creation for image is OK
    file = os.path.dirname(__file__) + '/data/sample.jpg'
    assert create_thumbnail_from_file(
        file, 'image/jpeg').startswith(b'Fake thumbnail image content')


def test_get_switch_aai_providers(app):
    """Test getting the list of SWITCHaai providers."""
    # Full list of providers
    app.config.update(SHIBBOLETH_IDENTITY_PROVIDERS={'idp': {}, 'idpdev': {}})
    assert get_switch_aai_providers() == ['idp', 'idpdev']

    # Removes providers containing dev
    app.config.update(SHIBBOLETH_IDENTITY_PROVIDERS={
        'idp': {},
        'idpdev': {
            'dev': True
        }
    })
    assert get_switch_aai_providers() == ['idp']


def test_get_current_language(app):
    """Test getting the current language."""
    assert get_current_language() == 'en'

    with app.test_request_context(headers=[('Accept-Language', 'fr')]):
        assert get_current_language() == 'fr'


def test_get_view_code(app, organisation):
    """Test get view code stored in organisation."""
    with app.test_request_context() as req:
        req.request.view_args['view'] = 'org'
        store_organisation()

    assert get_view_code() == 'org'

    g.pop('organisation', None)
    assert get_view_code() == 'global'


def test_format_date():
    """Test date formatting."""
    # Just year
    assert format_date('2020') == '2020'

    # Complete date
    assert format_date('2020-01-01') == '01.01.2020'

    # No processing
    assert format_date('July 31, 2020') == 'July 31, 2020'


def test_get_specific_theme(app, organisation, make_organisation):
    """Test getting a theme by organisation."""
    with app.test_request_context() as req:
        req.request.view_args['view'] = 'org'
        store_organisation()

    # Not dedicated --> global theme
    assert get_specific_theme() == 'global-theme.css'

    # Dedicated, but no specific style --> global theme
    g.organisation['isDedicated'] = True
    assert get_specific_theme() == 'global-theme.css'

    # Dedicated and specific style --> specific theme
    make_organisation('usi')
    with app.test_request_context() as req:
        req.request.view_args['view'] = 'usi'
        store_organisation()

    g.organisation['isDedicated'] = True
    assert get_specific_theme() == 'usi-theme.css'
