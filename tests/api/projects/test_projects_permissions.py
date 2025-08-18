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

"""Test project permissions."""

import json
import time

from flask import url_for
from invenio_access.permissions import any_user
from invenio_accounts.testutils import login_user_via_session


def test_list(
    app,
    client,
    make_project,
    superuser,
    admin,
    moderator,
    submitter,
    user,
    make_user,
    monkeypatch,
):
    """Test list projects permissions."""
    make_project("submitter", "org")
    make_project("admin", "org")
    make_project("submitter", "org2")

    # Wait for record to be indexed.
    time.sleep(1)

    # Not logged
    res = client.get(url_for("projects.search"))
    assert res.status_code == 403

    # Logged as user
    login_user_via_session(client, email=user["email"])
    res = client.get(url_for("projects.search"))
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser["email"])
    res = client.get(url_for("projects.search"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 3
    assert "organisation" in res.json["aggregations"]
    assert "user" in res.json["aggregations"]

    # Logged as submitter
    login_user_via_session(client, email=submitter["email"])
    res = client.get(url_for("projects.search"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert "organisation" not in res.json["aggregations"]
    assert "user" not in res.json["aggregations"]

    # Query string
    res = client.get(url_for("projects.search", q="metadata.name.suggest:Proj"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 2

    # Logged as moderator
    login_user_via_session(client, email=moderator["email"])
    res = client.get(url_for("projects.search"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 2
    assert "organisation" not in res.json["aggregations"]
    assert "user" in res.json["aggregations"]

    # Logged as admin
    login_user_via_session(client, email=admin["email"])
    res = client.get(url_for("projects.search"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 2
    assert "organisation" not in res.json["aggregations"]
    assert "user" in res.json["aggregations"]

    # Logged as user, with admin-access, no query filters
    monkeypatch.setattr(
        "invenio_records_permissions.generators.AdminAction.needs",
        lambda *args, **kwargs: [any_user],
    )
    new_user = make_user("user", "org", "admin_access")
    login_user_via_session(client, email=new_user["email"])
    res = client.get(url_for("projects.search"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 3


def test_create(client, project_json, superuser, admin, moderator, submitter, user):
    """Test create project permissions."""
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Not logged
    res = client.post(url_for("projects.search"), data=json.dumps(project_json), headers=headers)
    assert res.status_code == 403

    # User
    login_user_via_session(client, email=user["email"])
    res = client.post(url_for("projects.search"), data=json.dumps(project_json), headers=headers)
    assert res.status_code == 403

    # submitter
    login_user_via_session(client, email=submitter["email"])
    res = client.post(url_for("projects.search"), data=json.dumps(project_json), headers=headers)
    assert res.status_code == 201

    # Moderator
    login_user_via_session(client, email=moderator["email"])
    res = client.post(url_for("projects.search"), data=json.dumps(project_json), headers=headers)
    assert res.status_code == 201

    # Admin
    login_user_via_session(client, email=admin["email"])
    res = client.post(url_for("projects.search"), data=json.dumps(project_json), headers=headers)
    assert res.status_code == 201

    # Super user
    login_user_via_session(client, email=superuser["email"])
    res = client.post(url_for("projects.search"), data=json.dumps(project_json), headers=headers)
    assert res.status_code == 201


def test_read(client, make_project, make_user, superuser, admin, moderator, submitter, user):
    """Test read project permissions."""
    project1 = make_project("submitter", "org")
    project2 = make_project("submitter", "org2")

    # Not logged
    res = client.get(url_for("projects.read", pid_value=project1["id"]))
    assert res.status_code == 403

    # Logged as user
    login_user_via_session(client, email=user["email"])
    res = client.get(url_for("projects.read", pid_value=project1["id"]))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter["email"])
    res = client.get(url_for("projects.read", pid_value=project1["id"]))
    assert res.status_code == 200

    res = client.get(url_for("projects.read", pid_value=project2["id"]))
    assert res.status_code == 200

    # Logged as moderator
    login_user_via_session(client, email=moderator["email"])
    res = client.get(url_for("projects.read", pid_value=project1["id"]))
    assert res.status_code == 200

    res = client.get(url_for("projects.read", pid_value=project2["id"]))
    assert res.status_code == 200

    # Logged as admin
    login_user_via_session(client, email=admin["email"])
    res = client.get(url_for("projects.read", pid_value=project1["id"]))
    assert res.status_code == 200

    res = client.get(url_for("projects.read", pid_value=project2["id"]))
    assert res.status_code == 200

    # Logged as admin of other organisation
    other_admin = make_user("admin", "org2", access="admin-access")
    login_user_via_session(client, email=other_admin["email"])
    res = client.get(url_for("projects.read", pid_value=project1["id"]))
    assert res.status_code == 200

    # Logged as superuser
    login_user_via_session(client, email=superuser["email"])
    res = client.get(url_for("projects.read", pid_value=project1["id"]))
    assert res.status_code == 200


def test_update(client, make_project, superuser, admin, moderator, submitter, user):
    """Test update project permissions."""
    project1 = make_project("submitter", "org")
    project2 = make_project("submitter", "org2")

    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Not logged
    res = client.put(
        url_for("projects.read", pid_value=project1["id"]),
        data=json.dumps(project1.data),
        headers=headers,
    )
    assert res.status_code == 403

    # Logged as user
    login_user_via_session(client, email=user["email"])
    res = client.put(
        url_for("projects.read", pid_value=project1["id"]),
        data=json.dumps(project1.data),
        headers=headers,
    )
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter["email"])
    res = client.put(
        url_for("projects.read", pid_value=project1["id"]),
        data=json.dumps(project1.data),
        headers=headers,
    )
    assert res.status_code == 200

    res = client.put(
        url_for("projects.read", pid_value=project2["id"]),
        data=json.dumps(project2.data),
        headers=headers,
    )
    assert res.status_code == 403

    # Logged as moderator
    login_user_via_session(client, email=moderator["email"])
    res = client.put(
        url_for("projects.read", pid_value=project1["id"]),
        data=json.dumps(project1.data),
        headers=headers,
    )
    assert res.status_code == 200

    res = client.put(
        url_for("projects.read", pid_value=project2["id"]),
        data=json.dumps(project2.data),
        headers=headers,
    )
    assert res.status_code == 403

    # Logged as admin
    login_user_via_session(client, email=admin["email"])
    res = client.put(
        url_for("projects.read", pid_value=project1["id"]),
        data=json.dumps(project1.data),
        headers=headers,
    )
    assert res.status_code == 200

    res = client.put(
        url_for("projects.read", pid_value=project2["id"]),
        data=json.dumps(project2.data),
        headers=headers,
    )
    assert res.status_code == 403

    # Logged as superuser
    login_user_via_session(client, email=superuser["email"])
    res = client.put(
        url_for("projects.read", pid_value=project1["id"]),
        data=json.dumps(project1.data),
        headers=headers,
    )
    assert res.status_code == 200

    res = client.put(
        url_for("projects.read", pid_value=project2["id"]),
        data=json.dumps(project2.data),
        headers=headers,
    )
    assert res.status_code == 200

    # Save status rejected --> OK
    project2.data["metadata"]["validation"]["status"] = "rejected"
    res = client.put(
        url_for("projects.read", pid_value=project2["id"]),
        data=json.dumps(project2.data),
        headers=headers,
    )
    assert res.status_code == 200

    # Record is rejected, new save is not possible
    project2.data["metadata"]["validation"]["status"] = "validated"
    res = client.put(
        url_for("projects.read", pid_value=project2["id"]),
        data=json.dumps(project2.data),
        headers=headers,
    )
    assert res.status_code == 403


def test_delete(client, db, document, make_project, superuser, admin, moderator, submitter, user):
    """Test delete deposits permissions."""
    project1 = make_project("submitter", "org")
    project2 = make_project("submitter", "org2")

    # Not logged
    res = client.delete(url_for("projects.read", pid_value=project1["id"]))
    assert res.status_code == 403

    # Logged as user
    login_user_via_session(client, email=user["email"])
    res = client.delete(url_for("projects.read", pid_value=project1["id"]))
    assert res.status_code == 403

    # Logged as submitter
    login_user_via_session(client, email=submitter["email"])
    res = client.delete(url_for("projects.read", pid_value=project2["id"]))
    assert res.status_code == 403

    project1 = make_project("submitter", "org")

    # Logged as moderator
    login_user_via_session(client, email=moderator["email"])
    res = client.delete(url_for("projects.read", pid_value=project2["id"]))
    assert res.status_code == 403

    res = client.delete(url_for("projects.read", pid_value=project1["id"]))
    assert res.status_code == 204

    project1 = make_project("submitter", "org")

    # Logged as admin
    login_user_via_session(client, email=admin["email"])
    res = client.delete(url_for("projects.read", pid_value=project2["id"]))
    assert res.status_code == 403

    res = client.delete(url_for("projects.read", pid_value=project1["id"]))
    assert res.status_code == 204

    project1 = make_project("submitter", "org")

    # Logged as superuser
    login_user_via_session(client, email=superuser["email"])
    res = client.delete(url_for("projects.read", pid_value=project1["id"]))
    assert res.status_code == 204

    project1 = make_project("submitter", "org")

    # Cannot remove project as it is linked to document.
    document["projects"] = [{"$ref": f"https://sonar.ch/api/projects/{project1['id']}"}]
    document.commit()
    db.session.commit()
    document.reindex()

    res = client.delete(url_for("projects.read", pid_value=project1["id"]))
    assert res.status_code == 403
