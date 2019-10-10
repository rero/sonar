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

import pytest

from sonar.modules.deposits.utils import change_filename_extension


def test_change_filename_extension(app):
    """Test change filename extension."""
    with pytest.raises(Exception) as e:
        change_filename_extension('test', 'txt')
    assert str(e.value) == 'test is not a valid filename'

    assert change_filename_extension('test.pdf', 'txt') == 'test.txt'
