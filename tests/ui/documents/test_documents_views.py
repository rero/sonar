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
