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

"""Test resources service."""

import time

from flask import g
from invenio_accounts.testutils import login_user_via_view

from sonar.proxies import sonar


def test_bulk_reindex(client, superuser, project):
    """Test bulk reindex."""
    time.sleep(1)

    login_user_via_view(client, email=superuser['email'], password='123456')
    service = sonar.service('projects')

    res = service.search(g.identity,
                         q=f'id:{project.id}',
                         size=25,
                         page=1)
    assert res.total == 1

    service.indexer.delete(project._record)
    time.sleep(1)

    res = service.search(g.identity,
                         q=f'id:{project.id}',
                         size=25,
                         page=1)
    assert res.total == 0

    service.bulk_reindex()
    time.sleep(1)

    res = service.search(g.identity,
                         q=f'id:{project.id}',
                         size=25,
                         page=1)
    assert res.total == 1
