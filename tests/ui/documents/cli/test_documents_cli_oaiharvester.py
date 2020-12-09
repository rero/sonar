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

"""Test documents CLI commands."""

from click.testing import CliRunner
from invenio_oaiharvester.models import OAIHarvestConfig

import sonar.modules.documents.cli.oaiharvester as Cli


def test_oai_config_create(app, script_info):
    """Test create configuration for harvesting."""
    runner = CliRunner()

    # Test create configuration
    result = runner.invoke(Cli.oai_config_create,
                           ['./tests/ui/documents/data/oai_sources.json'],
                           obj=script_info)
    assert result.output.find('Created configuration for "fake"') != -1

    # Test already created configurations
    result = runner.invoke(Cli.oai_config_create,
                           ['./tests/ui/documents/data/oai_sources.json'],
                           obj=script_info)
    assert result.output.find('Config already registered for "fake"') != -1

    # Test error on configuration JSON file
    result = runner.invoke(
        Cli.oai_config_create,
        ['./tests/ui/documents/data/oai_sources_error.json'],
        obj=script_info)
    assert result.output.find('Configurations file cannot be parsed') != -1


def test_oai_config_info(app, script_info):
    """Test list configurations."""
    runner = CliRunner()

    # Create configurations
    runner.invoke(Cli.oai_config_create,
                  ['./tests/ui/documents/data/oai_sources.json'],
                  obj=script_info)

    # List configurations
    result = runner.invoke(Cli.oai_config_info, obj=script_info)
    assert result.output.startswith('\nfake')
