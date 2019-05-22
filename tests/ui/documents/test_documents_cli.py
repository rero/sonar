# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test CLI for importing documents."""

import click
import pytest
from click.exceptions import ClickException
from click.testing import CliRunner
from pytest_invenio.fixtures import script_info

import sonar.modules.documents.cli as Cli
from sonar.modules.institutions.api import InstitutionRecord


def test_import_documents(app, script_info):
    """Test import documents."""
    runner = CliRunner()

    result = runner.invoke(Cli.import_documents, ['test'], obj=script_info)
    assert result.output.find(
        'Institution record not found in database') != -1

    InstitutionRecord.create({
        "pid": "test",
        "name": "Test"
    }, dbcommit=True)

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
