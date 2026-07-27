# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test documents query."""

from flask import url_for


def test_ark_query(db, client, organisation, document, search_clear):
    """Test ark search query."""
    # an empty query: the document should be in the results
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 1

    # check the ark fields in the search output
    doc = res.json["hits"]["hits"][0]["metadata"]
    assert "ark" in doc["permalink"]
    assert "ark" in doc["identifiers"]["ark"][0]

    # the ark identifier field should exists
    ark = document.get_ark()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global", q="_exists_:identifiers.ark"))
    assert res.json["hits"]["total"]["value"] == 1

    # search with the field name
    res = client.get(url_for("invenio_records_rest.doc_list", view="global", q=f'identifiers.ark:"{ark}"'))
    assert res.json["hits"]["total"]["value"] == 1

    # search everywhere
    res = client.get(url_for("invenio_records_rest.doc_list", view="global", q=f'"{ark}"'))
    assert res.json["hits"]["total"]["value"] == 1
