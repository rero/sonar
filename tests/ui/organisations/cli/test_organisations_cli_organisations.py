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

"""Test CLI for organisations."""

from click.testing import CliRunner

import sonar.modules.organisations.cli.organisations as Cli
from sonar.modules.organisations.api import OrganisationRecord


def test_import_organisations(app, script_info, bucket_location,
                              without_oaiset_signals):
    """Test import organisations."""
    runner = CliRunner()

    datastore = app.extensions['security'].datastore
    datastore.create_role(name='admin')

    # Import ok
    result = runner.invoke(Cli.import_organisations,
                           ['./tests/ui/organisations/data/valid.json'],
                           obj=script_info)
    organisation = OrganisationRecord.get_record_by_pid('test')
    assert organisation
    assert organisation['pid'] == 'test'

    # Already existing
    result = runner.invoke(Cli.import_organisations,
                           ['./tests/ui/organisations/data/valid.json'],
                           obj=script_info)
    assert result.output.find(
        'Organisation {\'code\': \'test\', \'name\': \'Test\'} could not be '
        'imported: Record already exists in DB')
