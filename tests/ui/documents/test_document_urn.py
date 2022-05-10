# -*- coding: utf-8 -*-
#
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

"""Test Dublic Core marshmallow schema."""


import pytest
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from sonar.modules.documents.api import DocumentRecord


@pytest.fixture()
def minimal_document(db, bucket_location, organisation):
    record = DocumentRecord.create(
        {
            "title": [
                {
                    "type": "bf:Title",
                    "mainTitle": [
                        {"language": "eng", "value": "Title of the document"}
                    ],
                }
            ],
            "documentType": "coar:c_db06",
            "organisation": [
                {"$ref": "https://sonar.ch/api/organisations/org"}],
            "identifiedBy": [
                {"type": "bf:Local", "value": "10.1186"},
            ],
        },
        dbcommit=True,
        with_bucket=True,
    )
    record.commit()
    db.session.commit()
    return record


def test_urn_create(minimal_document):
    """Test create URN identifier."""
    urn_code = [
        identifier["value"]
        for identifier in minimal_document.get("identifiedBy")
        if identifier["type"] == "bf:Urn"
    ][0]
    assert urn_code == 'urn:nbn:ch:rero-006-17'
    urn_pid = PersistentIdentifier.get('urn', minimal_document.get('pid'))
    assert urn_pid.status == PIDStatus.NEW
