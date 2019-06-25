# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test institutions jsonresolvers."""

import pytest
from flask import url_for

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.institutions.api import InstitutionRecord


def test_institution_resolver(client):
    """Test institution resolver."""
    InstitutionRecord.create(
        {"pid": "usi", "name": "Università della Svizzera italiana"}
    )

    record = DocumentRecord.create(
        {
            "title": "The title of the record",
            "institution": {"$ref": "https://sonar.ch/api/institutions/usi"},
        }
    )

    assert (
        record.replace_refs().get("institution")["name"] == "Università "
        "della Svizzera italiana"
    )
