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

"""Test base overdo."""

from sonar.modules.documents.dojson.overdo import Overdo


def test_not_repetitve():
    """Test the function not_repetetive."""
    data = Overdo.not_repetitive({"sub": ("first", "second")}, "sub")
    assert data == "first"

    data = Overdo.not_repetitive({"sub": "only"}, "sub", "")
    assert data == "only"
