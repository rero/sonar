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

"""Test documents RERODOC cli commands."""

from click.testing import CliRunner
from mock import patch

import sonar.modules.documents.cli.rerodoc as cli


def test_update_file_permissions(app, script_info, document_with_file):
    """Test update file permissions."""
    runner = CliRunner()

    # Not existing input file
    result = runner.invoke(
        cli.update_file_permissions,
        ['./tests/ui/documents/data/not_existing.csv', '-c', '1'],
        obj=script_info)
    assert 'Error: Invalid value for \'PERMISSIONS_FILE\'' in result.output

    # Invalid input file
    result = runner.invoke(
        cli.update_file_permissions,
        ['./tests/ui/documents/data/invalid.csv', '-c', '1'],
        obj=script_info)
    assert 'CSV file seems to be not well formatted.' in result.output

    # File cannot be parsed
    result = runner.invoke(
        cli.update_file_permissions,
        ['./tests/ui/documents/data/permissions_file.pdf', '-c', '1'],
        obj=script_info)
    assert 'An error occured during file process' in result.output

    # OK
    result = runner.invoke(
        cli.update_file_permissions,
        ['./tests/ui/documents/data/permissions_file.csv', '-c', '1'],
        obj=script_info)
    assert 'Process finished' in result.output
