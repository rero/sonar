# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test Crossref schema."""

from sonar.heg.serializers.schemas.crossref import CrossrefSchema


def test_crossref_schema(app):
    """Test Crossref schema."""
    data = {
        "_id": "111",
        "title": ["Document title"],
        "abstract": "Abstract",
        "DOI": "10.1182/blood-2016-11-751065",
        "ISSN": ["123456"],
    }
    assert CrossrefSchema().dump(data) == {
        "abstracts": [{"language": "eng", "value": "Abstract"}],
        "documentType": "coar:c_6501",
        "identifiedBy": [
            {"type": "bf:Doi", "value": "111"},
            {"type": "bf:Issn", "value": "123456"},
        ],
        "language": [{"type": "bf:Language", "value": "eng"}],
        "title": [
            {
                "type": "bf:Title",
                "mainTitle": [{"value": "Document title", "language": "eng"}],
            }
        ],
    }

    # Without abstract
    assert CrossrefSchema().dump({"_id": "111"}) == {
        "documentType": "coar:c_6501",
        "identifiedBy": [{"type": "bf:Doi", "value": "111"}],
        "language": [{"type": "bf:Language", "value": "eng"}],
    }

    # Subjects
    assert CrossrefSchema().dump({"_id": "111", "subject": ["Subject 1", "Subject 2"]})["subjects"] == [
        {"label": {"language": "eng", "value": ["Subject 1"]}},
        {"label": {"language": "eng", "value": ["Subject 2"]}},
    ]

    # Contributor
    assert CrossrefSchema().dump(
        {
            "_id": "111",
            "author": [
                {
                    "given": "John",
                    "family": "Doe",
                    "affiliation": [{"name": "RERO"}, {"name": "Reference aff."}],
                    "ORCID": "http://orcid.org/0000-0003-4197-8913",
                },
                {},
            ],
        }
    )["contribution"] == [
        {
            "affiliation": "Reference aff.",
            "agent": {
                "identifiedBy": {
                    "source": "ORCID",
                    "type": "bf:Local",
                    "value": "0000-0003-4197-8913",
                },
                "preferred_name": "Doe, John",
                "type": "bf:Person",
            },
            "role": ["cre"],
        }
    ]

    # Provision activity
    assert CrossrefSchema().dump({"_id": "111", "published-online": {"date-parts": [[2020, 4, 12]]}})[
        "provisionActivity"
    ] == [
        {
            "startDate": "2020",
            "statement": [{"label": [{"value": "2020-4-12"}], "type": "Date"}],
            "type": "bf:Publication",
        }
    ]

    # Part of
    assert CrossrefSchema().dump(
        {
            "_id": "111",
            "container-title": ["Host document title"],
            "volume": "Volume",
            "page": "Page",
            "journal-issue": {"issue": "Issue"},
            "issn-type": [
                {"value": "0301-1526", "type": "print"},
                {"value": "1664-2872", "type": "electronic"},
            ],
            "issued": {"date-parts": [[2018, 1, 24]]},
            "publisher": "Publisher",
        }
    )["partOf"] == [
        {
            "document": {
                "publication": {"startDate": "2018-1-24", "statement": "Publisher"},
                "title": "Host document title",
                "identifiedBy": [{"type": "bf:Issn", "value": "1664-2872"}],
            },
            "numberingIssue": "Issue",
            "numberingPages": "Page",
            "numberingVolume": "Volume",
            "numberingYear": "2018",
        }
    ]
