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

"""Test collections views."""

from flask import url_for


def test_index(app, client, organisation):
    """Test list of collections."""
    # No collection index for global view
    assert client.get(url_for('collections.index',
                              view='global')).status_code == 404

    # OK in organisation context
    assert client.get(url_for('collections.index',
                              view='org')).status_code == 200


def test_detail(app, client, organisation, collection):
    """Test collection detail."""
    # No detail view in global context
    assert client.get(
        url_for('invenio_records_ui.coll',
                view='global',
                pid_value=collection['pid'])).status_code == 404

    # OK in organisation context
    result = client.get(
        url_for('invenio_records_ui.coll',
                view='org',
                pid_value=collection['pid']))
    assert result.status_code == 302
    assert result.location.find(f'collection_view={collection["pid"]}') != -1
