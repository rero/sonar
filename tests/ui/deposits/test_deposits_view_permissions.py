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
