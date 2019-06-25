# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Documents CLI commands."""

import json
from functools import partial

import click
import requests
from click.exceptions import ClickException
from flask import current_app
from flask.cli import with_appcontext
from invenio_db import db
from invenio_indexer.api import RecordIndexer

from .api import InstitutionRecord


@click.group()
def institutions():
    """Institutions CLI commands."""


@institutions.command("import")
@with_appcontext
def import_institutions():
    """Import institutions from JSON file."""
    institution_file = "./data/institutions.json"
    click.secho(
        "Importing institution from {file}".format(file=institution_file)
    )

    indexer = RecordIndexer()

    with open(institution_file) as json_file:
        records = json.load(json_file)
        for record in records:
            try:
                # Check existence in DB
                db_record = InstitutionRecord.get_record_by_pid(record["pid"])

                if db_record:
                    raise ClickException("Record already exists in DB")

                # Register record to DB
                db_record = InstitutionRecord.create(record)
                db.session.commit()

                indexer.index(db_record)
            except Exception as error:
                click.secho(
                    "Institution {institution} could not "
                    "be imported: {error}".format(
                        institution=record, error=str(error)
                    ),
                    fg="red",
                )

    click.secho("Finished", fg="green")
