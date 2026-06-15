# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test CLI for utils."""

from io import BytesIO
from os.path import isdir

import invenio_accounts.cli as cliusers
from click.testing import CliRunner
from invenio_search.cli import destroy

import sonar.modules.cli.utils as cli


def test_es_init(app, script_info, search_clear):
    """Test ES init command."""
    runner = CliRunner()

    result = runner.invoke(destroy, ["--yes-i-know"], obj=script_info)
    result = runner.invoke(cli.es_init, ["--force"], obj=script_info)
    assert result.output.find("Creating indexes...") != -1


def test_clear_files(app, script_info, bucket_location):
    """Test clear files command."""
    runner = CliRunner()

    # Delete ok
    assert isdir(bucket_location.uri)
    result = runner.invoke(cli.clear_files, ["--yes-i-know"], obj=script_info)
    assert not isdir(bucket_location.uri)

    # Directory not exists
    result = runner.invoke(cli.clear_files, ["--yes-i-know"], obj=script_info)
    assert result.output.find(f"Directory {bucket_location.uri} cannot be cleaned") != -1


def test_export(app, script_info, document, organisation):
    """Test export command."""
    # Add file to organisation
    organisation.files["logo.jpg"] = BytesIO(b"File content")

    runner = CliRunner()

    # No output directory
    result = runner.invoke(cli.export, obj=script_info)
    assert result.exit_code == 2

    # No record class found
    result = runner.invoke(cli.export, ["--pid-type", "fake", "--output-dir", "/tmp/fake"], obj=script_info)
    assert result.output.find('No record class found for type "fake"') != -1

    # Without export serializer
    result = runner.invoke(cli.export, ["--pid-type", "doc", "--output-dir", "/tmp/doc"], obj=script_info)
    assert result.output.find('Export "doc" records') != -1

    # With serializer
    result = runner.invoke(cli.export, ["--pid-type", "org", "--output-dir", "/tmp/org"], obj=script_info)
    assert result.output.find('Export "org" records') != -1


def test_cli_access_token(app, db, script_info):
    """Test access token cli."""
    runner = CliRunner()
    email = "test@test.com"
    res = runner.invoke(
        cliusers.users,
        ["create", "--active", "--confirm", "--password", "PWD_TEST", email],
        obj=script_info,
    )
    res = runner.invoke(
        cli.token_create,
        ["-n", "test_good", "-u", email, "-t", "my_token"],
        obj=script_info,
    )
    assert res.output.strip().split("\n") == ["my_token"]

    res = runner.invoke(
        cli.token_create,
        ["-n", "test_fail", "-u", "fail@test.com", "-t", "my_token"],
        obj=script_info,
    )
    assert res.output.strip().split("\n") == ["No user found"]
