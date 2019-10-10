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

"""Test CLI for deposits."""
import os

from click.testing import CliRunner

import sonar.modules.deposits.cli as cli


def test_create(app, script_info):
    """Test create location."""
    runner = CliRunner()

    directory = os.path.join(app.instance_path, 'files')

    os.mkdir(directory, 0o755)

    result = runner.invoke(cli.create, obj=script_info)
    assert 'Location #1 created successfully' in result.output
