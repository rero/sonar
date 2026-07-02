# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test shared metadata extraction helpers for citation serializers."""

from sonar.modules.documents.serializers.common import (
    extract_abstract,
    extract_authors,
    extract_editors,
    extract_journal_info,
    extract_publication_info,
    extract_title,
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
