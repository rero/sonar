# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test documents query."""

from flask import url_for


def test_collection_query(db, client, document, collection, search_clear):
    """Test documents query filtered by collection."""
    document["collections"] = [{"$ref": f"https://sonar.ch/api/collections/{collection['pid']}"}]
    document.commit()
    db.session.commit()
    document.reindex()

    res = client.get(
        url_for(
            "invenio_records_rest.doc_list",
            view="org",
            collection_view=collection["pid"],
        )
    )
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 1


def test_identifiers_query(client, document, search_clear):
    """Test identifiers search query."""
    res = client.get(
        url_for(
            "invenio_records_rest.doc_list",
            view="org",
            q="identifiers.local.text:(R003415*)",
        )
    )
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 1


def test_masked_document(db, client, organisation, document, search_clear):
    """Test masked document."""
    # Not masked (property not exists)
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 1

    # Not masked
    document["masked"] = "not_masked"
    document.commit()
    document.reindex()
    db.session.commit()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 1

    # Masked for all
    document["masked"] = "masked_for_all"
    document.commit()
    document.reindex()
    db.session.commit()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 0

    # Masked for external IPs, IP is not allowed
    document["masked"] = "masked_for_external_ips"
    document.commit()
    document.reindex()
    db.session.commit()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 0

    # Masked for external IPs, IP is allowed
    organisation["allowedIps"] = "127.0.0.1/32"
    organisation.commit()
    db.session.commit()
    organisation.reindex()
    document.reindex()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 1

    # Masked for external IPs, IP is allowed
    organisation["allowedIps"] = "127.0.0.*"
    organisation.commit()
    db.session.commit()
    organisation.reindex()
    document.reindex()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 1

    # Masked for external IPs, IP is allowed
    organisation["allowedIps"] = "127.0.0.1"
    organisation.commit()
    db.session.commit()
    organisation.reindex()
    document.reindex()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 1

    # Masked for external IPs, IP is not allowed
    organisation["allowedIps"] = "192.168.1.1"
    organisation.commit()
    db.session.commit()
    organisation.reindex()
    document.reindex()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 0
