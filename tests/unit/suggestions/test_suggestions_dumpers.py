# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test suggestions dumpers."""

from sonar.suggestions.dumpers import SuggestionsDumperExt


def test_extract_values():
    """Test collecting the values reachable through a field path."""
    data = {
        "contribution": [
            {"agent": {"preferred_name": "Dupont, Jean"}},
            {"agent": {"preferred_name": "Zimmermann, Ada"}},
            {"role": ["cre"]},
        ],
        "customField1": ["Test", "Other"],
        "isOpenAccess": True,
    }

    assert list(SuggestionsDumperExt._extract_values(data, ["contribution", "agent", "preferred_name"])) == [
        "Dupont, Jean",
        "Zimmermann, Ada",
    ]
    assert list(SuggestionsDumperExt._extract_values(data, ["customField1"])) == ["Test", "Other"]

    # Unknown path and non string value
    assert not list(SuggestionsDumperExt._extract_values(data, ["unknown"]))
    assert not list(SuggestionsDumperExt._extract_values(data, ["isOpenAccess"]))


def test_suggestions_dumper_ext():
    """Test dumping the suggestable values as nested objects."""
    data = {
        "contribution": [
            {"agent": {"preferred_name": "Dupont, Jean"}},
            {"agent": {"preferred_name": "Dupont, Jean"}},
        ],
        "customField1": ["Test"],
    }

    dumper = SuggestionsDumperExt(["contribution.agent.preferred_name", "customField1", "customField2"])
    dumper.dump(None, data)

    # One object per value, duplicates removed, declaration order kept
    assert data["suggestions"] == [
        {"field": "contribution.agent.preferred_name", "value": "Dupont, Jean"},
        {"field": "customField1", "value": "Test"},
    ]

    # The values are dropped again when the indexed data is loaded back
    dumper.load(data, None)
    assert "suggestions" not in data
