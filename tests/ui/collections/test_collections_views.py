# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test collections views."""

from flask import url_for


def test_index(app, client, organisation):
    """Test list of collections."""
    # No collection index for global view
    assert client.get(url_for("collections.index", view="global")).status_code == 404

    # OK in organisation context
    assert client.get(url_for("collections.index", view="org")).status_code == 200


def test_detail(app, client, organisation, collection):
    """Test collection detail."""
    # No detail view in global context
    assert client.get(url_for("invenio_records_ui.coll", view="global", pid_value=collection["pid"])).status_code == 404

    # OK in organisation context
    result = client.get(url_for("invenio_records_ui.coll", view="org", pid_value=collection["pid"]))
    assert result.status_code == 302
    assert result.location.find(f"collection_view={collection['pid']}") != -1
