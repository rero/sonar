# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test OAIPMH URLS."""

from sonar.modules.documents.dumpers import IndexerDumper
from sonar.modules.documents.oaipmh_utils import getrecord_fetcher
from sonar.suggestions.dumpers import FIELD as SUGGESTIONS_FIELD


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


def test_oaipmh_getrecord_fetcher(app, document):
    """Test that the fetched record drops the values denormalized for the index."""
    assert SUGGESTIONS_FIELD in document.dumps(IndexerDumper())
    assert SUGGESTIONS_FIELD not in getrecord_fetcher(document.id)


def test_oaipmh_get_deleted_document(client, document):
    """Test OAIPMH GetRecord on a deleted document."""
    identifier = f"oai:sonar.ch:{document['pid']}"
    document.delete(dbcommit=True, delindex=True)

    res = client.get(f"/oai2d?verb=GetRecord&metadataPrefix=oai_dc&identifier={identifier}")
    assert res.status_code == 422
    assert '<error code="idDoesNotExist">' in res.text
