# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""SONAR cli commands."""

import json
from io import BytesIO

import click
import requests
from flask import current_app
from flask.cli import with_appcontext


@click.command('fixtures')
@click.argument('type')
@click.argument('infile', type=click.File('r'))
@with_appcontext
def fixtures(type, infile, *args):
    """Fixtures management commands.

    type: String type of document
    infile: Json document file
    """
    assert isinstance(type, str)

    click.secho('Import {}'.format(type))

    with click.progressbar(json.load(infile)) as records:
        for record in records:
            r = requests.post('{}{}/'.format(
                current_app.config.get('SONAR_FIXTURES_API_URL'), type),
                json=record,
                verify=False,
                headers={'Content-Type': 'application/json'})
            assert r.status_code == 201

    click.secho('Finished', fg='green')
