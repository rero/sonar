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

"""Test resources CLI."""

from click.testing import CliRunner

from sonar.resources.cli import reindex


def test_reindex(app, script_info, project):
    """Test reindex command."""
    runner = CliRunner()

    # Not existing input file
    result = runner.invoke(reindex, ['projects', '--yes-i-know'],
                           obj=script_info)
    assert 'Record indexed successfully!' in result.output
