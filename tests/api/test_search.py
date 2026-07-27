# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Search tests."""

from flask import url_for


def test_search_special_chars_not_rejected(client):
    """Test that Lucene and MARC special chars in query strings return 200.

    OAUTH2SERVER_ALLOWED_URLENCODE_CHARACTERS extends the oauthlib default so
    that these client-generated query characters are intentionally accepted and
    no longer rejected with a 400 by the OAuth middleware.  Spaces must still be
    encoded as %20.

    The public document search (``view``) is used so the endpoint is reachable
    without authentication; the characters are sent unencoded to exercise the
    raw query-string parsing done by the OAuth middleware.
    """
    base_url = url_for("invenio_records_rest.doc_list", view="global")

    # $ — MARC subfield codes ($a, $b, $c); unencoded by Angular's HttpClient
    res = client.get(f"{base_url}&q=customField1:$a%20test%20$b%202026")
    assert res.status_code == 200

    # [] — Lucene inclusive range query
    res = client.get(f"{base_url}&q=year:[2024%20TO%202026]")
    assert res.status_code == 200

    # {} — Lucene exclusive range query
    res = client.get(f"{base_url}&q=year:{{2024%20TO%202026}}")
    assert res.status_code == 200

    # ^ — Lucene boost factor
    res = client.get(f"{base_url}&q=title:test^2")
    assert res.status_code == 200

    # " — Lucene phrase query (unencoded double quote)
    res = client.get(f'{base_url}&q=title:"exact%20phrase"')
    assert res.status_code == 200

    # || — Lucene OR operator
    res = client.get(f"{base_url}&q=(title:foo)||(title:bar)")
    assert res.status_code == 200

    # ' — apostrophe in text values (e.g. O'Brien)
    res = client.get(f"{base_url}&q=author:O'Brien")
    assert res.status_code == 200
