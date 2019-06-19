# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test documents views."""

import pytest
from flask import url_for

import sonar.modules.documents.views as views
from sonar.modules.documents.api import DocumentRecord


def test_pull_ir(app):
    """Test pull IR."""
    views.pull_ir(None, {"ir": "sonar"})


def test_index(client):
    """Test frontpage."""
    assert isinstance(views.index(), str)
    assert client.get("/").status_code == 200


def test_search(app, client):
    """Test search."""
    assert isinstance(views.search(), str)
    assert client.get(url_for("invenio_search_ui.search")).status_code == 200


def test_detail(app, client):
    """Test document detail page."""
    DocumentRecord.create({"title": "The title of the record"}, dbcommit=True)

    # assert isinstance(views.detail('1', record, ir='sonar'), str)
    assert client.get("/organization/sonar/documents/1").status_code == 200


def test_authors_format():
    """Test author format filter."""
    authors = [{"name": "John Newby"}, {"name": "Kevin Doner"}]

    assert views.authors_format(authors) == "John Newby ; Kevin Doner"


def test_nl2br():
    """Test nl2br conversion."""
    text = "Multiline text\nMultiline text"
    assert views.nl2br(text) == "Multiline text<br>Multiline text"


def test_translate_language():
    """Test language translation."""
    assert views.translate_language("fre", "en") == "French"


def test_translate_content():
    """Test content item translation."""
    records = {"eng": "Summary of content", "fre": "Résumé du contenu"}
    assert views.translate_content(records, "fr") == "Résumé du contenu"
    assert views.translate_content(records, "de") == "Summary of content"
    assert views.translate_content(records, "pt") == "Summary of content"


def test_get_code_from_bibliographic_language():
    """Test bibliographic language code to alpha 2 code conversion."""
    assert views.get_code_from_bibliographic_language("ger") == "de"
    assert views.get_code_from_bibliographic_language("por") == "en"


def test_get_bibliographic_code_from_language():
    """Test bibliographic language code to alpha 2 code conversion."""
    assert not views.get_bibliographic_code_from_language("aa")
    assert views.get_bibliographic_code_from_language("de") == "ger"
