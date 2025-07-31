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

"""Test client views for PDF extractor."""

from invenio_accounts.testutils import login_user_via_view


def test_pdf_extractor_test_page(client, user):
    """Test the PDF extractor test page."""
    login_user_via_view(client, email=user["email"], password="123456")

    response = client.get("/pdf-extractor/test")
    assert response.status_code == 200
    assert "PDF metadata extraction" in str(response.data)
