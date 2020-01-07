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

"""Test CLI for utils."""

from click.testing import CliRunner
from invenio_search.cli import destroy

import sonar.modules.cli as Cli


def test_compile_json(app, script_info):
    """Test JSON compilation."""
    runner = CliRunner()

    result = runner.invoke(Cli.compile_json,
                           ['./tests/ui/data/json_to_compile.json'],
                           obj=script_info)

    assert result.output.find('#/definitions/language') == -1


def test_es_init(app, script_info, es_clear):
    """Test ES init command."""
    runner = CliRunner()

    result = runner.invoke(destroy, ['--yes-i-know'], obj=script_info)
    result = runner.invoke(Cli.es_init, ['--force'], obj=script_info)
    assert result.output.find('Creating indexes...') != -1
