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

"""Test CLI for importing documents."""

import click
from click.testing import CliRunner
from pytest_invenio.fixtures import script_info

import sonar.modules.institutions.cli as Cli
from sonar.modules.institutions.api import InstitutionRecord


def test_import_institutions(app, script_info):
    """Test import institutions."""
    InstitutionRecord.create({
        "pid": "usi",
        "name": "Università della Svizzera italiana"
    })

    runner = CliRunner()

    result = runner.invoke(Cli.import_institutions, obj=script_info)
    assert result.exit_code == 0
