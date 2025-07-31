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

"""Test documents API."""

from uuid import uuid4

from flask import url_for
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from sonar.modules.ark.api import Ark


def test_ark_create(app):
    """ARK id creation."""
    ark = Ark(naan="99999")
    doc_pid = "1234"
    ark_id = f"ark:/99999/ffk3{doc_pid}"
    assert ark
    assert (
        ark.config()
        == """
config:
    resolver: https://n2t.net
    scheme: ark:
    shoulder: ffk3
    naan: 99999
"""
    )
    assert ark.ark_from_id(pid=doc_pid) == ark_id
    assert ark.resolver_url(pid=doc_pid).endswith(f"{ark_id}")
    assert ark.resolve(ark_id) == doc_pid
    pid = ark.create(doc_pid, uuid4())
    assert pid.status == PIDStatus.REGISTERED
    assert pid == ark.get(doc_pid)
    db.session.rollback()


def test_create_doc_with_ark(document, client, organisation):
    """Create a document and mint a ARK id."""
    # pid does not exist
    res = client.get(url_for("ark.resolve", naan="99999", path=f"ffk3foo"))
    assert res.status_code == 404

    # naan does not exist in organisations
    res = client.get(
        url_for("ark.resolve", naan="FOO999", path=f'ffk3{document.get("pid")}')
    )
    assert res.status_code == 404

    # a valid ark
    ark_id = f'ark:/99999/ffk3{document.get("pid")}'
    assert document.get_ark() == ark_id
    res = client.get(
        url_for("ark.resolve", naan="99999", path=f'ffk3{document.get("pid")}')
    )
    assert res.status_code == 302

    # the redirect to the right location
    assert res.location == f'/{organisation.get("code")}/documents/1'

    # the redirected URL give a valid response
    res = client.get(
        url_for("ark.resolve", naan="99999", path=f'ffk3{document.get("pid")}'),
        follow_redirects=True,
    )
    assert res.status_code == 200

    document.delete()
    pid = PersistentIdentifier.get("ark", ark_id)
    assert pid.status == PIDStatus.DELETED
    res = client.get(
        url_for("ark.resolve", naan="99999", path=f'ffk3{document.get("pid")}')
    )
    # redirect to the existing document and thumbstone
    assert res.status_code == 302
    assert res.location == f'/{organisation.get("code")}/documents/1'

    # the redirected URL is deleted
    res = client.get(
        url_for("ark.resolve", naan="99999", path=f'ffk3{document.get("pid")}'),
        follow_redirects=True,
    )
    # Gone
    assert res.status_code == 410
    db.session.rollback()
