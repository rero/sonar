# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test simple rest flow."""

import json

from invenio_search import current_search


def test_simple_flow(client):
    """Test simple flow using REST API."""
    headers = [("Content-Type", "application/json")]
    data = {
        "title": "The title of the record",
        "abstracts": ["Record summary"],
    }
    url = "https://localhost:5000/documents/"

    # create a record
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.status_code == 201
    current_search.flush_and_refresh("documents")

    # retrieve record
    res = client.get("https://localhost:5000/documents/1")
    assert res.status_code == 200
