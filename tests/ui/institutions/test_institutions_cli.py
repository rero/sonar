# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test CLI for importing documents."""

import click
from click.testing import CliRunner
from pytest_invenio.fixtures import script_info

import sonar.modules.institutions.cli as Cli
from sonar.modules.institutions.api import InstitutionRecord


def test_import_institutions(app, script_info):
    """Test import institutions."""
    InstitutionRecord.create({
        "pid": "usi",
        "name": "Università della Svizzera italiana"
    })

    runner = CliRunner()

    result = runner.invoke(Cli.import_institutions, obj=script_info)
    assert result.exit_code == 0
