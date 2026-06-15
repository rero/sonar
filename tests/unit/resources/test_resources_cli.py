# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test resources CLI."""

from click.testing import CliRunner

from sonar.resources.cli import reindex


def test_reindex(app, script_info, project):
    """Test reindex command."""
    runner = CliRunner()

    # Not existing input file
    result = runner.invoke(reindex, ["projects", "--yes-i-know"], obj=script_info)
    assert "Record indexed successfully!" in result.output
