# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test resources service."""

from flask import g
from invenio_accounts.testutils import login_user_via_view
from invenio_search import current_search

from sonar.proxies import sonar


def test_bulk_reindex(client, superuser, project):
    """Test bulk reindex."""
    # To be sure project is indexed.
    current_search.flush_and_refresh(index="projects")

    login_user_via_view(client, email=superuser["email"], password="123456")

    service = sonar.service("projects")

    res = service.search(g.identity, q=f"id:{project.id}", size=25, page=1)
    assert res.total == 1

    service.indexer.delete(project._record)
    current_search.flush_and_refresh(index="projects")

    res = service.search(g.identity, q=f"id:{project.id}", size=25, page=1)
    assert res.total == 0

    service.bulk_reindex()
    current_search.flush_and_refresh(index="projects")

    res = service.search(g.identity, q=f"id:{project.id}", size=25, page=1)
    assert res.total == 1
