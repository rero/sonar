# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test OAIPMH URLS."""


def test_oaipmh_get(client, org_oaiset, document):
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
