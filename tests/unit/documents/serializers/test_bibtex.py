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


def test_bibtex_coar_mapping_is_complete():
    """Every COAR documentType value has an explicit BibTeX entry type."""
    schema_path = Path(sonar.__file__).parent / "jsonschemas" / "common" / "type-v1.0.0.json"
    coar_types = set(json.loads(schema_path.read_text())["enum"])
    assert coar_types <= _COAR_TO_BIBTEX.keys()


def test_bibtex_coar_mapping_conference_and_bachelor():
    """Conference papers, proceedings and bachelor theses map to their dedicated entry types."""
    assert _COAR_TO_BIBTEX["coar:c_5794"] == "inproceedings"
    assert _COAR_TO_BIBTEX["coar:c_f744"] == "proceedings"
    assert _COAR_TO_BIBTEX["coar:c_7a1f"] == "mastersthesis"


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


def test_bibtex_serialize_search_deduplicates_cite_keys():
    """Two records with the same author surname and year get distinct cite keys."""
    metadata1 = {
        "contribution": [{"agent": {"type": "bf:Person", "preferred_name": "Smith, John"}, "role": ["cre"]}],
        "provisionActivity": [{"type": "bf:Publication", "startDate": "2020", "statement": []}],
    }
    metadata2 = {
        "contribution": [{"agent": {"type": "bf:Person", "preferred_name": "Smith, Jane"}, "role": ["cre"]}],
        "provisionActivity": [{"type": "bf:Publication", "startDate": "2020", "statement": []}],
    }
    search_result = {"hits": {"hits": [{"_source": {"metadata": metadata1}}, {"_source": {"metadata": metadata2}}]}}
    result = BibTeXSerializer().serialize_search(None, search_result)
    assert "@misc{Smith2020," in result
    assert "@misc{Smith2020a," in result


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
