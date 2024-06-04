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

"""Test swisscovery rest API."""

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_get_record(client, user, submitter):
    """Test get record on swisscovery."""
    url = url_for("swisscovery.get_record")

    # Not logged
    res = client.get(url)
    assert res.status_code == 401

    # Not authorized
    login_user_via_session(client, email=user["email"])
    res = client.get(url)
    assert res.status_code == 403

    # Bad parameter
    login_user_via_session(client, email=submitter["email"])
    res = client.get(url)
    assert res.status_code == 400

    # No record found
    login_user_via_session(client, email=submitter["email"])
    res = client.get(
        url_for("swisscovery.get_record", query="NON-EXISTING", type="mms_id")
    )
    assert res.status_code == 200
    assert res.json == {}

    # Document serialized
    login_user_via_session(client, email=submitter["email"])
    res = client.get(
        url_for("swisscovery.get_record", query="991087591959705501", type="mms_id")
    )
    assert res.status_code == 200
    assert res.json == {
        "contribution": [
            {
                "agent": {
                    "preferred_name": "Garay Vargas, Javier Leonardo",
                    "type": "bf:Person",
                },
                "role": ["cre"],
            }
        ],
        "documentType": "coar:c_2f33",
        "extent": "174 p.",
        "identifiedBy": [
            {
                "source": "swisscovery",
                "type": "bf:Local",
                "value": "991087591959705501",
            },
            {"type": "bf:Isbn", "value": "9789587105322"},
            {"type": "bf:Isbn", "value": "958710532X"},
        ],
        "language": [{"type": "bf:Language", "value": "spa"}],
        "title": [
            {
                "mainTitle": [
                    {
                        "language": "spa",
                        "value": "¿Política exterior o política de cooperación?",
                    }
                ],
                "subtitle": [
                    {
                        "language": "spa",
                        "value": "una aproximación constructivista al estudio de la política exterior colombiana",
                    }
                ],
                "type": "bf:Title",
            }
        ],
        "provisionActivity": [
            {
                "startDate": "2010",
                "statement": [
                    {"label": {"value": "Bogotá"}, "type": "bf:Place"},
                    {
                        "label": {"value": "Universidad Externado de Colombia"},
                        "type": "bf:Agent",
                    },
                    {"label": {"value": "2010"}, "type": "Date"},
                ],
                "type": "bf:Publication",
            }
        ],
        "notes": ["Bibliografía: p. 163-174"],
        "series": [{"name": "Serie pretextos", "number": "No. 3"}],
        "partOf": [{"document": {"title": "Serie pretextos"}, "numberingVolume": "38"}],
    }

    # Deposit serialized
    login_user_via_session(client, email=submitter["email"])
    res = client.get(
        url_for(
            "swisscovery.get_record",
            query="991087591959705501",
            type="mms_id",
            format="deposit",
        )
    )
    assert res.status_code == 200
    assert res.json == {
        "contributors": [{"name": "Garay Vargas, Javier Leonardo", "role": "cre"}],
        "metadata": {
            "identifiedBy": [
                {
                    "source": "swisscovery",
                    "type": "bf:Local",
                    "value": "991087591959705501",
                },
                {"type": "bf:Isbn", "value": "9789587105322"},
                {"type": "bf:Isbn", "value": "958710532X"},
            ],
            "language": "spa",
            "title": "¿Política exterior o política de cooperación?",
            "subtitle": "una aproximación constructivista al estudio de la política exterior colombiana",
            "documentDate": "2010",
            "statementDate": "2010",
            "documentType": "coar:c_2f33",
            "publicationPlace": "Bogotá",
            "publisher": "Universidad Externado de Colombia",
            "extent": "174 p.",
            "notes": ["Bibliografía: p. 163-174"],
            "series": [{"name": "Serie pretextos", "number": "No. 3"}],
            "publication": {"publishedIn": "Serie pretextos", "volume": "38"},
        },
    }


def test_document_type(client, submitter):
    """Test of the document type with the content of field 502."""
    login_user_via_session(client, email=submitter["email"])
    res = client.get(
        url_for(
            "swisscovery.get_record",
            query="991050676859705501",
            type="mms_id",
            format="deposit",
        )
    )
    assert res.status_code == 200
    data = res.json
    assert data["metadata"]["documentType"] == "coar:c_db06"


def test_title_remove_char(client, submitter):
    """Test for the removal of << and >> characters in the title."""
    login_user_via_session(client, email=submitter["email"])
    res = client.get(url_for("swisscovery.get_record", query="2070406237"))
    assert res.status_code == 200
    assert res.json["title"][0]["mainTitle"][0]["value"] == "La vie est belle"
