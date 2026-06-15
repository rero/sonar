# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test CLI for deposits."""

import os

from click.testing import CliRunner

import sonar.modules.cli.utils as cli


def test_create(app, script_info):
    """Test create location."""
    runner = CliRunner()

    directory = os.path.join(app.instance_path, "files")

    os.makedirs(directory, 0o755, exist_ok=True)

    result = runner.invoke(cli.clear_files, ["--yes-i-know"], obj=script_info)
    assert "Finished" in result.output
