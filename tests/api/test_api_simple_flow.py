# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test simple rest flow."""

import json
from unittest import mock

from flask import url_for
from invenio_accounts.testutils import login_user_via_session

from tests.utils import VerifyRecordPermissionPatch


@mock.patch(
    "invenio_records_rest.views.verify_record_permission",
    mock.MagicMock(return_value=VerifyRecordPermissionPatch),
)
def test_simple_flow(client, document_json, admin, embargo_date):
    """Test simple flow using REST API."""
    headers = [("Content-Type", "application/json")]

    login_user_via_session(client, email=admin["email"])

    # create a record
    response = client.post(
        url_for("invenio_records_rest.doc_list"),
        data=json.dumps(document_json),
        headers=headers,
    )
    assert response.status_code == 201

    # retrieve record
    res = client.get(url_for("invenio_records_rest.doc_item", pid_value=1))
    assert res.status_code == 200
    assert response.json["metadata"]["title"][0]["mainTitle"][0]["value"] == "Title of the document"


def test_add_files_restrictions(client, document_with_file, superuser, embargo_date):
    """Test adding file restrictions before dumping object."""
    login_user_via_session(client, email=superuser["email"])
    res = client.get(
        url_for(
            "invenio_records_rest.doc_item",
            view="global",
            pid_value=document_with_file["pid"],
            resolve=1,
        )
    )
    assert res.status_code == 200
    assert res.json["metadata"]["_files"][0]["restriction"] == {
        "restricted": True,
        "date": embargo_date.strftime("%d/%m/%Y"),
    }
