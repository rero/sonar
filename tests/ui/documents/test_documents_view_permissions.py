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

"""Test documents files permissions."""


from flask import url_for
from flask_security import url_for_security
from invenio_accounts.testutils import login_user_via_session


def test_read(client, superuser, admin, moderator,
              submitter, user, user_without_org, document_with_file):
    """Test read documents permissions."""

    file_name = 'test1.pdf'
    users = [
        superuser, admin, moderator, submitter, user, user_without_org, None]
    url_file_content = url_for(
        'invenio_records_ui.doc_files',
        pid_value=document_with_file.get('pid'),
        filename=file_name)
    open_access_code = "coar:c_abf2"
    document_with_file.files[file_name]['access'] = open_access_code
    document_with_file.commit()
    for u, status in zip(users, [200, 200, 200, 200, 200, 200, 200]):
        if u:
            login_user_via_session(client, email=u['email'])
        else:
            client.get(url_for_security('logout'))
        res = client.get(url_file_content)
        assert res.status_code == status
    # Masked document
    document_with_file['masked'] = 'masked_for_all'
    document_with_file.commit()
    for u, status in zip(users, [200, 200, 200, 404, 404, 404, 404]):
        if u:
            login_user_via_session(client, email=u['email'])
        else:
            client.get(url_for_security('logout'))
        res = client.get(url_file_content)
        assert res.status_code == status

    del document_with_file['masked']

    # restricted files
    restricted_code = "coar:c_16ec"
    document_with_file.files[file_name]['access'] = restricted_code
    document_with_file.files[file_name]['restricted_outside_organisation'] = True
    document_with_file.commit()
    for u, status in zip(users, [200, 200, 200, 200, 200, 404, 404]):
        if u:
            login_user_via_session(client, email=u['email'])
        else:
            client.get(url_for_security('logout'))
        res = client.get(url_file_content)
        assert res.status_code == status
