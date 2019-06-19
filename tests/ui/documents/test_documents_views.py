# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test documents views."""

import pytest
from flask import g, url_for

import sonar.modules.documents.views as views
from sonar.modules.documents.api import DocumentRecord


def test_pull_ir(app):
    """Test pull IR."""
    views.pull_ir(None, {"ir": "sonar"})


def test_index(client):
    """Test frontpage."""
    assert isinstance(views.index(), str)
    assert client.get('/').status_code == 200


def test_search(app, client):
    """Test search."""
    assert isinstance(views.search(), str)
    assert client.get(
        url_for('invenio_search_ui.search')).status_code == 200


def test_detail(app, client):
    """Test document detail page."""
    record = DocumentRecord.create({
        "title": "The title of the record"
    }, dbcommit=True)

    # assert isinstance(views.detail('1', record, ir='sonar'), str)
    assert client.get('/organization/sonar/documents/1').status_code == 200


def test_authors_format():
    """Test author format filter."""
    authors = [{'name': 'John Newby'}, {'name': 'Kevin Doner'}]

    assert views.authors_format(authors) == 'John Newby ; Kevin Doner'


def test_nl2br():
    """Test nl2br conversion."""
    text = 'Multiline text\nMultiline text'
    assert views.nl2br(text) == 'Multiline text<br>Multiline text'


def test_translate_content(app):
    """Test content item translation."""
    assert views.translate_content([], 'fr') is None

    records = [{
        'language': 'eng',
        'value': 'Summary of content'
    }, {
        'language': 'fre',
        'value': 'Résumé du contenu'
    }]
    assert views.translate_content(records, 'fr') == 'Résumé du contenu'
    assert views.translate_content(records, 'de') == 'Summary of content'
    assert views.translate_content(records, 'pt') == 'Summary of content'

    with pytest.raises(Exception) as e:
        views.translate_content(records, 'de', 'not_existing_key')
    assert str(
        e.value
    ) == 'Value key "not_existing_key" in {record} does not exist'.format(
        record=records[0])


def test_get_code_from_bibliographic_language(app):
    """Test bibliographic language code to alpha 2 code conversion."""
    assert views.get_language_from_bibliographic_code('ger') == 'de'

    with pytest.raises(Exception) as e:
        views.get_language_from_bibliographic_code('zzz')
    assert str(e.value) == 'Language code not found for "zzz"'


def test_get_bibliographic_code_from_language(app):
    """Test bibliographic language code to alpha 2 code conversion."""
    with pytest.raises(Exception) as e:
        views.get_bibliographic_code_from_language("zz")
    assert str(e.value) == 'Language code not found for "zz"'

    assert views.get_bibliographic_code_from_language('de') == 'ger'
