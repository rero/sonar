# -*- coding: utf-8 -*-
#
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

"""Test organisations files permissions."""


from flask import url_for
from flask_security import url_for_security
from invenio_accounts.testutils import login_user_via_session


def test_update_delete(
    client, superuser, admin, moderator, submitter, user, organisation, pdf_file
):
    """Test permissions for uploading and deleting files."""
    file_name = "test.pdf"
    users = [superuser, admin, moderator, submitter, user, None]

    # upload the file
    url_file_content = url_for(
        "invenio_records_files.org_object_api",
        pid_value=organisation.get("pid"),
        key=file_name,
    )
    for u, status in zip(users, [200, 200, 404, 404, 404, 404]):
        if u:
            login_user_via_session(client, email=u["email"])
        else:
            client.get(url_for_security("logout"))
        res = client.put(url_file_content, input_stream=open(pdf_file, "rb"))
        assert res.status_code == status
        if status == 200:
            # the delete return status is no content
            status = 204
            res = client.delete(url_file_content)
            assert res.status_code == status


def test_read_metadata(
    client, superuser, admin, moderator, submitter, user, organisation_with_file
):
    """Test read files permissions."""

    users = [superuser, admin, moderator, submitter, user, None]
    url_files = url_for(
        "invenio_records_files.org_bucket_api",
        pid_value=organisation_with_file.get("pid"),
    )
    for u, status in zip(users, [200, 200, 200, 200, 200, 200]):
        if u:
            login_user_via_session(client, email=u["email"])
        else:
            client.get(url_for_security("logout"))
        res = client.get(url_files)
        assert res.status_code == status


def test_read_content(
    client, superuser, admin, moderator, submitter, user, organisation_with_file
):
    """Test read organisations permissions."""

    file_name = "test1.pdf"
    users = [superuser, admin, moderator, submitter, user, None]
    url_file_content = url_for(
        "invenio_records_files.org_object_api",
        pid_value=organisation_with_file.get("pid"),
        key=file_name,
    )
    for u, status in zip(users, [200, 200, 200, 200, 200, 200]):
        if u:
            login_user_via_session(client, email=u["email"])
        else:
            client.get(url_for_security("logout"))
        res = client.get(url_file_content)
        assert res.status_code == status
