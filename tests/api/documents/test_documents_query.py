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
    assert res.json["hits"]["total"] == 1


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
    assert res.json["hits"]["total"] == 1


def test_masked_document(db, client, organisation, document, search_clear):
    """Test masked document."""
    # Not masked (property not exists)
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1

    # Not masked
    document["masked"] = "not_masked"
    document.commit()
    document.reindex()
    db.session.commit()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1

    # Masked for all
    document["masked"] = "masked_for_all"
    document.commit()
    document.reindex()
    db.session.commit()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0

    # Masked for external IPs, IP is not allowed
    document["masked"] = "masked_for_external_ips"
    document.commit()
    document.reindex()
    db.session.commit()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0

    # Masked for external IPs, IP is allowed
    organisation["allowedIps"] = "127.0.0.1/32"
    organisation.commit()
    db.session.commit()
    organisation.reindex()
    document.reindex()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1

    # Masked for external IPs, IP is allowed
    organisation["allowedIps"] = "127.0.0.*"
    organisation.commit()
    db.session.commit()
    organisation.reindex()
    document.reindex()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1

    # Masked for external IPs, IP is allowed
    organisation["allowedIps"] = "127.0.0.1"
    organisation.commit()
    db.session.commit()
    organisation.reindex()
    document.reindex()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1

    # Masked for external IPs, IP is not allowed
    organisation["allowedIps"] = "192.168.1.1"
    organisation.commit()
    db.session.commit()
    organisation.reindex()
    document.reindex()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0


def test_anonymous_document_list_without_view(db, client, organisation, document, search_clear):
    """Test anonymous document list defaults to the global, non-masked scope."""
    # No view: behaves like the global view for anonymous users.
    res = client.get(url_for("invenio_records_rest.doc_list"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1

    # Masked documents are excluded, with or without a view.
    document["masked"] = "masked_for_all"
    document.commit()
    document.reindex()
    db.session.commit()
    res = client.get(url_for("invenio_records_rest.doc_list"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0

    # Masked for external IPs, IP is not allowed.
    document["masked"] = "masked_for_external_ips"
    document.commit()
    document.reindex()
    db.session.commit()
    res = client.get(url_for("invenio_records_rest.doc_list"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0

    # Masked for external IPs, IP is allowed.
    organisation["allowedIps"] = "127.0.0.1/32"
    organisation.commit()
    db.session.commit()
    organisation.reindex()
    document.reindex()
    res = client.get(url_for("invenio_records_rest.doc_list"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1

    # Org-scoped view still filters by organisation for anonymous users.
    res = client.get(url_for("invenio_records_rest.doc_list", view="org"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1

    res = client.get(url_for("invenio_records_rest.doc_list", view="org2"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0


def test_document_list_on_dedicated_portal(
    db, client, organisation, make_organisation, make_document, user, search_clear
):
    """Test public document list on a dedicated portal is restricted to its organisation."""
    portal_url = "https://org.domain.com"
    organisation.update({"isDedicated": True, "serverName": "org.domain.com"})
    organisation.commit()
    db.session.commit()
    organisation.reindex()

    make_document()
    make_organisation("org2")
    document = make_document()
    document["organisation"] = [{"$ref": "https://sonar.ch/api/organisations/org2"}]
    document.commit()
    db.session.commit()
    document.reindex()

    # Main domain: no view means the global scope.
    res = client.get(url_for("invenio_records_rest.doc_list"))
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 2

    def assert_portal_totals():
        # Only the documents of the portal organisation, whatever the view.
        for view, total in [(None, 1), ("global", 1), ("org", 1), ("org2", 0)]:
            res = client.get(url_for("invenio_records_rest.doc_list", view=view), base_url=portal_url)
            assert res.status_code == 200
            assert res.json["hits"]["total"] == total

    # Dedicated portal, anonymous user.
    assert_portal_totals()

    # Dedicated portal, logged-in non-moderator. The session cookie is bound to
    # the host, so it must be created for the portal.
    with client.session_transaction(base_url=portal_url) as session:
        session["_user_id"] = user.user.get_id()
    res = client.get(url_for("invenio_records_rest.user_item", pid_value=user["pid"]), base_url=portal_url)
    assert res.status_code == 200
    assert_portal_totals()
