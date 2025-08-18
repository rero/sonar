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

"""Test SONAR views."""

from datetime import datetime

import pytest
import pytz
from flask import url_for
from invenio_accounts.testutils import login_user_via_session, login_user_via_view

from sonar.help.views import process_link
from sonar.theme.views import format_date, record_image_url


def test_error(client):
    """Test error page"""
    with pytest.raises(Exception):
        assert client.get(url_for("sonar.error"))


def test_robots_txt(app):
    """Test le robots.txt file."""
    with app.test_client() as client:
        url = url_for("sonar.robots_txt")
        app.config.update(SONAR_APP_PRODUCTION_STATE=False)
        res = client.get(url)
        assert res.status_code == 200
        assert b"User-agent: *\nDisallow: /" in res.data

        app.config.update(SONAR_APP_PRODUCTION_STATE=True)
        res = client.get(url)
        assert res.status_code == 200
        assert b"User-agent: *\nAllow: /\n\nSitemap: http://localhost/global/sitemap.xml" in res.data


def test_admin_record_page(app, admin, user_without_role):
    """Test admin page redirection to defaults."""
    with app.test_client() as client:
        file_url = url_for("sonar.manage")

        # User is not logged
        res = client.get(file_url)
        assert res.status_code == 401

        # User is logged, but is not allowed to access the page.
        login_user_via_session(client, email=user_without_role.email)
        res = client.get(file_url)
        assert res.status_code == 403

        # OK, but redirected to the default page
        login_user_via_session(client, email=admin["email"])
        res = client.get(file_url)
        assert res.status_code == 200

        # OK
        file_url = url_for("sonar.manage", path="records/documents")
        res = client.get(file_url)
        assert res.status_code == 200
        assert "</sonar-root>" in str(res.data)


def test_logged_user(app, client, superuser, admin, moderator, submitter, user):
    """Test logged user page."""
    url = url_for("sonar.logged_user")

    res = client.get(url)
    assert res.json["settings"]
    assert not res.json.get("metadata")

    # Logged as admin
    login_user_via_session(client, email=admin["email"])
    res = client.get(url)
    assert res.json["metadata"]["email"] == "orgadmin@rero.ch"
    assert res.json["metadata"]["permissions"]["documents"]["add"]
    assert not res.json["metadata"]["permissions"]["organisations"]["add"]
    assert res.json["metadata"]["permissions"]["users"]["add"]
    assert res.json["metadata"]["permissions"]["deposits"]["add"]

    res = client.get(url + "?resolve=1")
    assert res.json["metadata"]["email"] == "orgadmin@rero.ch"
    assert res.json["metadata"]["pid"] == "orgadmin"

    # Check settings
    assert "settings" in res.json

    # Logged as superuser
    login_user_via_session(client, email=superuser["email"])
    res = client.get(url)
    assert res.json["metadata"]["email"] == "orgsuperuser@rero.ch"
    assert res.json["metadata"]["permissions"]["documents"]["add"]
    assert res.json["metadata"]["permissions"]["organisations"]["add"]
    assert res.json["metadata"]["permissions"]["users"]["add"]
    assert res.json["metadata"]["permissions"]["deposits"]["add"]
    assert res.json["metadata"]["permissions"]["documents"]["list"]
    assert res.json["metadata"]["permissions"]["organisations"]["list"]
    assert res.json["metadata"]["permissions"]["users"]["list"]
    assert res.json["metadata"]["permissions"]["deposits"]["list"]

    # Logged as moderator
    login_user_via_session(client, email=moderator["email"])
    res = client.get(url)
    assert res.json["metadata"]["email"] == "orgmoderator@rero.ch"
    assert res.json["metadata"]["permissions"]["documents"]["add"]
    assert not res.json["metadata"]["permissions"]["organisations"]["add"]
    assert not res.json["metadata"]["permissions"]["users"]["add"]
    assert res.json["metadata"]["permissions"]["deposits"]["add"]
    assert res.json["metadata"]["permissions"]["documents"]["list"]
    assert not res.json["metadata"]["permissions"]["organisations"]["list"]
    assert res.json["metadata"]["permissions"]["users"]["list"]
    assert res.json["metadata"]["permissions"]["deposits"]["list"]

    # Logged as submitter
    login_user_via_session(client, email=submitter["email"])
    res = client.get(url)
    assert res.json["metadata"]["email"] == "orgsubmitter@rero.ch"
    assert not res.json["metadata"]["permissions"]["documents"]["add"]
    assert not res.json["metadata"]["permissions"]["organisations"]["add"]
    assert not res.json["metadata"]["permissions"]["users"]["add"]
    assert res.json["metadata"]["permissions"]["deposits"]["add"]
    assert not res.json["metadata"]["permissions"]["documents"]["list"]
    assert not res.json["metadata"]["permissions"]["organisations"]["list"]
    assert res.json["metadata"]["permissions"]["users"]["list"]
    assert res.json["metadata"]["permissions"]["deposits"]["list"]

    # Logged as user
    login_user_via_session(client, email=user["email"])
    res = client.get(url)
    assert res.json["metadata"]["email"] == "orguser@rero.ch"
    assert not res.json["metadata"]["permissions"]["documents"]["add"]
    assert not res.json["metadata"]["permissions"]["organisations"]["add"]
    assert not res.json["metadata"]["permissions"]["users"]["add"]
    assert not res.json["metadata"]["permissions"]["deposits"]["add"]
    assert not res.json["metadata"]["permissions"]["documents"]["list"]
    assert not res.json["metadata"]["permissions"]["organisations"]["list"]
    assert res.json["metadata"]["permissions"]["users"]["list"]
    assert not res.json["metadata"]["permissions"]["deposits"]["list"]


def test_non_existing_schema(client, user):
    """Test schema no existing."""
    login_user_via_session(client, email=user["email"])
    res = client.get(url_for("sonar.schemas", record_type="not_existing"))
    assert res.status_code == 404


def test_schema_documents(client, user, superuser):
    """Test schema documents."""
    res = client.get(url_for("sonar.schemas", record_type="documents"))
    assert res.status_code == 200
    assert res.json["schema"]["properties"].get("organisation")

    login_user_via_session(client, email=user["email"])
    res = client.get(url_for("sonar.schemas", record_type="documents"))
    assert res.status_code == 200
    assert not res.json["schema"]["properties"].get("collections")
    assert "collections" not in res.json["schema"]["propertiesOrder"]
    assert not res.json["schema"]["properties"].get("subdivisions")
    assert "subdivisions" not in res.json["schema"]["propertiesOrder"]
    assert not res.json["schema"]["properties"].get("organisations")
    assert "organisations" not in res.json["schema"]["propertiesOrder"]

    login_user_via_session(client, email=superuser["email"])
    res = client.get(url_for("sonar.schemas", record_type="documents"))
    assert res.status_code == 200
    assert not res.json["schema"]["properties"].get("collections")
    assert "collections" not in res.json["schema"]["propertiesOrder"]
    assert not res.json["schema"]["properties"].get("subdivisions")
    assert "subdivisions" not in res.json["schema"]["propertiesOrder"]
    assert res.json["schema"]["properties"].get("organisation")
    assert "organisation" in res.json["schema"]["propertiesOrder"]


def test_schema_users(client, admin, admin_shared):
    """Test schema users."""
    res = client.get(url_for("sonar.schemas", record_type="users"))
    assert res.status_code == 200
    assert res.json["schema"]["properties"].get("organisation")
    assert res.json["schema"]["properties"].get("role")

    login_user_via_session(client, email=admin["email"])
    res = client.get(url_for("sonar.schemas", record_type="users"))
    assert res.status_code == 200
    assert not res.json["schema"]["properties"].get("organisation")
    assert res.json["schema"]["properties"].get("role")
    assert len(res.json["schema"]["properties"]["role"]["enum"]) == 4

    login_user_via_session(client, email=admin_shared["email"])
    res = client.get(url_for("sonar.schemas", record_type="users"))
    assert res.status_code == 200
    assert not res.json["schema"]["properties"].get("subdivision")


def test_schema_organisations(client, admin, user, superuser):
    """Test schema organisations."""
    login_user_via_session(client, email=admin["email"])
    # admin user --> no fields `isShared` and `isDedicated`
    res = client.get(url_for("sonar.schemas", record_type="organisations"))
    assert res.status_code == 200
    assert "isShared" not in res.json["schema"]["propertiesOrder"]
    assert "isDedicated" not in res.json["schema"]["propertiesOrder"]
    assert "arkNAAN" not in res.json["schema"]["propertiesOrder"]

    login_user_via_session(client, email=user["email"])
    res = client.get(url_for("sonar.schemas", record_type="users"))
    assert res.status_code == 200
    assert not res.json["schema"]["properties"].get("organisation")
    assert not res.json["schema"]["properties"].get("role")

    login_user_via_session(client, email=superuser["email"])
    res = client.get(url_for("sonar.schemas", record_type="organisations"))
    assert res.status_code == 200
    assert "isShared" in res.json["schema"]["propertiesOrder"]
    assert "isDedicated" in res.json["schema"]["propertiesOrder"]
    assert "arkNAAN" in res.json["schema"]["propertiesOrder"]


def test_schema_projects(client, user):
    """Test schema projects."""
    login_user_via_session(client, email=user["email"])
    res = client.get(url_for("sonar.schemas", record_type="projects"))
    assert res.status_code == 200
    assert not res.json["schema"]["properties"]["metadata"]["properties"].get("organisation")
    assert not res.json["schema"]["properties"].get("role")
    assert "organisation" not in res.json["schema"]["properties"]["metadata"]["propertiesOrder"]


def test_schema_deposits(client, moderator, submitter, moderator_dedicated):
    """Test schema deposits."""
    login_user_via_session(client, email=moderator["email"])
    res = client.get(url_for("sonar.schemas", record_type="deposits"))
    assert res.status_code == 200
    # Moderator with shared organisation
    assert not res.json["schema"]["properties"]["diffusion"]["properties"].get("subdivisions")
    assert "subdivisions" not in res.json["schema"]["properties"]["diffusion"]["propertiesOrder"]
    assert not res.json["schema"]["properties"]["metadata"]["properties"].get("collections")
    assert "collections" not in res.json["schema"]["properties"]["metadata"]["propertiesOrder"]

    login_user_via_session(client, email=submitter["email"])
    res = client.get(url_for("sonar.schemas", record_type="deposits"))
    assert res.status_code == 200
    assert not res.json["schema"]["properties"]["diffusion"]["properties"].get("subdivisions")
    assert "subdivisions" not in res.json["schema"]["properties"]["diffusion"]["propertiesOrder"]
    assert not res.json["schema"]["properties"]["metadata"]["properties"].get("collections")
    assert "collections" not in res.json["schema"]["properties"]["metadata"]["propertiesOrder"]

    # Moderator with dedicated organisation
    login_user_via_session(client, email=moderator_dedicated["email"])
    res = client.get(url_for("sonar.schemas", record_type="deposits"))
    assert res.status_code == 200
    assert res.json["schema"]["properties"]["metadata"]["properties"].get("collections")
    assert "collections" in res.json["schema"]["properties"]["metadata"]["propertiesOrder"]
    assert res.json["schema"]["properties"]["diffusion"]["properties"].get("subdivisions")
    assert "subdivisions" in res.json["schema"]["properties"]["diffusion"]["propertiesOrder"]


def test_profile(client, user):
    """Test profile page."""
    # Not logged
    res = client.get(url_for("sonar.profile"))
    assert res.status_code == 302
    assert res.location.find("/login/") != -1

    # Logged and redirected with user PID as param
    login_user_via_view(client, email=user["email"], password="123456")
    res = client.get(url_for("sonar.profile"))
    assert res.status_code == 302
    assert res.location.find(f"/users/profile/{user['pid']}") != -1

    # Logged
    res = client.get(url_for("sonar.profile", pid=user["pid"]))
    assert res.status_code == 200

    # Wrong PID
    res = client.get(url_for("sonar.profile", pid="wrong"))
    assert res.status_code == 403


def test_record_image_url(client):
    """Test getting record image url."""
    # No file key
    assert not record_image_url({}, "org")

    # No files
    assert not record_image_url({"_files": []}, "org")

    # No images
    assert not record_image_url({"_files": [{"bucket": "1234", "key": "test.pdf"}]}, "org")

    # No pid
    assert not record_image_url({"_files": [{"bucket": "1234", "key": "test.pdf"}]}, "org")

    record = {
        "pid": "1",
        "_files": [
            {"bucket": "1234", "key": "test.jpg"},
            {"bucket": "1234", "key": "test2.jpg"},
        ],
    }

    # Take the first file
    assert record_image_url(record, "org") == "/organisations/1/files/test.jpg"

    # Take files corresponding to key
    assert record_image_url(record, "org", "test2.jpg") == "/organisations/1/files/test2.jpg"


def test_rerodoc_redirection(client, app, document, organisation):
    """Test redirection with RERODOC identifier."""
    global_view = app.config.get("SONAR_APP_DEFAULT_ORGANISATION")
    # does not exist
    res = client.get(url_for("sonar.rerodoc_redirection", pid="NOT-EXISTING"))
    assert res.status_code == 404

    # Files
    res = client.get(url_for("sonar.rerodoc_redirection", pid="111111", filename="test.pdf"))
    assert res.status_code == 302
    assert res.location.find(f"/documents/{document['pid']}/files/test.pdf") != -1

    def changeorg(key, value):
        organisation[key] = value
        organisation.commit()
        organisation.dbcommit()
        # Note: this is not needed as all is done from the db
        # organisation.reindex()

    # No dedicated
    changeorg("isShared", False)
    res = client.get(url_for("sonar.rerodoc_redirection", pid="111111"))
    assert res.status_code == 302
    assert res.location.find(f"/{global_view}/documents/{document['pid']}") != -1

    # Dedicated
    changeorg("isDedicated", True)
    res = client.get(url_for("sonar.rerodoc_redirection", pid="111111"))
    assert res.status_code == 302
    assert res.location.find(f"/{organisation['code']}/documents/{document['pid']}") != -1

    # Shared
    changeorg("isDedicated", False)
    changeorg("isShared", True)
    res = client.get(url_for("sonar.rerodoc_redirection", pid="111111"))
    assert res.status_code == 302
    assert res.location.find(f"/{organisation['code']}/documents/{document['pid']}") != -1


def test_format_date(app):
    """Test date formatting."""
    assert format_date("1984-05-01 14:30:00", "%d/%m/%Y %H:%M") == "01/05/1984 16:30"

    date = datetime(1984, 5, 10, 14, 30)
    assert format_date(date, "%d/%m/%Y %H:%M") == "10/05/1984 16:30"

    timezone = pytz.timezone("Europe/Zurich")
    date = datetime(1984, 5, 10, 14, 30, tzinfo=timezone)
    assert format_date(date, "%d/%m/%Y %H:%M") == "10/05/1984 14:30"


def test_process_link():
    """Test process_link filter."""
    assert process_link("[search tips](/help/search_tips/)", "view") == "[search tips](/view/help/search_tips/)"

    assert (
        process_link(
            '![SONAR_collection.JPG](/help/files/SONAR_collection.JPG "SONAR_collection.JPG")',
            "view",
        )
        == '![SONAR_collection.JPG](/help/files/SONAR_collection.JPG "SONAR_collection.JPG")'
    )
