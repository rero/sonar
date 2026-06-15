# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test documents CLI commands."""

from click.testing import CliRunner

import sonar.modules.documents.cli.oaiharvester as cli


def test_oai_config_create(app, script_info):
    """Test create configuration for harvesting."""
    runner = CliRunner()

    # Test create configuration
    result = runner.invoke(
        cli.oai_config_create,
        ["./tests/ui/documents/data/oai_sources.json"],
        obj=script_info,
    )
    assert result.output.find('Created configuration for "fake"') != -1

    # Test already created configurations
    result = runner.invoke(
        cli.oai_config_create,
        ["./tests/ui/documents/data/oai_sources.json"],
        obj=script_info,
    )
    assert result.output.find('Config already registered for "fake"') != -1

    # Test error on configuration JSON file
    result = runner.invoke(
        cli.oai_config_create,
        ["./tests/ui/documents/data/oai_sources_error.json"],
        obj=script_info,
    )
    assert result.output.find("Configurations file cannot be parsed") != -1


def test_oai_config_info(app, script_info):
    """Test list configurations."""
    runner = CliRunner()

    # Create configurations
    runner.invoke(
        cli.oai_config_create,
        ["./tests/ui/documents/data/oai_sources.json"],
        obj=script_info,
    )

    # List configurations
    result = runner.invoke(cli.oai_config_info, obj=script_info)
    assert result.output.startswith("\nfake")
