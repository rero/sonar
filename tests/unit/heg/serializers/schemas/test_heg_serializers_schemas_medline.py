# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test Medline schema."""

from sonar.heg.serializers.schemas.medline import MedlineSchema


def test_medline_schema(app):
    """Test Medline schema."""
    data = {
        "_id": "111",
        "title": "Document title",
        "abstract": "Abstract",
        "doi": "10.1182/blood-2016-11-751065",
        "pmid": "123456",
    }

    assert MedlineSchema().dump(data) == {
        "abstracts": [{"language": "eng", "value": "Abstract"}],
        "documentType": "coar:c_6501",
        "identifiedBy": [
            {"type": "bf:Doi", "value": "111"},
            {"type": "bf:Local", "source": "PMID", "value": "123456"},
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
    assert MedlineSchema().dump({"_id": "111"}) == {
        "documentType": "coar:c_6501",
        "identifiedBy": [{"type": "bf:Doi", "value": "111"}],
        "title": [
            {
                "mainTitle": [{"language": "eng", "value": "Unknown title"}],
                "type": "bf:Title",
            }
        ],
        "language": [{"type": "bf:Language", "value": "eng"}],
    }

    # Contribution
    assert MedlineSchema().dump({"_id": "111", "authors": ["John Doe"], "affiliations": ["RERO"]})["contribution"] == [
        {
            "affiliation": "RERO",
            "agent": {"preferred_name": "John Doe", "type": "bf:Person"},
            "role": ["cre"],
        }
    ]

    # Provision activity
    assert MedlineSchema().dump({"_id": "111", "pubyear": "2019", "entrez_date": "2019-03-03"})[
        "provisionActivity"
    ] == [
        {
            "startDate": "2019",
            "statement": [{"label": [{"value": "2019-03-03"}], "type": "Date"}],
            "type": "bf:Publication",
        }
    ]

    # Part of
    assert MedlineSchema().dump({"_id": "111", "pubyear": "2019", "journal": "Journal"})["partOf"] == [
        {"document": {"title": "Journal"}, "numberingYear": "2019"}
    ]

    # Subjects
    assert MedlineSchema().dump(
        {
            "_id": "111",
            "keywords": ["Keyword", "Keyword2"],
            "mesh_terms": ["D032921:Consensus", "D015921:Dental Implants"],
        }
    )["subjects"] == [
        {"label": {"language": "eng", "value": ["Keyword"]}},
        {"label": {"language": "eng", "value": ["Keyword2"]}},
        {"label": {"language": "eng", "value": ["Consensus"]}, "source": "MeSH"},
        {"label": {"language": "eng", "value": ["Dental Implants"]}, "source": "MeSH"},
    ]
