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

"""Test REST endpoint for documents."""

import json

from flask import url_for


def test_put(app, client, document_with_file):
    """Test putting metadata on existing file."""
    # Disable configuration
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    headers = [('Content-Type', 'application/json')]

    # Retrieve document by doing a get request.
    response = client.get(url_for('invenio_records_rest.doc_item',
                                  pid_value=document_with_file['pid']),
                          headers=headers)

    # Put data to document
    response = client.put(url_for('invenio_records_rest.doc_item',
                                  pid_value=document_with_file['pid']),
                          headers=headers,
                          data=json.dumps(response.json['metadata']))
    assert response.status_code == 200
