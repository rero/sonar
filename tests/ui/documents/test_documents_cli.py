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

import requests
from click.testing import CliRunner

import sonar.modules.documents.cli as Cli
from sonar.modules.institutions.api import InstitutionRecord


def test_import_documents(app, script_info, monkeypatch):
    """Test import documents."""
    runner = CliRunner()

    result = runner.invoke(Cli.import_documents, ['test'], obj=script_info)
    assert result.output.find(
        'Institution record not found in database') != -1

    InstitutionRecord.create({
        "pid": "test",
        "name": "Test"
    }, dbcommit=True)

    app.config.update(SONAR_DOCUMENTS_INSTITUTIONS_MAP=None)

    result = runner.invoke(Cli.import_documents, ['test'], obj=script_info)
    assert result.output.find(
        'Institution map not found in configuration') != -1

    app.config.update(SONAR_DOCUMENTS_INSTITUTIONS_MAP=dict(
        usi='ticino.unisi',
        hevs='valais.hevs'
    ))

    result = runner.invoke(Cli.import_documents, ['test'], obj=script_info)
    assert result.output.find(
        'Institution map for "test" not found in configuration') != -1

    result = runner.invoke(Cli.import_documents, ['usi'], obj=script_info)
    assert result.exit_code == 1

    InstitutionRecord.create({
        "pid": "usi",
        "name": "Università della Svizzera italiana"
    }, dbcommit=True)

    result = runner.invoke(
        Cli.import_documents, ['usi', '--pages=1'], obj=script_info)
    assert result.exit_code == 0

    class MockResponse():
        """Mock response."""
        def __init__(self):
            self.status_code = 500

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_get)

    result = runner.invoke(
        Cli.import_documents, ['usi', '--pages=1'], obj=script_info)
    assert result.exit_code == 1
    assert result.output.find('failed') != -1
