# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Pytest fixtures and plugins for the API application."""

from __future__ import absolute_import, print_function

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
