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
from dojson.contrib.marc21.utils import create_record, split_stream
from flask import current_app
from flask.cli import with_appcontext
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_records import Record

from sonar.modules.documents.dojson.contrib.marc21tojson import marc21tojson
from sonar.modules.institutions.api import InstitutionRecord

from .api import DocumentRecord


@click.group()
def documents():
    """Documents CLI commands."""


@documents.command("import")
@click.argument("institution")
@click.option("--pages", "-p", required=True, type=int, default=10)
@with_appcontext
def import_documents(institution, pages):
    """Import documents from RERO doc.

    institution: String institution filter for retreiving documents
    pages: Number of pages to import
    """
    url = current_app.config.get("SONAR_DOCUMENTS_RERO_DOC_URL")

    click.secho(
        'Importing {pages} pages of records for "{institution}" '
        "from {url}".format(pages=pages, institution=institution, url=url)
    )

    # Get institution record from database
    institution_record = InstitutionRecord.get_record_by_pid(institution)

    if not institution_record:
        raise ClickException("Institution record not found in database")

    institution_ref_link = InstitutionRecord.get_ref_link(
        "institutions", institution_record["pid"]
    )

    # mapping between institution key and RERO doc filter
    institution_map = current_app.config.get(
        "SONAR_DOCUMENTS_INSTITUTIONS_MAP"
    )

    if not institution_map:
        raise ClickException("Institution map not found in configuration")

    if institution not in institution_map:
        raise ClickException(
            'Institution map for "{institution}" not found in configuration, '
            "keys available {keys}".format(
                institution=institution, keys=institution_map.keys()
            )
        )

    key = institution_map[institution]
    current_page = 1

    indexer = RecordIndexer()

    while current_page <= pages:
        click.echo(
            "Importing records {start} to {end}... ".format(
                start=(current_page * 10 - 9), end=(current_page * 10)
            ),
            nl=False,
        )

        # Read Marc21 data for current page
        response = requests.get(
            "{url}?of=xm&jrec={first_record}&c=NAVSITE.{institution}".format(
                url=url,
                first_record=(current_page * 10 - 9),
                institution=key.upper(),
            ),
            stream=True,
        )
        response.raw.decode_content = True

        if response.status_code != 200:
            raise ClickException('Request to "{url}" failed'.format(url=url))

        ids = []

        for data in split_stream(response.raw):
            # Convert from Marc XML to JSON
            record = create_record(data)

            # Transform JSON
            record = marc21tojson.do(record)

            # Add institution
            record["institution"] = {"$ref": institution_ref_link}

            # Register record to DB
            db_record = DocumentRecord.create(record)
            db.session.commit()

            # Add ID for bulk index in elasticsearch
            ids.append(str(db_record.id))

        # index and process queue in elasticsearch
        indexer.bulk_index(ids)
        indexer.process_bulk_queue()

        current_page += 1

        click.secho("Done", fg="green", nl=True)

    click.secho("Finished", fg="green")
