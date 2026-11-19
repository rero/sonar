# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test CLI for utils."""

from io import BytesIO
from os.path import isdir

from click.testing import CliRunner

import sonar.modules.cli.utils as cli


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
