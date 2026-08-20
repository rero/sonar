# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test RIS serializer."""

import json
from pathlib import Path

import sonar
from sonar.modules.documents.serializers.ris import _COAR_TO_RIS, RISSerializer, serialize_record_to_ris


def test_ris_coar_mapping_is_complete():
    """Every COAR documentType value has an explicit RIS type tag."""
    schema_path = Path(sonar.__file__).parent / "jsonschemas" / "common" / "type-v1.0.0.json"
    coar_types = set(json.loads(schema_path.read_text())["enum"])
    assert coar_types <= _COAR_TO_RIS.keys()


def test_ris_coar_mapping_conference_papers():
    """Conference papers and proceedings map to CONF, not JOUR or BOOK."""
    assert _COAR_TO_RIS["coar:c_5794"] == "CONF"
    assert _COAR_TO_RIS["coar:c_f744"] == "CONF"


def test_ris_issn_identifier():
    """ISSN identifiers are exported the same way as ISBN."""
    metadata = {"identifiedBy": [{"type": "bf:Issn", "value": "1234-5678"}]}
    assert "SN  - 1234-5678" in serialize_record_to_ris(metadata)


def test_ris_serialize_search_unwraps_metadata():
    """serialize_search unwraps the record envelope like serialize does."""
    metadata = {"identifiedBy": [{"type": "bf:Issn", "value": "1234-5678"}]}
    search_result = {"hits": {"hits": [{"_source": {"metadata": metadata}}]}}
    result = RISSerializer().serialize_search(None, search_result)
    assert "SN  - 1234-5678" in result


def test_ris_abstract_with_embedded_newlines():
    """Newlines inside a field value do not produce malformed RIS lines."""
    metadata = {"abstracts": [{"language": "eng", "value": "Line one\nLine two\r\nLine three"}]}
    result = serialize_record_to_ris(metadata)
    assert "AB  - Line one Line two Line three" in result
    assert "\nLine two" not in result


def test_ris_book_chapter_uses_secondary_title():
    """A book chapter's host document is exported as T2, not JO."""
    metadata = {
        "documentType": "coar:c_3248",
        "partOf": [{"document": {"title": "Host Book"}}],
    }
    result = serialize_record_to_ris(metadata)
    assert "T2  - Host Book" in result
    assert "JO  - " not in result


def test_ris_article_uses_journal_tag():
    """A journal article's host document is exported as JO."""
    metadata = {
        "documentType": "coar:c_3e5a",
        "partOf": [{"document": {"title": "Host Journal"}}],
    }
    result = serialize_record_to_ris(metadata)
    assert "JO  - Host Journal" in result
    assert "T2  - " not in result


def test_ris_thesis_institution_and_degree():
    """A thesis exports its granting institution as PB and degree as M3."""
    metadata = {
        "documentType": "coar:c_46ec",
        "dissertation": {"grantingInstitution": "University of Example", "degree": "PhD"},
    }
    result = serialize_record_to_ris(metadata)
    assert "PB  - University of Example" in result
    assert "M3  - PhD" in result


def test_ris_thesis_institution_overrides_publisher_but_keeps_place():
    """A thesis's granting institution takes the PB slot, its own place is kept."""
    metadata = {
        "documentType": "coar:c_7a1f",
        "provisionActivity": [
            {
                "type": "bf:Publication",
                "startDate": "2017",
                "statement": [
                    {"type": "bf:Place", "label": [{"value": "Experimenton"}]},
                    {"type": "bf:Agent", "label": [{"value": "Mirage Editions"}]},
                ],
            }
        ],
        "dissertation": {"grantingInstitution": "École des hautes études partagées", "degree": "Travail de bachelor"},
    }
    result = serialize_record_to_ris(metadata)
    assert "PB  - École des hautes études partagées" in result
    assert "CY  - Experimenton" in result
    assert "Mirage Editions" not in result


def test_ris_thesis_publisher_used_without_granting_institution():
    """A thesis with no granting institution keeps its own publisher as PB."""
    metadata = {
        "documentType": "coar:c_db06",
        "provisionActivity": [
            {
                "type": "bf:Publication",
                "statement": [{"type": "bf:Agent", "label": [{"value": "Université de l'Exemple"}]}],
            }
        ],
    }
    assert "PB  - Université de l'Exemple" in serialize_record_to_ris(metadata)


def test_ris_hosted_item_keeps_its_own_place_and_publisher():
    """A hosted item keeps its own place/publisher, which the host does not provide."""
    metadata = {
        "documentType": "coar:c_6501",
        "provisionActivity": [
            {
                "type": "bf:Publication",
                "startDate": "2021",
                "statement": [
                    {"type": "bf:Place", "label": [{"value": "Hypothetica"}]},
                    {"type": "bf:Agent", "label": [{"value": "Conceptual Press"}]},
                ],
            }
        ],
        "partOf": [{"document": {"title": "Transactions on Conceptual Systems"}, "numberingYear": "2007"}],
    }
    result = serialize_record_to_ris(metadata)
    assert "CY  - Hypothetica" in result
    assert "PB  - Conceptual Press" in result
    assert "JO  - Transactions on Conceptual Systems" in result


def test_ris_host_publication_statement_fills_publisher_and_place():
    """A chapter's PB/CY come from the host publication statement."""
    metadata = {
        "documentType": "coar:c_3248",
        "provisionActivity": [
            {
                "type": "bf:Publication",
                "startDate": "2016",
                "statement": [{"type": "bf:Agent", "label": [{"value": "Imported Press"}]}],
            }
        ],
        "partOf": [{"document": {"title": "Le livre hôte", "publication": {"statement": "Paris : PUF, 2016"}}}],
    }
    result = serialize_record_to_ris(metadata)
    assert "CY  - Paris" in result
    assert "PB  - PUF" in result
    assert "Imported Press" not in result


def test_ris_host_statement_without_place_keeps_the_record_place():
    """A host statement stating only its publisher leaves the record's own CY in place."""
    metadata = {
        "documentType": "coar:c_3248",
        "provisionActivity": [
            {
                "type": "bf:Publication",
                "startDate": "2016",
                "statement": [
                    {"type": "bf:Place", "label": [{"value": "Genève"}]},
                    {"type": "bf:Agent", "label": [{"value": "Droz"}]},
                ],
            }
        ],
        "partOf": [{"document": {"title": "Le livre hôte", "publication": {"statement": "PUF"}}}],
    }
    result = serialize_record_to_ris(metadata)
    assert "CY  - Genève" in result
    assert "PB  - PUF" in result


def test_ris_series_entry_does_not_replace_own_publisher():
    """A monograph in a series keeps its own place/publisher, as a series carries no statement."""
    metadata = {
        "documentType": "coar:c_2f33",
        "provisionActivity": [
            {
                "type": "bf:Publication",
                "startDate": "2019",
                "statement": [
                    {"type": "bf:Place", "label": [{"value": "Bern"}]},
                    {"type": "bf:Agent", "label": [{"value": "Peter Lang"}]},
                ],
            }
        ],
        "partOf": [{"document": {"title": "Studien zur Germanistik"}, "numberingVolume": "12"}],
    }
    result = serialize_record_to_ris(metadata)
    assert "CY  - Bern" in result
    assert "PB  - Peter Lang" in result


def test_ris_other_identifiers_are_exported_as_notes():
    """Identifiers with no dedicated RIS tag (ark, URN...) are kept as notes, not dropped."""
    metadata = {
        "identifiedBy": [
            {"type": "ark", "value": "ark-000279"},
            {"type": "ark", "value": "ark:/99999/ffk3312"},
            {"type": "bf:Urn", "value": "Urn-000307"},
        ]
    }
    result = serialize_record_to_ris(metadata)
    assert "N1  - ARK: ark-000279" in result
    assert "N1  - ARK: ark:/99999/ffk3312" in result
    assert "N1  - URN: Urn-000307" in result


def test_ris_pages_with_double_dash():
    """A page range using a double dash is still parsed correctly."""
    metadata = {"partOf": [{"numberingPages": "135--142"}]}
    result = serialize_record_to_ris(metadata)
    assert "SP  - 135" in result
    assert "EP  - 142" in result


def test_ris_pages_open_ended():
    """A single page number does not produce an EP line."""
    metadata = {"partOf": [{"numberingPages": "135-"}]}
    result = serialize_record_to_ris(metadata)
    assert "SP  - 135" in result
    assert "EP  - " not in result


def test_ris_year_falls_back_to_part_of():
    """The year falls back to the host document's numbering year."""
    metadata = {"partOf": [{"numberingYear": "2019"}]}
    assert "PY  - 2019" in serialize_record_to_ris(metadata)


def test_ris_multiple_languages():
    """Every language with a value is exported, not only the first one."""
    metadata = {"language": [{"value": "eng"}, {"value": "fre"}]}
    result = serialize_record_to_ris(metadata)
    assert "LA  - eng" in result
    assert "LA  - fre" in result


def test_ris_excludes_meeting_authors():
    """A bf:Meeting agent is never exported as an author."""
    metadata = {
        "contribution": [{"agent": {"type": "bf:Meeting", "preferred_name": "Some Conference"}, "role": ["cre"]}]
    }
    assert "AU  - " not in serialize_record_to_ris(metadata)


def test_ris_serialize_search_unwraps_sibling_permalink():
    """A permalink sibling to "metadata" (not nested inside it) is not dropped."""
    search_result = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "metadata": {"identifiedBy": [{"type": "bf:Issn", "value": "1234-5678"}]},
                        "permalink": "https://sonar.example/documents/abc",
                    }
                }
            ]
        }
    }
    result = RISSerializer().serialize_search(None, search_result)
    assert "UR  - https://sonar.example/documents/abc" in result
