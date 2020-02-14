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

import mock
import pytest

from sonar.modules.utils import change_filename_extension, \
    create_thumbnail_from_file


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
