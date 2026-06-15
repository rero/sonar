# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Pytest fixtures and plugins for the API application."""

import pytest
import requests_mock
from invenio_app.factory import create_api

from sonar.modules.documents.api import DocumentRecord


@pytest.fixture(scope="module")
def create_app():
    """Create test app."""
    return create_api


@pytest.fixture()
def minimal_thesis_document(db, bucket_location, organisation):
    """Return a minimal thesis document."""
    with requests_mock.mock() as response:
        response.head(requests_mock.ANY, status_code=404)
        response.post(requests_mock.ANY, status_code=201, json={"urn": "urn:nbn:ch:rero-006-17"})
        record = DocumentRecord.create(
            {
                "title": [
                    {
                        "type": "bf:Title",
                        "mainTitle": [{"language": "eng", "value": "Title of the document"}],
                    }
                ],
                "documentType": "coar:c_db06",
                "organisation": [{"$ref": "https://sonar.ch/api/organisations/org"}],
                "identifiedBy": [
                    {"type": "bf:Local", "value": "10.1186"},
                ],
            },
            dbcommit=True,
            with_bucket=True,
        )
        record.commit()
        db.session.commit()
        record.reindex()
        return record
