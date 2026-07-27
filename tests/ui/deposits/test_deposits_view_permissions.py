# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test deposits files permissions."""

from flask import url_for
from flask_security import url_for_security
from invenio_accounts.testutils import login_user_via_session


def test_read(client, superuser, admin, moderator, submitter, user, deposit):
    """Test read deposits permissions."""
    file_name = "main.pdf"
    users = [superuser, admin, moderator, submitter, user, None]
    url_file_content = url_for(
        "invenio_records_ui.depo_files",
        pid_value=deposit.get("pid"),
        filename=file_name,
    )
    for u, status in zip(users, [200, 200, 200, 404, 404, 404]):
        if u:
            login_user_via_session(client, email=u["email"])
        else:
            client.get(url_for_security("logout"))
        res = client.get(url_file_content)
        assert res.status_code == status
