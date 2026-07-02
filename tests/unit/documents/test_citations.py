# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Unit tests for citation formatting."""

import pytest

from sonar.modules.documents.citations import citation_registry

ARTICLE = {
    "title": [{"type": "bf:Title", "mainTitle": [{"language": "eng", "value": "The Art of Testing"}]}],
    "contribution": [
        {"agent": {"type": "bf:Person", "preferred_name": "Smith, John"}, "role": ["cre"]},
        {"agent": {"type": "bf:Person", "preferred_name": "Doe, Jane"}, "role": ["cre"]},
    ],
    "provisionActivity": [
        {
            "type": "bf:Publication",
            "startDate": "2023",
            "statement": [
                {"type": "bf:Place", "label": [{"value": "London"}]},
                {"type": "bf:Agent", "label": [{"value": "Academic Press"}]},
            ],
        }
    ],
    "partOf": [
        {
            "document": {"title": "Journal of Research"},
            "numberingVolume": "10",
            "numberingIssue": "2",
            "numberingPages": "45-67",
        }
    ],
    "identifiedBy": [{"type": "bf:Doi", "value": "10.1000/xyz123"}],
}

BOOK = {
    "title": [
        {
            "type": "bf:Title",
            "mainTitle": [{"language": "eng", "value": "Deep Learning"}],
            "subtitle": [{"language": "eng", "value": "A Practical Approach"}],
        }
    ],
    "contribution": [
        {"agent": {"type": "bf:Person", "preferred_name": "Lecun, Yann"}, "role": ["cre"]},
    ],
    "provisionActivity": [
        {
            "type": "bf:Publication",
            "startDate": "2021",
            "statement": [
                {"type": "bf:Place", "label": [{"value": "New York"}]},
                {"type": "bf:Agent", "label": [{"value": "MIT Press"}]},
            ],
        }
    ],
}

EDITOR_ONLY = {
    "title": [{"type": "bf:Title", "mainTitle": [{"language": "eng", "value": "Collected Essays"}]}],
    "contribution": [
        {"agent": {"type": "bf:Person", "preferred_name": "Brown, Alice"}, "role": ["edt"]},
        {"agent": {"type": "bf:Person", "preferred_name": "Green, Bob"}, "role": ["edt"]},
    ],
    "provisionActivity": [
        {
            "type": "bf:Publication",
            "startDate": "2020",
            "statement": [
                {"type": "bf:Place", "label": [{"value": "Oxford"}]},
                {"type": "bf:Agent", "label": [{"value": "Oxford UP"}]},
            ],
        }
    ],
}

MULTILANG = {
    "title": [
        {
            "type": "bf:Title",
            "mainTitle": [
                {"language": "fre", "value": "La science des données"},
                {"language": "eng", "value": "Data Science"},
            ],
        }
    ],
    "contribution": [
        {"agent": {"type": "bf:Person", "preferred_name": "Martin, Pierre"}, "role": ["cre"]},
    ],
    "provisionActivity": [
        {
            "type": "bf:Publication",
            "startDate": "2022",
            "statement": [{"type": "bf:Agent", "label": [{"value": "Dunod"}]}],
        }
    ],
}


def test_unsupported_style():
    """Unsupported style raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported citation style"):
        citation_registry.format(ARTICLE, "bibtex")


# --- APA ---


def test_apa_article():
    """APA journal article citation."""
    result = citation_registry.format(ARTICLE, "apa_7")
    assert "Smith, John" in result
    assert "Doe, Jane" in result
    assert "(2023)" in result
    assert "The Art of Testing" in result
    assert "*Journal of Research*" in result
    assert "10(2)" in result
    assert "45-67" in result
    assert "https://doi.org/10.1000/xyz123" in result


def test_apa_book():
    """APA book citation with subtitle."""
    result = citation_registry.format(BOOK, "apa_7")
    assert "Lecun, Yann" in result
    assert "(2021)" in result
    assert "Deep Learning: A Practical Approach" in result
    assert "MIT Press" in result


def test_apa_editors():
    """APA falls back to editors with (Eds.) suffix."""
    result = citation_registry.format(EDITOR_ONLY, "apa_7")
    assert "Brown, Alice" in result
    assert "(Eds.)" in result


# --- Chicago ---


def test_chicago_article():
    """Chicago journal article citation."""
    result = citation_registry.format(ARTICLE, "chicago_17")
    assert "Smith, John" in result
    assert "2023" in result
    assert '"The Art of Testing."' in result
    assert "*Journal of Research*" in result
    assert "45-67" in result


def test_chicago_book():
    """Chicago book citation."""
    result = citation_registry.format(BOOK, "chicago_17")
    assert "*Deep Learning: A Practical Approach*" in result
    assert "Lecun, Yann" in result
    assert "New York" in result
    assert "MIT Press" in result


def test_chicago_editors():
    """Chicago falls back to editors with eds. suffix."""
    result = citation_registry.format(EDITOR_ONLY, "chicago_17")
    assert "Brown, Alice" in result
    assert "eds." in result


# --- MLA ---


def test_mla_article():
    """MLA journal article citation."""
    result = citation_registry.format(ARTICLE, "mla_9")
    assert "Smith, John" in result
    assert '"The Art of Testing."' in result
    assert "*Journal of Research*" in result
    assert "pp. 45-67" in result
    assert "2023" in result


def test_mla_three_authors_et_al():
    """MLA uses et al. for 3+ authors."""
    record = {
        **ARTICLE,
        "contribution": [
            {"agent": {"type": "bf:Person", "preferred_name": "A, One"}, "role": ["cre"]},
            {"agent": {"type": "bf:Person", "preferred_name": "B, Two"}, "role": ["cre"]},
            {"agent": {"type": "bf:Person", "preferred_name": "C, Three"}, "role": ["cre"]},
        ],
    }
    result = citation_registry.format(record, "mla_9")
    assert "et al." in result


def test_mla_book():
    """MLA book citation."""
    result = citation_registry.format(BOOK, "mla_9")
    assert "*Deep Learning: A Practical Approach*" in result
    assert "MIT Press" in result


# --- Harvard ---


def test_harvard_article():
    """Harvard journal article citation."""
    result = citation_registry.format(ARTICLE, "harvard_12")
    assert "Smith, John" in result
    assert "(2023)" in result
    assert "'The Art of Testing'" in result
    assert "*Journal of Research*" in result
    assert "pp. 45-67" in result


def test_harvard_book():
    """Harvard book citation."""
    result = citation_registry.format(BOOK, "harvard_12")
    assert "Lecun, Yann" in result
    assert "(2021)" in result
    assert "*Deep Learning: A Practical Approach*" in result
    assert "New York: MIT Press" in result


def test_harvard_editors():
    """Harvard falls back to editors with (eds.) suffix."""
    result = citation_registry.format(EDITOR_ONLY, "harvard_12")
    assert "Brown, Alice" in result
    assert "(eds.)" in result


# --- Language selection ---


def test_lang_param_selects_title():
    """Lang param selects the matching mainTitle."""
    assert "La science des données" in citation_registry.format(MULTILANG, "apa_7", lang="fre")
    assert "Data Science" in citation_registry.format(MULTILANG, "apa_7", lang="eng")


def test_lang_param_fallback_to_first():
    """Unknown lang falls back to first mainTitle."""
    result = citation_registry.format(MULTILANG, "apa_7", lang="deu")
    assert "La science des données" in result


# --- Edge cases ---


def test_no_authors():
    """Record with no contribution produces a citation without author."""
    record = {**BOOK, "contribution": []}
    result = citation_registry.format(record, "apa_7")
    assert "Deep Learning" in result


def test_no_publication_date():
    """Missing publication date uses n.d."""
    record = {**BOOK, "provisionActivity": []}
    result = citation_registry.format(record, "apa_7")
    assert "(n.d.)" in result
