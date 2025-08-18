# Swiss Open Access Repository
# Copyright (C) 2022 RERO
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

"""Test DnbUrnService rest API."""

import mock
import requests_mock
from invenio_pidstore.models import PersistentIdentifier

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.dnb import DnbUrnService


def test_dnb_rest_api_verify_exist(app):
    """Test dnb rest api verify code exist."""
    with requests_mock.mock() as response:
        response.head(requests_mock.ANY, status_code=200)
        urn_code = "urn:nbn:ch:rero-006-119656"
        assert DnbUrnService.exists(urn_code)


def test_dnb_rest_api_verify_not_exist(app):
    """Test dnb rest api verify code does not exist."""
    with requests_mock.mock() as response:
        response.head(requests_mock.ANY, status_code=404)
        urn_code = "urn:nbn:ch:rero-006-119654__"
        assert not DnbUrnService.exists(urn_code)


def test_dnb_rest_api_register(organisation_with_urn):
    """Test dnb rest api register new code."""
    with requests_mock.mock() as response:
        from sonar.modules.documents.urn import Urn

        # mock the next URN id
        with mock.patch.object(Urn, "_generate_urn") as mock_method:
            urn = "urn:nbn:ch:rero-006-17"
            mock_method.return_value = urn
            response.head(requests_mock.ANY, status_code=404)
            response.post(requests_mock.ANY, status_code=201, json={"urn": urn})
            doc = DocumentRecord.create(
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
                dbcommit=False,
                with_bucket=False,
            )
            urn_code = DocumentRecord.get_rero_urn_code(doc)
            assert urn_code
            assert PersistentIdentifier.get("urn", urn_code).status == "R"
