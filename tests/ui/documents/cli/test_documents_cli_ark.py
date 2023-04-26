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

from sonar.modules.ark import cli
from sonar.modules.documents.api import DocumentRecord


def test_ark_disabled_cli(app, script_info):
    """Test ARK command line interface with ARK disabled."""
    resolver = app.config['SONAR_APP_ARK_RESOLVER']
    app.config['SONAR_APP_ARK_RESOLVER'] = None

    runner = CliRunner()

    # server status
    result = runner.invoke(
        cli.ark,
        ['config'],
        obj=script_info)
    assert 'ARK is not enabled.' in result.output

    app.config['SONAR_APP_ARK_RESOLVER'] = resolver


def test_ark_cli_cfg(app, script_info):
    """Test ARK command line interface."""

    runner = CliRunner()

    # ark server config
    result = runner.invoke(
        cli.config,
        obj=script_info)
    assert 'config' in result.output


def test_ark_cli_create_missing_org_not_exists(app, script_info):
    """Test create missing ark with the given org pid does not exist."""
    runner = CliRunner()
    # ark server config
    result = runner.invoke(
        cli.create_missing,
        ['foo'],
        obj=script_info)
    assert 'not exist' in result.output


def test_ark_cli_create_missing_no_doc(app, script_info, organisation):
    """Test create missing ark with no doc to update."""
    runner = CliRunner()
    result = runner.invoke(
        cli.create_missing,
        ['org'],
        obj=script_info)
    assert 'No document found.' in result.output


def test_ark_cli_create_missing(app, db, script_info, organisation, make_document):
    """Test create missing ark."""
    runner = CliRunner()

    # remove the naan configuration in the organisation
    naan = organisation['arkNAAN']
    del organisation['arkNAAN']
    organisation.commit()

    result = runner.invoke(
        cli.create_missing,
         ['org'],
        obj=script_info)
    assert 'NAAN configuration does not exist' in result.output

    # Create a document without an ark
    doc = make_document()
    assert not doc.get_ark()
    #restore the configuration
    organisation['arkNAAN'] = naan
    organisation.commit()

    # remove the should to disable the ARK in the instance
    shoulder = app.config.get('SONAR_APP_ARK_SHOULDER')
    app.config['SONAR_APP_ARK_SHOULDER'] = None
    result = runner.invoke(
        cli.create_missing,
        ['org'],
        obj=script_info)
    assert 'Ark is not enabled' in result.output

    # restore the ARK config
    app.config['SONAR_APP_ARK_SHOULDER'] = shoulder
    # document should be processed
    result = runner.invoke(
        cli.create_missing,
        ['org'],
        obj=script_info)
    assert 'has been updated' in result.output
    # the ark exists in the document
    assert DocumentRecord.get_record_by_pid(doc['pid']).get_ark()

    # the second call do nothing
    result = runner.invoke(
        cli.create_missing,
        ['org'],
        obj=script_info)
    assert 'No document found.' in result.output
