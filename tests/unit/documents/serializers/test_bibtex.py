# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test BibTeX serializer."""

import json
from pathlib import Path

import sonar
from sonar.modules.documents.serializers.bibtex import (
    _COAR_TO_BIBTEX,
    BibTeXSerializer,
    _bibtex_key,
    serialize_record_to_bibtex,
)
from sonar.modules.documents.serializers.common import THESIS_DOCUMENT_TYPES


def test_bibtex_coar_mapping_is_complete():
    """Every COAR documentType value has an explicit BibTeX entry type."""
    schema_path = Path(sonar.__file__).parent / "jsonschemas" / "common" / "type-v1.0.0.json"
    coar_types = set(json.loads(schema_path.read_text())["enum"])
    assert coar_types <= _COAR_TO_BIBTEX.keys()


def test_bibtex_coar_mapping_conference_types():
    """Conference papers and proceedings map to their dedicated entry types."""
    assert _COAR_TO_BIBTEX["coar:c_5794"] == "inproceedings"
    assert _COAR_TO_BIBTEX["coar:c_f744"] == "proceedings"


def test_bibtex_coar_mapping_thesis_entry_types():
    """Only a doctoral thesis is a phdthesis; every other level rides on mastersthesis."""
    assert _COAR_TO_BIBTEX["coar:c_db06"] == "phdthesis"
    assert {_COAR_TO_BIBTEX[doc_type] for doc_type in THESIS_DOCUMENT_TYPES - {"coar:c_db06"}} == {"mastersthesis"}


def test_bibtex_key_multi_word_last_name():
    """A multi-word last name does not introduce whitespace in the cite key."""
    metadata = {
        "contribution": [{"agent": {"type": "bf:Person", "preferred_name": "van der Berg, Jan"}, "role": ["cre"]}],
        "provisionActivity": [{"type": "bf:Publication", "startDate": "2020", "statement": []}],
    }
    assert _bibtex_key(metadata) == "vanderBerg2020"


def test_bibtex_issn_identifier():
    """ISSN identifiers use the dedicated issn field."""
    metadata = {"identifiedBy": [{"type": "bf:Issn", "value": "1234-5678"}]}
    assert "issn         = {1234-5678}," in serialize_record_to_bibtex(metadata)


def test_bibtex_serialize_search_unwraps_metadata():
    """serialize_search unwraps the record envelope like serialize does."""
    metadata = {"identifiedBy": [{"type": "bf:Issn", "value": "1234-5678"}]}
    search_result = {"hits": {"hits": [{"_source": {"metadata": metadata}}]}}
    result = BibTeXSerializer().serialize_search(None, search_result)
    assert "issn         = {1234-5678}," in result


def test_bibtex_book_chapter_uses_booktitle():
    """A book chapter's host document is exported as booktitle, not journal."""
    metadata = {
        "documentType": "coar:c_3248",
        "partOf": [{"document": {"title": "Host Book"}}],
    }
    result = serialize_record_to_bibtex(metadata)
    assert "booktitle    = {Host Book}," in result
    assert "journal" not in result


def test_bibtex_article_uses_journal():
    """A journal article's host document is exported as journal."""
    metadata = {
        "documentType": "coar:c_3e5a",
        "partOf": [{"document": {"title": "Host Journal"}}],
    }
    result = serialize_record_to_bibtex(metadata)
    assert "journal      = {Host Journal}," in result
    assert "booktitle" not in result


def test_bibtex_thesis_school():
    """A thesis exports its granting institution as school."""
    metadata = {
        "documentType": "coar:c_46ec",
        "dissertation": {"grantingInstitution": "University of Example"},
    }
    assert "school       = {University of Example}," in serialize_record_to_bibtex(metadata)


def test_bibtex_thesis_degree_uses_type_field_regardless_of_entry_type():
    """A thesis states its degree via "type", as the entry type cannot tell a bachelor's from a PhD."""
    metadata = {
        "documentType": "coar:c_7a1f",
        "dissertation": {"grantingInstitution": "Example University", "degree": "Travail de bachelor"},
    }
    result = serialize_record_to_bibtex(metadata)
    assert result.startswith("@mastersthesis{")
    assert "type         = {Travail de bachelor}," in result


def test_bibtex_all_thesis_types_export_school_and_degree():
    """Every thesis document type exports its school and degree, whatever its entry type."""
    for doc_type in THESIS_DOCUMENT_TYPES:
        metadata = {
            "documentType": doc_type,
            "dissertation": {"grantingInstitution": "Example University", "degree": "Travail de bachelor"},
        }
        result = serialize_record_to_bibtex(metadata)
        assert "school       = {Example University}," in result
        assert "type         = {Travail de bachelor}," in result


def test_bibtex_thesis_institution_overrides_publisher_but_keeps_place():
    """A thesis's granting institution takes the publisher slot, its own place is kept."""
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
    result = serialize_record_to_bibtex(metadata)
    assert "school       = {École des hautes études partagées}," in result
    assert "address      = {Experimenton}," in result
    assert "publisher" not in result


def test_bibtex_thesis_school_falls_back_to_own_publisher():
    """A thesis with no granting institution fills its school with its own publisher."""
    metadata = {
        "documentType": "coar:c_db06",
        "provisionActivity": [
            {
                "type": "bf:Publication",
                "statement": [{"type": "bf:Agent", "label": [{"value": "Université de l'Exemple"}]}],
            }
        ],
    }
    result = serialize_record_to_bibtex(metadata)
    assert "school       = {Université de l'Exemple}," in result
    assert "publisher" not in result


def test_bibtex_hosted_item_keeps_its_own_place_and_publisher():
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
    result = serialize_record_to_bibtex(metadata)
    assert "address      = {Hypothetica}," in result
    assert "publisher    = {Conceptual Press}," in result
    assert "journal      = {Transactions on Conceptual Systems}," in result


def test_bibtex_host_publication_statement_fills_publisher_and_address():
    """A chapter's publisher/address come from the host publication statement."""
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
    result = serialize_record_to_bibtex(metadata)
    assert "address      = {Paris}," in result
    assert "publisher    = {PUF}," in result
    assert "Imported Press" not in result


def test_bibtex_host_statement_without_place_keeps_the_record_place():
    """A host statement stating only its publisher leaves the record's own address in place."""
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
    result = serialize_record_to_bibtex(metadata)
    assert "address      = {Genève}," in result
    assert "publisher    = {PUF}," in result


def test_bibtex_series_entry_does_not_replace_own_publisher():
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
    result = serialize_record_to_bibtex(metadata)
    assert "address      = {Bern}," in result
    assert "publisher    = {Peter Lang}," in result


def test_bibtex_other_identifiers_get_their_own_field():
    """Identifiers with no dedicated BibTeX field (ark, URN...) are kept, not dropped."""
    metadata = {"identifiedBy": [{"type": "bf:Urn", "value": "urn:nbn:ch:rero-006-3078"}]}
    assert "urn          = {urn:nbn:ch:rero-006-3078}," in serialize_record_to_bibtex(metadata)


def test_bibtex_duplicate_identifier_types_get_numbered_fields():
    """A type repeated between the record and its host document gets distinct field names, as BibTeX requires."""
    metadata = {
        "identifiedBy": [{"type": "bf:Local", "value": "LOCAL-1"}],
        "partOf": [{"document": {"identifiedBy": [{"type": "bf:Local", "value": "LOCAL-2"}]}}],
    }
    result = serialize_record_to_bibtex(metadata)
    assert "local        = {LOCAL-1}," in result
    assert "local2       = {LOCAL-2}," in result


def test_bibtex_escapes_special_characters():
    """LaTeX special characters are escaped in free-text fields."""
    metadata = {"title": [{"mainTitle": [{"value": "100% AT&T's Report_v2"}]}]}
    result = serialize_record_to_bibtex(metadata)
    assert r"100\% AT\&T's Report\_v2" in result


def test_bibtex_does_not_escape_identifiers_and_url():
    """DOI, ISBN, ISSN and URL fields are not LaTeX-escaped."""
    metadata = {
        "permalink": "https://sonar.example/documents/abc_def",
        "identifiedBy": [{"type": "bf:Doi", "value": "10.1000/abc_def"}],
    }
    result = serialize_record_to_bibtex(metadata)
    assert "doi          = {10.1000/abc_def}," in result
    assert "url          = {https://sonar.example/documents/abc_def}," in result


def test_bibtex_year_falls_back_to_part_of():
    """The year falls back to the host document's numbering year."""
    metadata = {"partOf": [{"numberingYear": "2019"}]}
    assert "year         = {2019}," in serialize_record_to_bibtex(metadata)


def test_bibtex_excludes_meeting_authors():
    """A bf:Meeting agent is never exported as an author."""
    metadata = {
        "contribution": [{"agent": {"type": "bf:Meeting", "preferred_name": "Some Conference"}, "role": ["cre"]}]
    }
    assert "author" not in serialize_record_to_bibtex(metadata)


def test_bibtex_escapes_backslash_in_single_pass():
    """A literal backslash is escaped without doubling the inserted braces."""
    metadata = {"title": [{"mainTitle": [{"value": "a\\b"}]}]}
    result = serialize_record_to_bibtex(metadata)
    assert r"a\textbackslash{}b" in result
    assert r"\{\}" not in result


def test_bibtex_key_uses_pid_for_uniqueness_across_independent_calls():
    """Cite keys stay unique across independent calls, which share no collision state."""
    metadata1 = {
        "pid": "161",
        "permalink": "https://sonar.example/documents/161",
        "contribution": [{"agent": {"type": "bf:Person", "preferred_name": "Huang, Mei"}, "role": ["cre"]}],
        "provisionActivity": [{"type": "bf:Publication", "startDate": "2024", "statement": []}],
    }
    metadata2 = {
        "pid": "75",
        "permalink": "https://sonar.example/documents/75",
        "contribution": [{"agent": {"type": "bf:Person", "preferred_name": "Huang, Wei"}, "role": ["cre"]}],
        "provisionActivity": [{"type": "bf:Publication", "startDate": "2024", "statement": []}],
    }
    # Each call is independent, exactly like two separate pages of a
    # paginated bulk export.
    result1 = serialize_record_to_bibtex(metadata1)
    result2 = serialize_record_to_bibtex(metadata2)
    assert "@misc{Huang2024-161," in result1
    assert "@misc{Huang2024-75," in result2


def test_bibtex_key_falls_back_to_editor_when_no_author():
    """The cite key uses the first editor's surname when there is no author."""
    metadata = {
        "contribution": [{"agent": {"type": "bf:Person", "preferred_name": "Bonnet, Lars"}, "role": ["edt"]}],
        "provisionActivity": [{"type": "bf:Publication", "startDate": "2021", "statement": []}],
    }
    assert _bibtex_key(metadata) == "Bonnet2021"


def test_bibtex_serialize_search_unwraps_sibling_permalink():
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
    result = BibTeXSerializer().serialize_search(None, search_result)
    assert "url          = {https://sonar.example/documents/abc}," in result
