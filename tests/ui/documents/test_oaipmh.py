# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2025 RERO
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

"""Test OAIPMH URLS."""


def test_oaipmh_get(client, app, document):
    """Test OAIPMH API."""
    res = client.get("/oai2d?verb=ListSets")
    assert res.status_code == 200
    assert "<setSpec>org</setSpec>" in res.text

    res = client.get("/oai2d?verb=ListRecords&metadataPrefix=oai_dc&set=org")
    assert res.status_code == 200
    assert "<setSpec>org</setSpec>" in res.text

    res = client.get("/oai2d?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:sonar.ch:1")
    assert res.status_code == 200
    assert "<setSpec>org</setSpec>" in res.text
