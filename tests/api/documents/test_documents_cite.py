# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test citation REST endpoint for documents."""

from unittest import mock

from flask import url_for


def test_citation_styles(client):
    """Citation styles endpoint returns all supported styles."""
    res = client.get(url_for("documents.citation_styles"))
    assert res.status_code == 200
    assert res.json == [
        {"id": "apa_7", "label": "APA (7th edition)"},
        {"id": "chicago_17", "label": "Chicago (17th edition)"},
        {"id": "harvard_12", "label": "Harvard (12th edition)"},
        {"id": "mla_9", "label": "MLA (9th edition)"},
    ]


def test_cite_not_found(client):
    """Unknown pid returns 404."""
    res = client.get(url_for("documents.citation", pid_value="unknown-pid"))
    assert res.status_code == 404


def test_cite_invalid_style(client, document):
    """Unsupported style returns 400."""
    res = client.get(url_for("documents.citation", pid_value=document["pid"], style="bibtex"))
    assert res.status_code == 400
    assert "style" in res.json["message"].lower()


def test_cite_default_style(client, document):
    """Default style (apa) is used when no style param is given."""
    res = client.get(url_for("documents.citation", pid_value=document["pid"]))
    assert res.status_code == 200
    assert "citation" in res.json
    assert res.json["citation"]


def test_cite_all_styles(client, document):
    """All supported styles return a non-empty citation."""
    for style in ("apa_7", "chicago_17", "mla_9", "harvard_12"):
        res = client.get(url_for("documents.citation", pid_value=document["pid"], style=style))
        assert res.status_code == 200, f"Style {style} returned {res.status_code}"
        assert res.json["citation"], f"Style {style} returned empty citation"


def test_cite_contains_title(client, document):
    """Citation contains the document title."""
    res = client.get(url_for("documents.citation", pid_value=document["pid"]))
    assert "Title of the document" in res.json["citation"]


def test_cite_lang_param(client, document):
    """Lang param is accepted and does not break the response."""
    res = client.get(url_for("documents.citation", pid_value=document["pid"], style="apa_7", lang="eng"))
    assert res.status_code == 200
    assert "Title of the document" in res.json["citation"]


def test_cite_masked_document_denied_anonymous(client, document):
    """Anonymous citation of a masked document is denied with 401."""
    magic_mock = mock.MagicMock(return_value=True)
    with mock.patch("sonar.modules.documents.api.DocumentRecord.is_masked", magic_mock):
        res = client.get(url_for("documents.citation", pid_value=document["pid"]))
        assert res.status_code == 401


def test_cite_contains_document_link(client, document):
    """Citation contains a link back to the document when there is no DOI."""
    res = client.get(url_for("documents.citation", pid_value=document["pid"]))
    assert document["pid"] in res.json["citation"]
