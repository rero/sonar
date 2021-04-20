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


def test_ark_disabled_cli(app, script_info):
    """Test ARK command line interface with ARK disabled."""

    runner = CliRunner()

    # server status
    result = runner.invoke(
        cli.ark,
        ['config'],
        obj=script_info)
    assert 'ARK is not enabled.' in result.output


def test_ark_bad_auth_cli(app, script_info, monkeypatch, mock_ark):
    """Test ARK command line interface with bad authentication."""

    # enable ARK with bad credential
    monkeypatch.setitem(app.config, 'SONAR_APP_ARK_USER', 'unauthorized')

    runner = CliRunner()

    # server login
    result = runner.invoke(
        cli.ark,
        ['login'],
        obj=script_info)
    assert 'unauthorized' in result.output

    # mint a new ark id
    result = runner.invoke(
        cli.mint,
        ['https://sonar.ch/global/documents/1'],
        obj=script_info)
    assert 'unauthorized' in result.output

    # create a new ark id
    result = runner.invoke(
        cli.create,
        ['1', 'https://sonar.ch/global/documents/1'],
        obj=script_info)
    assert 'unauthorized' in result.output

    # update the target of an existing ark id
    result = runner.invoke(
        cli.update,
        ['1', 'https://sonar.ch/view1/documents/1'],
        obj=script_info)
    assert 'unauthorized' in result.output

    # invalidate a an existing ark id
    result = runner.invoke(
        cli.delete,
        ['1'],
        obj=script_info)
    assert 'unauthorized' in result.output


def test_ark_cli(app, script_info, mock_ark):
    """Test ARK command line interface."""

    runner = CliRunner()

    # server status
    result = runner.invoke(
        cli.status,
        obj=script_info)
    assert 'message: EZID is up' in result.output

    # get ark information
    # monkeypatch.setattr(Ark, 'get', ArkMock.get)
    result = runner.invoke(
        cli.get,
        ['7'],
        obj=script_info)
    assert '"success": "ark:/99999/ffk37"' in result.output

    # ark resolution
    result = runner.invoke(
        cli.resolve,
        ['7'],
        obj=script_info)
    assert result.output.startswith('http')

    # ark server login
    result = runner.invoke(
        cli.login,
        obj=script_info)
    assert 'session cookie returned' in result.output

    # ark server config
    result = runner.invoke(
        cli.config,
        obj=script_info)
    assert 'config' in result.output

    # mint a new ark id
    result = runner.invoke(
        cli.mint,
        ['https://sonar.ch/global/documents/1'],
        obj=script_info)
    assert result.output.startswith('ark:/')

    # create a new ark id
    result = runner.invoke(
        cli.create,
        ['1', 'https://sonar.ch/global/documents/1'],
        obj=script_info)
    assert result.output.startswith('ark:/')

    # update the target of an existing ark id
    result = runner.invoke(
        cli.update,
        ['1', 'https://sonar.ch/view1/documents/1'],
        obj=script_info)
    assert result.output.startswith('ark:/')

    # invalidate a an existing ark id
    result = runner.invoke(
        cli.delete,
        ['1'],
        obj=script_info)
    assert result.output.startswith('ark:/')
