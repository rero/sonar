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

from io import BytesIO
from os.path import isdir

import mock
from click.testing import CliRunner
from invenio_search.cli import destroy

import sonar.modules.cli as Cli


def test_compile_json(app, script_info):
    """Test JSON compilation."""
    runner = CliRunner()

    result = runner.invoke(Cli.compile_json,
                           ['./tests/ui/data/json_to_compile.json'],
                           obj=script_info)

    assert result.output.find('language-v1.0.0.json') == -1
    assert result.output.find('#/definitions/someDefinition') == -1


def test_es_init(app, script_info, es_clear):
    """Test ES init command."""
    runner = CliRunner()

    result = runner.invoke(destroy, ['--yes-i-know'], obj=script_info)
    result = runner.invoke(Cli.es_init, ['--force'], obj=script_info)
    assert result.output.find('Creating indexes...') != -1


def test_clear_files(app, script_info, bucket_location):
    """Test clear files command."""
    runner = CliRunner()

    # Delete ok
    assert isdir(bucket_location.uri)
    result = runner.invoke(Cli.clear_files, obj=script_info)
    assert not isdir(bucket_location.uri)

    # Directory not exists
    result = runner.invoke(Cli.clear_files, obj=script_info)
    assert result.output.find('Directory {directory} cannot be cleaned'.format(
        directory=bucket_location.uri)) != -1


def test_export(app, script_info, document, organisation):
    """Test export command."""
    # Add file to organisation
    organisation.files['logo.jpg'] = BytesIO(b'File content')

    runner = CliRunner()

    # No output directory
    result = runner.invoke(Cli.export, obj=script_info)
    assert result.exit_code == 2

    # No record class found
    result = runner.invoke(Cli.export,
                           ['--pid-type', 'fake', '--output-dir', '/tmp/fake'],
                           obj=script_info)
    assert result.output.find('No record class found for type "fake"') != -1

    # Without export serializer
    result = runner.invoke(Cli.export,
                           ['--pid-type', 'doc', '--output-dir', '/tmp/doc'],
                           obj=script_info)
    assert result.output.find('Export "doc" records') != -1

    # With serializer
    result = runner.invoke(Cli.export,
                           ['--pid-type', 'org', '--output-dir', '/tmp/org'],
                           obj=script_info)
    assert result.output.find('Export "org" records') != -1
