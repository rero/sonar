# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test shared metadata extraction helpers for citation serializers."""

from sonar.modules.documents.serializers.common import (
    extract_abstract,
    extract_authors,
    extract_dissertation,
    extract_editors,
    extract_identifiers,
    extract_journal_info,
    extract_publication_info,
    extract_title,
    extract_url,
    extract_year,
    unwrap_metadata,
)


def test_extract_authors():
    """Only contributors with the "cre" role and a preferred name are returned."""
    metadata = {
        "contribution": [
            {"agent": {"preferred_name": "Doe, John"}, "role": ["cre"]},
            {"agent": {"preferred_name": "Smith, Jane"}, "role": ["cre", "edt"]},
            {"agent": {"preferred_name": "Editor, Ed"}, "role": ["edt"]},
            {"agent": {}, "role": ["cre"]},
        ]
    }
    assert extract_authors(metadata) == ["Doe, John", "Smith, Jane"]


def test_extract_authors_empty():
    """No contribution field returns an empty list."""
    assert extract_authors({}) == []


def test_extract_authors_excludes_meetings():
    """A bf:Meeting agent is never returned as an author."""
    metadata = {
        "contribution": [
            {"agent": {"type": "bf:Meeting", "preferred_name": "Some Conference"}, "role": ["cre"]},
            {"agent": {"type": "bf:Person", "preferred_name": "Doe, John"}, "role": ["cre"]},
        ]
    }
    assert extract_authors(metadata) == ["Doe, John"]


def test_extract_editors():
    """Only contributors with the "edt" role and a preferred name are returned."""
    metadata = {
        "contribution": [
            {"agent": {"preferred_name": "Doe, John"}, "role": ["cre"]},
            {"agent": {"preferred_name": "Editor, Ed"}, "role": ["edt"]},
        ]
    }
    assert extract_editors(metadata) == ["Editor, Ed"]


def test_extract_editors_empty():
    """No contribution field returns an empty list."""
    assert extract_editors({}) == []


def test_extract_editors_excludes_meetings():
    """A bf:Meeting agent is never returned as an editor."""
    metadata = {
        "contribution": [
            {"agent": {"type": "bf:Meeting", "preferred_name": "Some Conference"}, "role": ["edt"]},
            {"agent": {"type": "bf:Person", "preferred_name": "Editor, Ed"}, "role": ["edt"]},
        ]
    }
    assert extract_editors(metadata) == ["Editor, Ed"]


def test_extract_title_with_subtitle():
    """Title and subtitle are combined with a colon."""
    metadata = {
        "title": [
            {
                "mainTitle": [{"value": "Main title"}],
                "subtitle": [{"value": "Sub title"}],
            }
        ]
    }
    assert extract_title(metadata) == "Main title: Sub title"


def test_extract_title_without_subtitle():
    """Title alone is returned unchanged when there is no subtitle."""
    metadata = {"title": [{"mainTitle": [{"value": "Main title"}]}]}
    assert extract_title(metadata) == "Main title"


def test_extract_title_missing():
    """No title field returns None."""
    assert extract_title({}) is None


def test_extract_publication_info():
    """Year, place and publisher are extracted from the "bf:Publication" activity."""
    metadata = {
        "provisionActivity": [
            {
                "type": "bf:Publication",
                "startDate": "2020-05-01",
                "statement": [
                    {"type": "bf:Place", "label": [{"value": "Geneva"}]},
                    {"type": "bf:Agent", "label": {"value": "Pub Inc"}},
                ],
            }
        ]
    }
    assert extract_publication_info(metadata) == ("2020", "Geneva", "Pub Inc")


def test_extract_publication_info_ignores_other_activity_types():
    """Activities that are not "bf:Publication" are skipped."""
    metadata = {"provisionActivity": [{"type": "bf:Manufacture", "startDate": "2020-01-01"}]}
    assert extract_publication_info(metadata) == (None, None, None)


def test_extract_publication_info_missing():
    """No provisionActivity field returns a tuple of None."""
    assert extract_publication_info({}) == (None, None, None)


def test_extract_journal_info():
    """Journal, volume, issue and pages are extracted from the first partOf entry."""
    metadata = {
        "partOf": [
            {
                "document": {"title": "Journal X"},
                "numberingVolume": "3",
                "numberingIssue": "2",
                "numberingPages": "10-20",
            }
        ]
    }
    assert extract_journal_info(metadata) == ("Journal X", "3", "2", "10-20")


def test_extract_journal_info_missing():
    """No partOf field returns a tuple of None."""
    assert extract_journal_info({}) == (None, None, None, None)


def test_extract_abstract():
    """The first non-empty abstract value is returned."""
    metadata = {"abstracts": [{"value": ""}, {"value": "Real abstract"}, {"value": "Second abstract"}]}
    assert extract_abstract(metadata) == "Real abstract"


def test_extract_abstract_missing():
    """No abstracts field returns None."""
    assert extract_abstract({}) is None


def test_extract_year_from_publication_activity():
    """The year is taken from the "bf:Publication" activity when present."""
    metadata = {"provisionActivity": [{"type": "bf:Publication", "startDate": "2020-05-01", "statement": []}]}
    assert extract_year(metadata) == "2020"


def test_extract_year_falls_back_to_part_of():
    """The year falls back to the host document's numbering year."""
    metadata = {"partOf": [{"numberingYear": "2019"}]}
    assert extract_year(metadata) == "2019"


def test_extract_year_missing():
    """No provisionActivity nor partOf field returns None."""
    assert extract_year({}) is None


def test_extract_dissertation():
    """Degree, granting institution and jury note are extracted from the dissertation field."""
    metadata = {
        "dissertation": {
            "degree": "PhD",
            "grantingInstitution": "University of Example",
            "jury_note": "Passed with honors",
        }
    }
    assert extract_dissertation(metadata) == ("PhD", "University of Example", "Passed with honors")


def test_extract_dissertation_missing():
    """No dissertation field returns a tuple of None."""
    assert extract_dissertation({}) == (None, None, None)


def test_extract_identifiers_top_level():
    """DOI, ISBN and ISSN are extracted from the top-level identifiedBy."""
    metadata = {
        "identifiedBy": [
            {"type": "bf:Doi", "value": "10.1000/abc"},
            {"type": "bf:Isbn", "value": "978-3-16-148410-0"},
            {"type": "bf:Issn", "value": "1234-5678"},
        ]
    }
    assert extract_identifiers(metadata) == ("10.1000/abc", "978-3-16-148410-0", "1234-5678")


def test_extract_identifiers_falls_back_to_part_of():
    """The host document's ISSN is used when there is none at the top level."""
    metadata = {"partOf": [{"document": {"identifiedBy": [{"type": "bf:Issn", "value": "1234-5678"}]}}]}
    assert extract_identifiers(metadata) == (None, None, "1234-5678")


def test_extract_identifiers_top_level_wins_over_part_of():
    """A top-level identifier takes precedence over the host document's."""
    metadata = {
        "identifiedBy": [{"type": "bf:Issn", "value": "1111-1111"}],
        "partOf": [{"document": {"identifiedBy": [{"type": "bf:Issn", "value": "2222-2222"}]}}],
    }
    assert extract_identifiers(metadata) == (None, None, "1111-1111")


def test_extract_identifiers_missing():
    """No identifiedBy nor partOf field returns a tuple of None."""
    assert extract_identifiers({}) == (None, None, None)


def test_extract_url_uses_permalink_when_present():
    """The permalink already computed on a search hit is used as-is."""
    metadata = {"permalink": "https://sonar.example/documents/123"}
    assert extract_url(metadata) == "https://sonar.example/documents/123"


def test_extract_url_missing():
    """No permalink nor pid field returns None."""
    assert extract_url({}) is None


def test_unwrap_metadata_no_envelope():
    """A plain metadata dict with no "metadata" key is returned unchanged."""
    metadata = {"title": [{"mainTitle": [{"value": "Title"}]}]}
    assert unwrap_metadata(metadata) is metadata


def test_unwrap_metadata_preserves_sibling_pid_and_permalink():
    """Pid/permalink siblings of "metadata" are merged in, not dropped."""
    record = {
        "metadata": {"title": [{"mainTitle": [{"value": "Title"}]}]},
        "pid": "123",
        "permalink": "https://sonar.example/documents/123",
    }
    result = unwrap_metadata(record)
    assert result["pid"] == "123"
    assert result["permalink"] == "https://sonar.example/documents/123"
    assert result["title"] == record["metadata"]["title"]


def test_unwrap_metadata_metadata_pid_wins_over_sibling():
    """A "pid"/"permalink" already inside "metadata" is not overwritten."""
    record = {
        "metadata": {"pid": "inner", "permalink": "https://sonar.example/inner"},
        "pid": "outer",
        "permalink": "https://sonar.example/outer",
    }
    result = unwrap_metadata(record)
    assert result["pid"] == "inner"
    assert result["permalink"] == "https://sonar.example/inner"
